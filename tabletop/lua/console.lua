-- ===== The Spawner Console — the in-game script generator =====
-- Generic flexible shapes: pick SHAPE x COLOR x TIER (size), hit SPAWN.
-- Presets spawn fully-scripted kit pieces (hourglass, persona, biome,
-- clock, grain bags, timecoin, AP) — their Lua is embedded here by the
-- forge, so the console needs nothing else on the table.
-- CENSUS reads every cc-holder: world totals per element (time vs
-- timelessness) and per-region totals including personas standing on
-- each biome tile.

{{FORGE:COMMON}}

{{FORGE:SCRIPTS}}

local COLORS = {}
local state = { shape = 1, color = 2, tier = 1, spawned = 0 }

function onSave() return JSON.encode(state) end

function onLoad(saved)
  if saved ~= nil and saved ~= "" then
    local ok, s = pcall(function() return JSON.decode(saved) end)
    if ok and type(s) == "table" and s.shape ~= nil then state = s end
  end
  for _, e in ipairs(CC.elements) do
    table.insert(COLORS, { name = e.name, color = { e.color.r, e.color.g, e.color.b } })
  end
  table.insert(COLORS, { name = "White", color = { 0.95, 0.95, 0.95 } })
  table.insert(COLORS, { name = "Black", color = { 0.12, 0.12, 0.12 } })
  ccEnsureTag("cc-console")
  self.setLock(true)
  buildUI()
  refresh()
end

function buildUI()
  self.clearButtons()
  ccBtn({ click_function = "ccNoop", label = "CATALYST CORE — SPAWNER",
          position = { 0, 0.58, -0.44 }, width = 0, height = 0, font_size = 130 }) -- 0
  ccBtn({ click_function = "cShape", label = "", position = { -0.22, 0.58, -0.30 },
          width = 900, height = 240, font_size = 100,
          tooltip = "Cycle shape" })                                               -- 1
  ccBtn({ click_function = "cColor", label = "", position = { 0.22, 0.58, -0.30 },
          width = 900, height = 240, font_size = 100,
          tooltip = "Cycle color (the eight elements + white/black)" })            -- 2
  ccBtn({ click_function = "cTier", label = "", position = { -0.22, 0.58, -0.18 },
          width = 900, height = 240, font_size = 100,
          tooltip = "Cycle tier: sets size, hourglass capacity, persona rarity" }) -- 3
  ccBtn({ click_function = "cSpawnShape", label = "SPAWN SHAPE", position = { 0.22, 0.58, -0.18 },
          width = 900, height = 240, font_size = 100,
          color = { 0.2, 0.45, 0.25 }, font_color = { 1, 1, 1 } })                 -- 4
  local presets = {
    { "HOURGLASS", "cHourglass" }, { "PERSONA", "cPersona" }, { "BIOME", "cBiome" },
    { "CLOCK", "cClock" }, { "GRAIN BAGS", "cGrains" }, { "TIMECOIN", "cCoins" },
    { "AP TOKENS", "cAP" }, { "CENSUS", "cCensus" }, { "HELP", "cHelp" },
  }
  for i, p in ipairs(presets) do
    local col = (i - 1) % 3
    local row = math.floor((i - 1) / 3)
    ccBtn({ click_function = p[2], label = p[1],
            position = { -0.30 + col * 0.30, 0.58, 0.02 + row * 0.14 },
            width = 800, height = 240, font_size = 90,
            color = { 0.25, 0.22, 0.30 }, font_color = { 0.95, 0.9, 0.8 } })
  end
end

function refresh()
  self.editButton({ index = 1, label = "SHAPE: " .. CC.shapes[state.shape].label })
  local c = COLORS[state.color]
  self.editButton({ index = 2, label = "COLOR: " .. c.name, font_color = c.color })
  self.editButton({ index = 3, label = "TIER: " .. state.tier
      .. " (cap " .. ccTier(state.tier).capacity .. ")" })
  self.setName("Spawner Console")
  self.setDescription("The in-game script generator. Buttons here, or chat:\n!cc help")
end

function ccNoop() end
function cShape() state.shape = state.shape % #CC.shapes + 1; refresh() end
function cColor() state.color = state.color % #COLORS + 1; refresh() end
function cTier() state.tier = state.tier % #CC.tiers + 1; refresh() end

local function dropPos()
  state.spawned = state.spawned + 1
  local p = self.getPosition()
  local i = state.spawned % 5
  return { x = p.x + (i - 2) * 2.2, y = p.y + 2.5, z = p.z - 6 }
end

-- ---- generic shapes ----

function cSpawnShape(_, _, _)
  ccSpawn({ kind = "shape", shape = CC.shapes[state.shape].label,
            color = COLORS[state.color].name, tier = state.tier })
end

-- ---- presets ----

function cHourglass() ccSpawn({ kind = "hourglass", tier = state.tier }) end
function cPersona() ccSpawn({ kind = "persona", tier = state.tier }) end
function cBiome() ccSpawn({ kind = "biome", element = COLORS[state.color].name }) end
function cClock() ccSpawn({ kind = "clock" }) end
function cGrains() ccSpawn({ kind = "grains" }) end
function cCoins() ccSpawn({ kind = "coins" }) end
function cAP() ccSpawn({ kind = "ap" }) end
function cCensus() ccCensus() end

function cHelp()
  local lines = {
    "— Catalyst Core spawner —",
    "Buttons: pick SHAPE / COLOR / TIER, then SPAWN SHAPE; presets spawn scripted pieces.",
    "Chat: !cc shape <shape> <color> [tier] | !cc hourglass [tier]",
    "  !cc persona [name] [race] [class] [tier] | !cc biome [name] [element] [own] [rate]",
    "  !cc clock | !cc grains | !cc coins | !cc ap | !cc census | !cc endturn",
    "Shapes: block, slab, wedge, pawn, die, chip, checker. Colors: the 8 elements, white, black.",
    "Every scripted piece is reconfigurable via its GM Notes (JSON).",
  }
  for _, l in ipairs(lines) do printToAll(l, { 0.85, 0.75, 0.5 }) end
end

-- ---- the one spawn seam (buttons and chat both land here) ----

local function findShape(label)
  for _, s in ipairs(CC.shapes) do
    if string.lower(s.label) == string.lower(tostring(label)) then return s end
  end
  return CC.shapes[1]
end

local function findColor(name)
  for _, c in ipairs(COLORS) do
    if string.lower(c.name) == string.lower(tostring(name)) then return c end
  end
  return COLORS[#COLORS - 1]  -- white
end

local function scripted(objType, scale, script, notes, name, tint)
  local o = spawnObject({ type = objType, position = dropPos(), scale = scale, sound = false })
  o.setGMNotes(JSON.encode(notes or {}))  -- notes first: the script reads them on load
  if name then o.setName(name) end
  if tint then o.setColorTint(tint) end
  o.setLuaScript(script)
  o.reload()  -- guarantee the script's onLoad runs, whatever setLuaScript did
  return o
end

function ccSpawn(params)
  local kind = tostring(params.kind or "shape")
  local tier = math.min(#CC.tiers, math.max(1, tonumber(params.tier) or state.tier))
  if kind == "shape" then
    local shape = findShape(params.shape or CC.shapes[state.shape].label)
    local color = findColor(params.color or COLORS[state.color].name)
    local size = 0.6 + 0.35 * tier
    local o = spawnObject({ type = shape.tts, position = dropPos(),
                            scale = { size, size, size }, sound = false })
    o.setColorTint(color.color)
    o.setName(color.name .. " " .. shape.label .. " (T" .. tier .. ")")
    o.addTag("cc-shape")
  elseif kind == "hourglass" then
    scripted("BlockRectangle", { 2.5, 0.8, 2.5 }, CC_SCRIPTS.hourglass,
        { tier = tier }, "Hourglass T" .. tier)
  elseif kind == "persona" then
    scripted("PlayerPawn", { 1.1, 1.1, 1.1 }, CC_SCRIPTS.persona,
        { name = params.name or ("Persona " .. state.spawned),
          race = params.race or "Mortal", class = params.class or "Lord",
          tier = tier, pool = params.pool or {}, identified = params.identified == true })
  elseif kind == "biome" then
    local e = ccElem(params.element)
    if e == nil then
      printToAll("A biome needs one of the eight element colors ('"
          .. tostring(params.element) .. "' is not one) — spawning Fire.",
          { 0.9, 0.6, 0.2 })
      e = CC.elements[2]
    end
    scripted("BlockRectangle", { 6, 0.2, 6 }, CC_SCRIPTS.biome,
        { name = params.name or ("Region " .. state.spawned), element = e.name,
          own = tonumber(params.own) or 0, rate = tonumber(params.rate) or 1 })
  elseif kind == "clock" then
    scripted("BlockSquare", { 7, 0.3, 7 }, CC_SCRIPTS.clock,
        { max_turns = tonumber(params.max_turns) or CC.clock.max_turns },
        "The Global Clock", { 0.30, 0.22, 0.16 })
  elseif kind == "grains" then
    for i, e in ipairs(CC.elements) do
      local p = self.getPosition()
      spawnGrainBag(e, { x = p.x + (i - 4.5) * 2.4, y = p.y + 2.5, z = p.z - 9 })
    end
  elseif kind == "coins" then
    local chips = { [10] = "Chip_10", [100] = "Chip_100", [1000] = "Chip_1000" }
    local i = 0
    for _, denom in ipairs(CC.currency.denominations) do
      local p = self.getPosition()
      spawnCoinBag(denom, chips[denom] or "Chip_100",
          { x = p.x + (i - 1) * 2.4, y = p.y + 2.5, z = p.z - 11 })
      i = i + 1
    end
  elseif kind == "ap" then
    local p = self.getPosition()
    spawnTokenBag(CC.attention.name, { 0.15, 0.65, 0.6 },
        { x = p.x, y = p.y + 2.5, z = p.z - 13 },
        CC.attention.name .. " — attention/action points ("
        .. CC.attention.per_turn .. "/turn; unspent AP converts to "
        .. CC.currency.name .. " at end of turn)"
        .. (CC.attention.note and ("\nNote: " .. CC.attention.note) or ""))
  else
    printToAll("Unknown spawn kind: " .. kind, { 0.9, 0.4, 0.3 })
  end
end

-- one recipe for every infinite bag: spawn the bag, spawn its one item
-- above it, drop the item in once physics has settled
local function spawnFilledBag(spec)
  local bag = spawnObject({ type = "Infinite_Bag", position = spec.pos,
                            scale = { 0.9, 0.9, 0.9 }, sound = false })
  bag.setColorTint(spec.bagTint)
  bag.setName(spec.bagName)
  if spec.desc then bag.setDescription(spec.desc) end
  if spec.bagTag then bag.addTag(spec.bagTag) end
  local item = spawnObject({ type = spec.itemType,
      position = { x = spec.pos.x, y = spec.pos.y + 3, z = spec.pos.z },
      scale = spec.itemScale, sound = false })
  item.setColorTint(spec.itemTint or spec.bagTint)
  item.setName(spec.itemName)
  if spec.itemTag then item.addTag(spec.itemTag) end
  Wait.frames(function() bag.putObject(item) end, 20)
end

function spawnGrainBag(e, pos)
  spawnFilledBag({
    pos = pos, bagName = e.name .. " Grains",
    bagTint = { e.color.r, e.color.g, e.color.b }, bagTag = "cc-grainbag",
    desc = e.role .. " | opposite: " .. e.opposite
        .. "\nPull grains from here into hourglasses and pools.",
    itemType = "Checker_white", itemName = e.name .. " Grain",
    itemScale = { 0.45, 0.45, 0.45 }, itemTag = "cc-grain",
  })
end

function spawnCoinBag(denom, chipType, pos)
  spawnFilledBag({
    pos = pos, bagName = CC.currency.name .. " " .. denom,
    bagTint = { 0.85, 0.7, 0.25 }, bagTag = "cc-coinbag",
    itemType = chipType, itemName = CC.currency.name .. " " .. denom,
    itemTint = { 0.9, 0.75, 0.3 },
  })
end

function spawnTokenBag(name, tint, pos, desc)
  spawnFilledBag({
    pos = pos, bagName = name .. " Tokens", bagTint = tint, desc = desc,
    itemType = "Checker_white", itemName = name, itemScale = { 0.5, 0.5, 0.5 },
  })
end

-- ---- the census: region + occupants -> world (bdo's Herald example) ----

local function inBounds(pos, b)
  return math.abs(pos.x - b.center.x) <= b.size.x / 2
     and math.abs(pos.z - b.center.z) <= b.size.z / 2
end

local function addInto(total, pool)
  for k, v in pairs(pool or {}) do total[k] = (total[k] or 0) + v end
end

function ccCensus()
  local biomes, movers = {}, {}
  local worldTop, worldBottom = {}, {}
  for _, o in ipairs(getAllObjects()) do
    if o.hasTag("cc-holder") then
      local p = o.call("ccGetPool")
      if p ~= nil then
        addInto(worldTop, p.top)
        addInto(worldBottom, p.bottom)
        if p.kind == "biome" then
          table.insert(biomes, { pool = p, bounds = o.getBounds() })
        else
          table.insert(movers, { pool = p, pos = o.getPosition() })
        end
      end
    end
  end
  printToAll("===== CENSUS =====", { 0.85, 0.75, 0.5 })
  printToAll("WORLD in time: " .. ccFmtPool(worldTop), { 0.85, 0.75, 0.5 })
  printToAll("WORLD timeless: " .. ccFmtPool(worldBottom), { 0.6, 0.4, 0.9 })
  local t, b = ccTotal(worldTop), ccTotal(worldBottom)
  printToAll("Grains: " .. t .. " in time vs " .. b .. " timeless — "
      .. (t >= b and "TIME holds." or "TIMELESSNESS is winning."),
      t >= b and { 0.3, 0.7, 0.4 } or { 0.7, 0.3, 0.9 })
  for _, bio in ipairs(biomes) do
    local regionTop, regionBottom = {}, {}
    addInto(regionTop, bio.pool.top)
    addInto(regionBottom, bio.pool.bottom)
    local names = {}
    for _, m in ipairs(movers) do
      if inBounds(m.pos, bio.bounds) then
        addInto(regionTop, m.pool.top)
        addInto(regionBottom, m.pool.bottom)
        table.insert(names, m.pool.name or m.pool.kind)
      end
    end
    local line = bio.pool.name .. " [" .. bio.pool.element .. "]: "
        .. ccFmtPool(regionTop)
    if ccTotal(regionBottom) > 0 then line = line .. " | timeless: " .. ccFmtPool(regionBottom) end
    if #names > 0 then line = line .. "  (with " .. table.concat(names, ", ") .. ")" end
    printToAll(line, { 0.85, 0.85, 0.85 })
  end
end
