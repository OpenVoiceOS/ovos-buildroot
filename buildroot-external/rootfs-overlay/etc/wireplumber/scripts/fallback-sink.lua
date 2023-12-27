-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author Frédéric Danis <frederic.danis@collabora.com>
--
-- SPDX-License-Identifier: MIT

local sink_ids = {}
local fallback_node = nil

node_om = ObjectManager {
  Interest {
    type = "node",
    Constraint { "media.class", "matches", "Audio/Sink", type = "pw-global" },
    -- Do not consider endpoints created by WirePlumber
    Constraint { "wireplumber.is-endpoint", "!", true, type = "pw" },
    -- or the fallback sink itself
    Constraint { "wireplumber.is-fallback", "!", true, type = "pw" },
  }
}

function createFallbackSink()
  if fallback_node then
    return
  end

  Log.info("Create fallback sink")

  local properties = {}

  properties["node.name"] = "auto_null"
  properties["node.description"] = "Dummy Output"

  properties["audio.rate"] = 48000
  properties["audio.channels"] = 2
  properties["audio.position"] = "FL,FR"

  properties["media.class"] = "Audio/Sink"
  properties["factory.name"] = "support.null-audio-sink"
  properties["node.virtual"] = "true"
  properties["monitor.channel-volumes"] = "true"

  properties["wireplumber.is-fallback"] = "true"
  properties["priority.session"] = 500

  fallback_node = LocalNode("adapter", properties)
  fallback_node:activate(Feature.Proxy.BOUND)
end

function checkSinks()
  local sink_ids_items = 0
  for _ in pairs(sink_ids) do sink_ids_items = sink_ids_items + 1 end

  if sink_ids_items > 0 then
    if fallback_node then
      Log.info("Remove fallback sink")
      fallback_node = nil
    end
  elseif not fallback_node then
    createFallbackSink()
  end
end

function checkSinksAfterTimeout()
  if timeout_source then
    timeout_source:destroy()
  end
  timeout_source = Core.timeout_add(1000, function ()
    checkSinks()
    timeout_source = nil
  end)
end

node_om:connect("object-added", function (_, node)
  Log.debug("object added: " .. node.properties["object.id"] .. " " ..
      tostring(node.properties["node.name"]))

  sink_ids[node.properties["object.id"]] = node.properties["node.name"]

  checkSinksAfterTimeout()
end)

node_om:connect("object-removed", function (_, node)
  Log.debug("object removed: " .. node.properties["object.id"] .. " " ..
      tostring(node.properties["node.name"]))

  sink_ids[node.properties["object.id"]] = nil
  checkSinksAfterTimeout()
end)

node_om:activate()

checkSinksAfterTimeout()
