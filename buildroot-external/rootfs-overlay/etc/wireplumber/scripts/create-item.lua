-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author Julian Bouzas <julian.bouzas@collabora.com>
--
-- SPDX-License-Identifier: MIT

-- Receive script arguments from config.lua
local config = ... or {}

items = {}

function configProperties(node)
  local np = node.properties
  local properties = {
    ["item.node"] = node,
    ["item.plugged.usec"] = GLib.get_monotonic_time(),
    ["item.features.no-dsp"] = config["audio.no-dsp"],
    ["item.features.monitor"] = true,
    ["item.features.control-port"] = false,
    ["node.id"] = node["bound-id"],
    ["client.id"] = np["client.id"],
    ["object.path"] = np["object.path"],
    ["object.serial"] = np["object.serial"],
    ["target.object"] = np["target.object"],
    ["priority.session"] = np["priority.session"],
    ["device.id"] = np["device.id"],
    ["card.profile.device"] = np["card.profile.device"],
    ["target.endpoint"] = np["target.endpoint"],
  }

  for k, v in pairs(np) do
    if k:find("^node") or k:find("^stream") or k:find("^media") then
      properties[k] = v
    end
  end

  local media_class = properties["media.class"] or ""

  if not properties["media.type"] then
    for _, i in ipairs({ "Audio", "Video", "Midi" }) do
      if media_class:find(i) then
        properties["media.type"] = i
        break
      end
    end
  end

  properties["item.node.type"] =
      media_class:find("^Stream/") and "stream" or "device"

  if media_class:find("Sink") or
      media_class:find("Input") or
      media_class:find("Duplex") then
    properties["item.node.direction"] = "input"
  elseif media_class:find("Source") or media_class:find("Output") then
    properties["item.node.direction"] = "output"
  end
  return properties
end

function addItem (node, item_type)
  local id = node["bound-id"]
  local item

  -- create item
  item = SessionItem ( item_type )
  items[id] = item

  -- configure item
  if not item:configure(configProperties(node)) then
    Log.warning(item, "failed to configure item for node " .. tostring(id))
    return
  end

  item:register ()

  -- activate item
  items[id]:activate (Features.ALL, function (item, e)
    if e then
      Log.message(item, "failed to activate item: " .. tostring(e));
      if item then
        item:remove ()
      end
    else
      Log.info(item, "activated item for node " .. tostring(id))

      -- Trigger object managers to update status
      item:remove ()
      if item["active-features"] ~= 0 then
        item:register ()
      end
    end
  end)
end

nodes_om = ObjectManager {
  Interest {
    type = "node",
    Constraint { "media.class", "#", "Stream/*", type = "pw-global" },
  },
  Interest {
    type = "node",
    Constraint { "media.class", "#", "Video/*", type = "pw-global" },
  },
  Interest {
    type = "node",
    Constraint { "media.class", "#", "Audio/*", type = "pw-global" },
    Constraint { "wireplumber.is-endpoint", "-", type = "pw" },
  },
}

nodes_om:connect("object-added", function (om, node)
  local media_class = node.properties['media.class']
  if string.find (media_class, "Audio") then
    addItem (node, "si-audio-adapter")
  else
    addItem (node, "si-node")
  end
end)

nodes_om:connect("object-removed", function (om, node)
  local id = node["bound-id"]
  if items[id] then
    items[id]:remove ()
    items[id] = nil
  end
end)

nodes_om:activate()
