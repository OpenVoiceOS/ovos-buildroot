-- WirePlumber
--
-- Copyright © 2022 Pauli Virtanen
--    @author Pauli Virtanen
--
-- SPDX-License-Identifier: MIT

local config = ... or {}

-- unique device/node name tables
node_names_table = nil
id_to_name_table = nil

-- preprocess rules and create Interest objects
for _, r in ipairs(config.rules or {}) do
  r.interests = {}
  for _, i in ipairs(r.matches) do
    local interest_desc = { type = "properties" }
    for _, c in ipairs(i) do
      c.type = "pw"
      table.insert(interest_desc, Constraint(c))
    end
    local interest = Interest(interest_desc)
    table.insert(r.interests, interest)
  end
  r.matches = nil
end

-- applies properties from config.rules when asked to
function rulesApplyProperties(properties)
  for _, r in ipairs(config.rules or {}) do
    if r.apply_properties then
      for _, interest in ipairs(r.interests) do
        if interest:matches(properties) then
          for k, v in pairs(r.apply_properties) do
            properties[k] = v
          end
        end
      end
    end
  end
end

function setLatencyOffset(node, offset_msec)
  if not offset_msec then
    return
  end

  local props = { "Spa:Pod:Object:Param:Props", "Props" }
  props.latencyOffsetNsec = tonumber(offset_msec) * 1000000

  local param = Pod.Object(props)
  Log.debug(param, "setting latency offset on " .. tostring(node))
  node:set_param("Props", param)
end

function createNode(parent, id, type, factory, properties)
  properties["factory.name"] = factory

  -- set the node description
  local desc = properties["node.description"]
  -- sanitize description, replace ':' with ' '
  properties["node.description"] = desc:gsub("(:)", " ")

  -- set the node name
  local name =
      "bluez_midi." .. properties["api.bluez5.address"]
  -- sanitize name
  name = name:gsub("([^%w_%-%.])", "_")
  -- deduplicate nodes with the same name
  properties["node.name"] = name
  for counter = 2, 99, 1 do
    if node_names_table[properties["node.name"]] ~= true then
      node_names_table[properties["node.name"]] = true
      break
    end
    properties["node.name"] = name .. "." .. counter
  end

  properties["api.glib.mainloop"] = "true"

  -- apply properties from config.rules
  rulesApplyProperties(properties)

  local latency_offset = properties["node.latency-offset-msec"]
  properties["node.latency-offset-msec"] = nil

  -- create the node
  -- it doesn't necessarily need to be a local node,
  -- the other Bluetooth parts run in the local process,
  -- so it's consistent to have also this here
  local node = LocalNode("spa-node-factory", properties)
  node:activate(Feature.Proxy.BOUND)
  parent:store_managed_object(id, node)
  id_to_name_table[id] = properties["node.name"]
  setLatencyOffset(node, latency_offset)
end

function createMonitor()
  local monitor_props = {}
  for k, v in pairs(config.properties or {}) do
    monitor_props[k] = v
  end
  monitor_props["server"] = nil

  monitor_props["api.glib.mainloop"] = "true"

  local monitor = SpaDevice("api.bluez5.midi.enum", monitor_props)
  if monitor then
    monitor:connect("create-object", createNode)
    monitor:connect("object-removed", function (parent, id)
        node_names_table[id_to_name_table[id]] = nil
        id_to_name_table[id] = nil
    end)
  else
    Log.message("PipeWire's BlueZ MIDI SPA missing or broken. Bluetooth not supported.")
    return nil
  end

  -- reset the name tables to make sure names are recycled
  node_names_table = {}
  id_to_name_table = {}

  monitor:activate(Feature.SpaDevice.ENABLED)
  return monitor
end

function createServers()
  local props = config.properties or {}

  if not props["servers"] then
    return nil
  end

  local servers = {}
  local i = 1

  for k, v in pairs(props["servers"]) do
    local node_props = {
      ["node.name"] = v,
      ["node.description"] = string.format(I18n.gettext("BLE MIDI %d"), i),
      ["api.bluez5.role"] = "server",
      ["factory.name"] = "api.bluez5.midi.node",
      ["api.glib.mainloop"] = "true",
    }
    rulesApplyProperties(node_props)

    local latency_offset = node_props["node.latency-offset-msec"]
    node_props["node.latency-offset-msec"] = nil

    local node = LocalNode("spa-node-factory", node_props)
    if node then
      node:activate(Feature.Proxy.BOUND)
      table.insert(servers, node)
      setLatencyOffset(node, latency_offset)
    else
      Log.message("Failed to create BLE MIDI server.")
    end
    i = i + 1
  end

  return servers
end

logind_plugin = Plugin.find("logind")
if logind_plugin then
  -- if logind support is enabled, activate
  -- the monitor only when the seat is active
  function startStopMonitor(seat_state)
    Log.info(logind_plugin, "Seat state changed: " .. seat_state)

    if seat_state == "active" then
      monitor = createMonitor()
      servers = createServers()
    elseif monitor then
      monitor:deactivate(Feature.SpaDevice.ENABLED)
      monitor = nil
      servers = nil
    end
  end

  logind_plugin:connect("state-changed", function(p, s) startStopMonitor(s) end)
  startStopMonitor(logind_plugin:call("get-state"))
else
  monitor = createMonitor()
  servers = createServers()
end
