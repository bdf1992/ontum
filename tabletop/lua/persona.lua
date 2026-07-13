-- ===== Persona pawn =====
-- A persona carries its own grains (top = in time, bottom = timeless) and
-- an identity that starts hidden: the fog of war shows rarity and available
-- grain only until someone IDENTIFYs it (race, class, wants/weak revealed).
-- Stand it on a biome tile and the census counts its grains toward that
-- region (Herald with 5 Fire on Region A makes the region 10 Fire).
-- GM Notes JSON: {"name":"Herald","race":"Primal","class":"Lord","tier":3,
--                 "pool":{"Fire":5},"identified":false}

{{FORGE:COMMON}}

local state = { name = "Persona", race = "Mortal", class = "Lord", tier = 1,
                identified = false, sel = 2, top = {}, bottom = {} }

local function findRow(rows, name)
  for _, r in ipairs(rows) do
    if string.lower(r.name) == string.lower(tostring(name)) then return r end
  end
  return rows[1]
end

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
    local cfg = ccNotesConfig({ name = "Persona", race = "Mortal", class = "Lord",
                                tier = 1, pool = {}, identified = false })
    state.name = tostring(cfg.name)
    state.race = findRow(CC.races, cfg.race).name
    state.class = findRow(CC.classes, cfg.class).name
    state.tier = tonumber(cfg.tier) or 1
    state.identified = cfg.identified == true
    state.top = cfg.pool or {}
    state.bottom = {}
  end
  ccEnsureTag("cc-holder")
  ccEnsureTag("cc-persona")
  buildUI()
  refresh()
end

local function selName() return CC.elements[state.sel].name end
local function isTimeless() return ccTotal(state.bottom) > ccTotal(state.top) end
-- a persona's own hourglass: its tier bounds its total grains, like any vessel
local function used() return ccTotal(state.top) + ccTotal(state.bottom) end
local function full()
  if used() >= ccTier(state.tier).capacity then
    broadcastToAll(self.getName() .. "'s hourglass is full ("
        .. ccTier(state.tier).capacity .. " grains at Tier " .. state.tier .. ").",
        { 0.9, 0.6, 0.2 })
    return true
  end
  return false
end

function buildUI()
  self.clearButtons()
  ccBtn({ click_function = "ccNoop", label = "", position = { 0, 0.3, -0.9 },
          width = 0, height = 0, font_size = 120 })                        -- 0 headline
  ccBtn({ click_function = "pIdentify", label = "ID?", position = { 0, 0.3, 0.9 },
          width = 340, height = 260, font_size = 110,
          tooltip = "Identify: reveal race, class and hidden variables" })  -- 1
  ccBtn({ click_function = "pPrev", label = "<", position = { -0.75, 0.3, 0 },
          width = 200, height = 200, font_size = 110 })                     -- 2
  ccBtn({ click_function = "pNext", label = ">", position = { 0.75, 0.3, 0 },
          width = 200, height = 200, font_size = 110 })                     -- 3
  ccBtn({ click_function = "pMinus", label = "-", position = { -0.45, 0.3, 0.55 },
          width = 200, height = 200, font_size = 120 })                     -- 4
  ccBtn({ click_function = "pPlus", label = "+", position = { -0.15, 0.3, 0.55 },
          width = 200, height = 200, font_size = 120 })                     -- 5
  ccBtn({ click_function = "pDrop", label = "v", position = { 0.15, 0.3, 0.55 },
          width = 200, height = 200, font_size = 110,
          tooltip = "Spend a grain into timelessness" })                    -- 6
  ccBtn({ click_function = "pRaise", label = "^", position = { 0.45, 0.3, 0.55 },
          width = 200, height = 200, font_size = 110 })                     -- 7
end

function refresh()
  local race = findRow(CC.races, state.race)
  local cls = findRow(CC.classes, state.class)
  local shown = state.identified
      and (state.name .. " T" .. state.tier)
      or ("Unknown T" .. state.tier)
  self.editButton({ index = 0,
    label = shown .. "  " .. ccTotal(state.top) .. "^ " .. ccTotal(state.bottom) .. "v"
      .. (isTimeless() and " TIMELESS" or "") })
  self.editButton({ index = 1, label = state.identified and "ID:OK" or "ID?" })
  self.setName(shown)
  if state.identified then
    self.setDescription(state.name .. " — " .. state.race .. " " .. state.class
        .. " (Tier " .. state.tier .. ")"
        .. "\nIS " .. race.is .. "/" .. cls.is
        .. " | WANTS " .. race.wants .. "/" .. cls.wants
        .. " | WEAK " .. race.weak .. "/" .. cls.weak
        .. "\nAbility: " .. (cls.ability or "?")
        .. "\nGrains in time: " .. ccFmtPool(state.top)
        .. "\nGrains timeless: " .. ccFmtPool(state.bottom))
    local e = ccElem(race.is)
    if e ~= nil then self.setColorTint({ e.color.r, e.color.g, e.color.b }) end
  else
    self.setDescription("Unidentified persona. Rarity: Tier " .. state.tier
        .. ". Available grain: " .. ccTotal(state.top)
        .. ". Hidden: race, class, abilities. Click ID? to identify.")
    self.setColorTint({ 0.45, 0.45, 0.45 })
  end
end

function ccNoop() end
function pPrev() state.sel = (state.sel - 2) % #CC.elements + 1; refreshSel() end
function pNext() state.sel = state.sel % #CC.elements + 1; refreshSel() end
function refreshSel()
  local e = CC.elements[state.sel]
  broadcastToAll(self.getName() .. " grain cursor: " .. e.name .. " ("
      .. (state.top[e.name] or 0) .. "^ " .. (state.bottom[e.name] or 0) .. "v)",
      { e.color.r, e.color.g, e.color.b })
end

function pIdentify()
  if not state.identified then
    state.identified = true
    broadcastToAll("Identified: " .. state.name .. " — " .. state.race .. " "
        .. state.class .. " (Tier " .. state.tier .. ")", { 0.85, 0.75, 0.5 })
  end
  refresh()
end

function pPlus()
  if full() then return end
  state.top[selName()] = (state.top[selName()] or 0) + 1
  refresh()
end
function pMinus()
  local n = state.top[selName()] or 0
  if n > 0 then state.top[selName()] = n - 1 end
  refresh()
end
function pDrop()
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
function pRaise()
  local n = state.bottom[selName()] or 0
  if n > 0 then
    state.bottom[selName()] = n - 1
    state.top[selName()] = (state.top[selName()] or 0) + 1
  end
  refresh()
end

function ccGetPool()
  -- fog of war holds here too: the census never leaks an unidentified name
  local shown = state.identified and state.name or ("Unknown T" .. state.tier)
  return { kind = "persona", name = shown, tier = state.tier,
           top = state.top, bottom = state.bottom, timeless = isTimeless() }
end

function ccAddGrain(params)
  local e = ccElem(params.element)
  if e == nil then return false end
  local n = tonumber(params.n) or 1
  if used() + n > ccTier(state.tier).capacity then return false end
  local side = (params.side == "bottom") and "bottom" or "top"
  state[side][e.name] = (state[side][e.name] or 0) + n
  refresh()
  return true
end
