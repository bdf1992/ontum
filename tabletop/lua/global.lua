-- ===== Catalyst Core: The 13th Hour — Global script =====
-- Chat commands route to the Spawner Console (tag cc-console) and the
-- Global Clock (tag cc-clock). Type "!cc help" in chat.

{{FORGE:COMMON}}

function onLoad()
  printToAll("Catalyst Core: The 13th Hour — paper-play kit loaded.", { 0.85, 0.75, 0.5 })
  printToAll(string.gsub(CC.clock.eon_message, "{turns}", tostring(CC.clock.max_turns)),
      { 0.9, 0.6, 0.2 })
  printToAll("Start with " .. CC.currency.start .. " " .. CC.currency.name
      .. ". Chat commands: !cc help", { 0.85, 0.75, 0.5 })
end

local function findTagged(tag)
  for _, o in ipairs(getAllObjects()) do
    if o.hasTag(tag) then return o end
  end
  return nil
end

local function words(s)
  local out = {}
  for w in string.gmatch(s, "%S+") do table.insert(out, w) end
  return out
end

function onChat(message, player)
  if string.sub(message, 1, 3) ~= "!cc" then return true end
  local a = words(message)
  local cmd = string.lower(a[2] or "help")
  local console = findTagged("cc-console")
  if cmd == "endturn" then
    local clock = findTagged("cc-clock")
    if clock ~= nil then clock.call("endTurn")
    else printToAll("No Global Clock on the table — spawn one: !cc clock", { 0.9, 0.4, 0.3 }) end
    return false
  end
  if console == nil then
    printToAll("No Spawner Console on the table — place it from Saved Objects first.",
        { 0.9, 0.4, 0.3 })
    return false
  end
  if cmd == "help" then
    console.call("cHelp")
  elseif cmd == "census" then
    console.call("ccCensus")
  elseif cmd == "shape" then
    console.call("ccSpawn", { kind = "shape", shape = a[3], color = a[4],
                              tier = tonumber(a[5]) })
  elseif cmd == "hourglass" then
    console.call("ccSpawn", { kind = "hourglass", tier = tonumber(a[3]) })
  elseif cmd == "persona" then
    console.call("ccSpawn", { kind = "persona", name = a[3], race = a[4],
                              class = a[5], tier = tonumber(a[6]) })
  elseif cmd == "biome" then
    console.call("ccSpawn", { kind = "biome", name = a[3], element = a[4],
                              own = tonumber(a[5]), rate = tonumber(a[6]) })
  elseif cmd == "clock" or cmd == "grains" or cmd == "coins" or cmd == "ap" then
    console.call("ccSpawn", { kind = cmd })
  else
    console.call("cHelp")
  end
  return false
end
