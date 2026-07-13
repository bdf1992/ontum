-- ===== Hourglass — a tiered vessel of elemental grains =====
-- Top = grains in time; bottom = grains fallen into timelessness.
-- Timeless when more grains sit on the bottom than the top (bdo's rule).
-- The hourglass itself is a resource: its tier bounds total grains.
-- GM Notes JSON: {"tier":3, "top":{"Fire":5}, "bottom":{}}

{{FORGE:COMMON}}

local state = { tier = 1, sel = 2, top = {}, bottom = {} }

function onSave() return JSON.encode(state) end

function onLoad(saved)
  local restored = false
  if saved ~= nil and saved ~= "" then
    local ok, s = pcall(function() return JSON.decode(saved) end)
    if ok and type(s) == "table" and s.top ~= nil then
      state = s
      restored = true
    end
  end
  if not restored then
    local cfg = ccNotesConfig({ tier = 1, top = {}, bottom = {} })
    state.tier = tonumber(cfg.tier) or 1
    state.top = cfg.top or {}
    state.bottom = cfg.bottom or {}
    state.sel = state.sel or 2
  end
  ccEnsureTag("cc-holder")
  ccEnsureTag("cc-hourglass")
  buildUI()
  refresh()
end

local function selName() return CC.elements[state.sel].name end
local function used() return ccTotal(state.top) + ccTotal(state.bottom) end
local function isTimeless() return ccTotal(state.bottom) > ccTotal(state.top) end

function buildUI()
  self.clearButtons()
  ccBtn({ click_function = "ccNoop", label = "", position = { 0, 0.58, -0.30 },
          width = 0, height = 0, font_size = 130 })                       -- 0 headline
  ccBtn({ click_function = "hgPrev", label = "<", position = { -0.34, 0.58, 0 },
          width = 220, height = 220, font_size = 130 })                   -- 1
  ccBtn({ click_function = "ccNoop", label = "", position = { 0, 0.58, 0 },
          width = 0, height = 0, font_size = 130 })                       -- 2 element label
  ccBtn({ click_function = "hgNext", label = ">", position = { 0.34, 0.58, 0 },
          width = 220, height = 220, font_size = 130 })                   -- 3
  ccBtn({ click_function = "hgMinus", label = "-", position = { -0.34, 0.58, 0.30 },
          width = 220, height = 220, font_size = 140 })                   -- 4
  ccBtn({ click_function = "hgPlus", label = "+", position = { -0.12, 0.58, 0.30 },
          width = 220, height = 220, font_size = 140 })                   -- 5
  ccBtn({ click_function = "hgDrop", label = "v", position = { 0.12, 0.58, 0.30 },
          width = 220, height = 220, font_size = 130,
          tooltip = "Spend: one grain falls into timelessness" })         -- 6
  ccBtn({ click_function = "hgRaise", label = "^", position = { 0.34, 0.58, 0.30 },
          width = 220, height = 220, font_size = 130,
          tooltip = "Reclaim: one grain rises back into time" })          -- 7
end

function refresh()
  local cap = ccTier(state.tier).capacity
  local head = "T" .. state.tier .. "  " .. ccTotal(state.top) .. "^ "
      .. ccTotal(state.bottom) .. "v / " .. cap
  if isTimeless() then head = head .. "  TIMELESS" end
  local e = CC.elements[state.sel]
  self.editButton({ index = 0, label = head })
  self.editButton({ index = 2,
    label = e.name .. " " .. (state.top[e.name] or 0) .. "^" .. (state.bottom[e.name] or 0) .. "v",
    font_color = { e.color.r, e.color.g, e.color.b } })
  self.setName("Hourglass T" .. state.tier .. (isTimeless() and " (TIMELESS)" or ""))
  self.setDescription("Capacity " .. cap .. " grains | worth "
      .. ccTier(state.tier).timecoin .. " " .. CC.currency.name
      .. "\nTop (in time): " .. ccFmtPool(state.top)
      .. "\nBottom (timeless): " .. ccFmtPool(state.bottom))
  if isTimeless() then
    self.setColorTint({ 0.25, 0.20, 0.35 })
  else
    local t = state.tier
    self.setColorTint({ 0.55 + 0.08 * t, 0.50 + 0.06 * t, 0.35 })
  end
end

function ccNoop() end
function hgPrev() state.sel = (state.sel - 2) % #CC.elements + 1; refresh() end
function hgNext() state.sel = state.sel % #CC.elements + 1; refresh() end

function hgPlus()
  if used() >= ccTier(state.tier).capacity then
    broadcastToAll("Hourglass T" .. state.tier .. " is full ("
        .. ccTier(state.tier).capacity .. " grains) — a higher tier holds more.",
        { 0.9, 0.6, 0.2 })
    return
  end
  state.top[selName()] = (state.top[selName()] or 0) + 1
  refresh()
end

function hgMinus()
  local n = state.top[selName()] or 0
  if n > 0 then state.top[selName()] = n - 1 end
  refresh()
end

function hgDrop()
  local n = state.top[selName()] or 0
  if n > 0 then
    local was = isTimeless()
    state.top[selName()] = n - 1
    state.bottom[selName()] = (state.bottom[selName()] or 0) + 1
    if not was and isTimeless() then
      broadcastToAll(self.getName() .. " has slipped into TIMELESSNESS.", { 0.6, 0.4, 0.9 })
    end
  end
  refresh()
end

function hgRaise()
  local n = state.bottom[selName()] or 0
  if n > 0 then
    state.bottom[selName()] = n - 1
    state.top[selName()] = (state.top[selName()] or 0) + 1
  end
  refresh()
end

-- Census / automation seam: other objects read and feed this vessel.
function ccGetPool()
  return { kind = "hourglass", tier = state.tier, top = state.top,
           bottom = state.bottom, timeless = isTimeless() }
end

-- params: {element="Fire", n=1, side="top"|"bottom"}; refuses past capacity.
function ccAddGrain(params)
  local e = ccElem(params.element)
  if e == nil then return false end
  local n = tonumber(params.n) or 1
  local side = (params.side == "bottom") and "bottom" or "top"
  if used() + n > ccTier(state.tier).capacity then return false end
  state[side][e.name] = (state[side][e.name] or 0) + n
  refresh()
  return true
end
