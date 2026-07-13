-- ===== The Global Clock — the one clock; everything else is grains =====
-- One hand, twelve hours. End Turn advances the hand and fires the world:
-- every object tagged cc-turn-listener gets onGlobalTurnEnd({turn=N}).
-- Turns are a resource ([+T]/[-T] extend or shorten the game).
-- Click an hour to warp it: ON -> REMOVED (the hand skips it; time lurches)
-- -> DOUBLED (the hand lingers there a second turn) -> ON.
-- GM Notes JSON: {"max_turns":12}

{{FORGE:COMMON}}

local ROMAN = { "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII" }
local state = { turn = 1, max_turns = 12, hand = 12, hours = {}, linger = false }

function onSave() return JSON.encode(state) end

function onLoad(saved)
  local restored = false
  if saved ~= nil and saved ~= "" then
    local ok, s = pcall(function() return JSON.decode(saved) end)
    if ok and type(s) == "table" and s.hours ~= nil and #s.hours == CC.clock.hours then
      state = s
      restored = true
    end
  end
  if not restored then
    local cfg = ccNotesConfig({ max_turns = CC.clock.max_turns })
    state.max_turns = tonumber(cfg.max_turns) or CC.clock.max_turns
    state.hours = {}
    for i = 1, CC.clock.hours do state.hours[i] = "on" end
  end
  ccEnsureTag("cc-clock")
  buildUI()
  refresh()
end

function buildUI()
  self.clearButtons()
  -- the twelve hours, a dial (indices 1..12; hour h sits where a clock face puts it)
  for h = 1, CC.clock.hours do
    local ang = math.rad(h * (360 / CC.clock.hours) - 90)
    ccBtn({ click_function = "hour" .. h, label = ROMAN[h],
            position = { 0.40 * math.cos(ang), 0.62, -0.40 * math.sin(ang) },
            width = 260, height = 260, font_size = 110,
            tooltip = "Hour " .. ROMAN[h] .. ": click to warp (remove / double / restore)" })
  end
  ccBtn({ click_function = "endTurn", label = "END TURN", position = { 0, 0.62, 0 },
          width = 900, height = 420, font_size = 130,
          color = { 0.75, 0.2, 0.15 }, font_color = { 1, 1, 1 } })          -- 12
  ccBtn({ click_function = "ccNoop", label = "", position = { 0, 0.62, 0.17 },
          width = 0, height = 0, font_size = 90 })                          -- 13 status
  ccBtn({ click_function = "turnPlus", label = "+T", position = { 0.62, 0.62, -0.55 },
          width = 260, height = 220, font_size = 100,
          tooltip = "Gain a turn: the end comes later" })                   -- 14
  ccBtn({ click_function = "turnMinus", label = "-T", position = { 0.62, 0.62, -0.42 },
          width = 260, height = 220, font_size = 100,
          tooltip = "Lose a turn: the end comes sooner" })                  -- 15
end

local function hourLabel(h)
  if state.hours[h] == "off" then return "--" end
  if state.hours[h] == "dup" then return ROMAN[h] .. "!" end
  return ROMAN[h]
end

function refresh()
  for h = 1, CC.clock.hours do
    local mine = (h == state.hand)
    self.editButton({ index = h - 1, label = hourLabel(h),
      color = mine and { 0.9, 0.75, 0.2 } or
        (state.hours[h] == "off" and { 0.15, 0.12, 0.2 } or { 0.35, 0.25, 0.18 }),
      font_color = mine and { 0.1, 0.1, 0.1 } or { 0.95, 0.9, 0.8 } })
  end
  local left = state.max_turns - state.turn + 1
  self.editButton({ index = 13,
    label = "Turn " .. state.turn .. "/" .. state.max_turns
      .. "  |  hand on " .. hourLabel(state.hand)
      .. "  |  Eon in " .. math.max(0, left) })
  self.setName("The Global Clock — Turn " .. state.turn .. "/" .. state.max_turns)
end

function ccNoop() end

-- click an hour to warp it: on -> off -> dup -> on
for h = 1, 12 do
  _G["hour" .. h] = function()
    local cur = state.hours[h]
    state.hours[h] = (cur == "on") and "off" or ((cur == "off") and "dup" or "on")
    if state.hours[h] == "off" then
      broadcastToAll("The hour of " .. ROMAN[h] .. " is deleted from the clock.", { 0.6, 0.4, 0.9 })
    elseif state.hours[h] == "dup" then
      broadcastToAll("The hour of " .. ROMAN[h] .. " is doubled — time lingers there.", { 0.6, 0.4, 0.9 })
    end
    refresh()
  end
end

function turnPlus()
  state.max_turns = state.max_turns + 1
  broadcastToAll("A turn is gained — the Eon arrives later. (" .. state.max_turns .. " turns)", { 0.3, 0.7, 0.4 })
  refresh()
end

function turnMinus()
  state.max_turns = math.max(1, state.max_turns - 1)
  broadcastToAll("A turn is lost — the Eon arrives sooner. (" .. state.max_turns .. " turns)", { 0.9, 0.4, 0.3 })
  refresh()
end

local function advanceHand()
  -- a doubled hour holds the hand for one extra turn
  if state.hours[state.hand] == "dup" and not state.linger then
    state.linger = true
    return {}
  end
  state.linger = false
  local skipped, steps = {}, 0
  repeat
    state.hand = state.hand % CC.clock.hours + 1
    steps = steps + 1
    if state.hours[state.hand] == "off" then table.insert(skipped, ROMAN[state.hand]) end
  until state.hours[state.hand] ~= "off" or steps > CC.clock.hours
  if steps > CC.clock.hours then
    broadcastToAll("Every hour is deleted — the hand spins in a clockless void.", { 0.7, 0.3, 0.9 })
  end
  return skipped
end

function endTurn()
  local skipped = advanceHand()
  state.turn = state.turn + 1
  if #skipped > 0 then
    broadcastToAll("The hour" .. (#skipped > 1 and "s" or "") .. " of "
        .. table.concat(skipped, ", ")
        .. " never come" .. (#skipped > 1 and "" or "s")
        .. " — you lose that time, and something stirs...", { 0.7, 0.3, 0.9 })
  end
  -- the world computes: biomes generate, events fire
  local fired = 0
  for _, o in ipairs(getAllObjects()) do
    if o ~= self and o.hasTag("cc-turn-listener") then
      o.call("onGlobalTurnEnd", { turn = state.turn })
      fired = fired + 1
    end
  end
  local left = state.max_turns - state.turn + 1
  if left <= 0 then
    broadcastToAll("THE EON HAS ARRIVED. Count the grains: time against timelessness decides the world.", { 0.95, 0.8, 0.2 })
  else
    broadcastToAll("Turn " .. state.turn .. " begins — the Eon arrives in " .. left
        .. " turn" .. (left == 1 and "" or "s") .. ". (" .. fired .. " listener"
        .. (fired == 1 and "" or "s") .. " fired)", { 0.85, 0.75, 0.5 })
  end
  refresh()
end

-- seam for the console / chat
function ccGetClock()
  return { turn = state.turn, max_turns = state.max_turns, hand = state.hand, hours = state.hours }
end
