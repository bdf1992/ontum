-- ===== Biome / Region tile =====
-- A biome owns grains of its element and generates `rate` more each time
-- the Global Clock ends a turn (it listens via the cc-turn-listener tag).
-- TIME/TIMELESS toggle: a timeless biome's generation falls into its
-- bottom pool (the timeless side) instead of time.
-- Personas standing on the tile count toward the region in the census.
-- GM Notes JSON: {"name":"Region A", "element":"Fire", "own":5, "rate":1}

{{FORGE:COMMON}}

local state = { name = "Region", element = "Fire", rate = 1, timeless = false,
                top = {}, bottom = {} }

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
    local cfg = ccNotesConfig({ name = "Region", element = "Fire", own = 0, rate = 1 })
    state.name = tostring(cfg.name)
    state.element = (ccElem(cfg.element) or CC.elements[2]).name
    state.rate = tonumber(cfg.rate) or 1
    state.top = {}
    if (tonumber(cfg.own) or 0) > 0 then state.top[state.element] = tonumber(cfg.own) end
    state.bottom = {}
  end
  ccEnsureTag("cc-holder")
  ccEnsureTag("cc-biome")
  ccEnsureTag("cc-turn-listener")
  buildUI()
  refresh()
end

function buildUI()
  self.clearButtons()
  ccBtn({ click_function = "ccNoop", label = "", position = { 0, 0.58, -0.38 },
          width = 0, height = 0, font_size = 150 })                        -- 0 headline
  ccBtn({ click_function = "bMinus", label = "-", position = { -0.30, 0.58, 0.40 },
          width = 240, height = 240, font_size = 150 })                    -- 1
  ccBtn({ click_function = "bPlus", label = "+", position = { -0.15, 0.58, 0.40 },
          width = 240, height = 240, font_size = 150 })                    -- 2
  ccBtn({ click_function = "bToggle", label = "TIME", position = { 0.22, 0.58, 0.40 },
          width = 620, height = 240, font_size = 110,
          tooltip = "Toggle: a timeless region generates into its timeless pool" }) -- 3
end

function refresh()
  local e = ccElem(state.element)
  self.editButton({ index = 0,
    label = state.name .. "  [" .. state.element .. "]  "
      .. ccTotal(state.top) .. "^ " .. ccTotal(state.bottom) .. "v  (+" .. state.rate .. "/turn)" })
  self.editButton({ index = 3, label = state.timeless and "TIMELESS" or "TIME",
    color = state.timeless and { 0.25, 0.18, 0.4 } or { 0.2, 0.45, 0.25 },
    font_color = { 1, 1, 1 } })
  self.setName(state.name .. " — " .. state.element .. " biome")
  self.setDescription("Generates " .. state.rate .. " " .. state.element
      .. " grain(s) per turn" .. (state.timeless and " INTO TIMELESSNESS" or "")
      .. "\nOwn (in time): " .. ccFmtPool(state.top)
      .. "\nOwn (timeless): " .. ccFmtPool(state.bottom)
      .. "\nPersonas standing here add their grains to this region's census.")
  if state.timeless then
    self.setColorTint({ 0.22, 0.16, 0.32 })
  elseif e ~= nil then
    self.setColorTint({ e.color.r, e.color.g, e.color.b })
  end
end

function ccNoop() end
function bPlus() state.top[state.element] = (state.top[state.element] or 0) + 1; refresh() end
function bMinus()
  local n = state.top[state.element] or 0
  if n > 0 then state.top[state.element] = n - 1 end
  refresh()
end
function bToggle()
  state.timeless = not state.timeless
  broadcastToAll(state.name .. (state.timeless
      and " slips into TIMELESSNESS — its grains now fall to the timeless pool."
      or " rejoins TIME."), { 0.6, 0.4, 0.9 })
  refresh()
end

-- the Global Clock fires this on every End Turn
function onGlobalTurnEnd(params)
  local side = state.timeless and "bottom" or "top"
  state[side][state.element] = (state[side][state.element] or 0) + state.rate
  refresh()
end

function ccGetPool()
  return { kind = "biome", name = state.name, element = state.element,
           top = state.top, bottom = state.bottom, timeless = state.timeless }
end
