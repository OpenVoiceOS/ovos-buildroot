-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author Julian Bouzas <julian.bouzas@collabora.com>
--
-- SPDX-License-Identifier: MIT

-- Receive script arguments from config.lua
local config = ... or {}

-- ensure config.move and config.follow are not nil
config.move = config.move or false
config.follow = config.follow or false

local self = {}
self.scanning = false
self.pending_rescan = false

function rescan ()
  -- check endpoints and register new links
  for si_ep in endpoints_om:iterate() do
    handleLinkable(si_ep)
  end

  for filter in streams_om:iterate {
    Constraint { "node.link-group", "+" },
  } do
    handleFilter(filter)
  end
end

function scheduleRescan ()
  if self.scanning then
    self.pending_rescan = true
    return
  end

  self.scanning = true
  rescan ()
  self.scanning = false

  if self.pending_rescan then
    self.pending_rescan = false
    Core.sync(function ()
      scheduleRescan ()
    end)
  end
end

function findFilterTarget (props)
  for si_target in linkables_om:iterate {
    -- exclude filter targets
    Constraint { "node.link-group", "+" },
  } do
    local si_props = si_target.properties
    if si_props["target.endpoint"] and si_props["target.endpoint"] == props["name"] then
      return si_target
    end
  end
end

function findTargetByDefaultNode (target_media_class)
  local def_id = default_nodes:call("get-default-node", target_media_class)
  if def_id ~= Id.INVALID then
    for si_target in linkables_om:iterate {
      -- exclude filter targets
      Constraint { "node.link-group", "-" },
    } do
      local target_node = si_target:get_associated_proxy ("node")
      if target_node["bound-id"] == def_id then
        return si_target
      end
    end
  end
  return nil
end

function findTargetByFirstAvailable (target_media_class)
  for si_target in linkables_om:iterate {
    -- exclude filter targets
    Constraint { "node.link-group", "-" },
  } do
    local target_node = si_target:get_associated_proxy ("node")
    if target_node.properties["media.class"] == target_media_class then
      return si_target
    end
  end
  return nil
end

function findUndefinedTarget (si_ep)
  local media_class = si_ep.properties["media.class"]
  local target_class_assoc = {
    ["Audio/Source"] = "Audio/Source",
    ["Stream/Output/Audio"] = "Audio/Sink",
    ["Audio/Sink"] = "Audio/Sink",
    ["Video/Source"] = "Video/Source",
  }
  local target_media_class = target_class_assoc[media_class]
  if not target_media_class then
    return nil
  end

  local si_target = findFilterTarget (si_ep.properties)
  if not si_target then
    si_target = findTargetByDefaultNode (target_media_class)
  end
  if not si_target then
    si_target = findTargetByFirstAvailable (target_media_class)
  end
  return si_target
end

function createLink (si_ep, si_target)
  local out_item = nil
  local in_item = nil
  local ep_props = si_ep.properties
  local target_props = si_target.properties

  if target_props["item.node.direction"] == "input" then
    -- playback
    out_item = si_ep
    in_item = si_target
  else
    -- capture
    in_item = si_ep
    out_item = si_target
  end

  local link_string = string.format("link %s <-> %s ",
    (is_filter and ep_props["node.name"] or ep_props["name"]),
    target_props["node.name"])

  Log.info(si_link, link_string)

  -- create and configure link
  local si_link = SessionItem ( "si-standard-link" )
  if not si_link:configure {
    ["out.item"] = out_item,
    ["in.item"] = in_item,
    ["out.item.port.context"] = "output",
    ["in.item.port.context"] = "input",
    ["is.policy.endpoint.device.link"] = true,
  } then
    Log.warning (si_link, "failed to configure si-standard-link")
    return
  end

  -- register
  si_link:register ()

  Log.info (si_link, " activating link " .. link_string)

  -- activate
  si_link:activate (Feature.SessionItem.ACTIVE, function (l, e)
    if e then
      Log.warning (l, "failed to activate link: " .. link_string .. tostring(e))
      l:remove ()
    else
      Log.info (l, "activated link " .. link_string)
    end
  end)
end

function handleFilter(filter)
  handleLinkable(filter)
end

function handleLinkable (si)
  local si_props = si.properties
  local is_filter = (si_props["node.link-group"] ~= nil)
  if is_filter then
    Log.info (si, "handling filter " .. si_props["node.name"])
  else
    Log.info (si, "handling endpoint " .. si_props["name"])
  end

  -- find proper target item
  local si_target = findUndefinedTarget (si)
  if not si_target then
    Log.info (si, "... target item not found")
    return
  end

  -- Check if item is linked to proper target, otherwise re-link
  for link in links_om:iterate() do
    local out_id = tonumber(link.properties["out.item.id"])
    local in_id = tonumber(link.properties["in.item.id"])
    if out_id == si.id or in_id == si.id then
      local is_out = out_id == si.id and true or false
      for peer in linkables_om:iterate() do
        if peer.id == (is_out and in_id or out_id) then

          if peer.id == si_target.id then
            Log.info (si, "... already linked to proper target")
            return
          end

          -- remove old link if active, otherwise schedule rescan
          if ((link:get_active_features() & Feature.SessionItem.ACTIVE) ~= 0) then
            link:remove ()
            Log.info (si, "... moving to new target")
          else
            scheduleRescan ()
            Log.info (si, "... scheduled rescan")
            return
          end

        end
      end
    end
  end

  -- create new link
  createLink (si, si_target)
end

function unhandleLinkable (si)
  si_props = si.properties

  Log.info (si, string.format("unhandling item: %s (%s)",
      tostring(si_props["node.name"]), tostring(si_props["node.id"])))

  -- remove any links associated with this item
  for silink in links_om:iterate() do
    local out_id = tonumber (silink.properties["out.item.id"])
    local in_id = tonumber (silink.properties["in.item.id"])
    if out_id == si.id or in_id == si.id then
      silink:remove ()
      Log.info (silink, "... link removed")
    end
  end
end

default_nodes = Plugin.find("default-nodes-api")
endpoints_om = ObjectManager { Interest { type = "SiEndpoint" }}
linkables_om = ObjectManager {
  Interest {
    type = "SiLinkable",
    -- only handle device si-audio-adapter items
    Constraint { "item.factory.name", "=", "si-audio-adapter", type = "pw-global" },
    Constraint { "item.node.type", "=", "device", type = "pw-global" },
    Constraint { "active-features", "!", 0, type = "gobject" },
  }
}
streams_om = ObjectManager {
  Interest {
    type = "SiLinkable",
    -- only handle stream si-audio-adapter items
    Constraint { "item.factory.name", "=", "si-audio-adapter", type = "pw-global" },
    Constraint { "active-features", "!", 0, type = "gobject" },
    Constraint { "media.class", "=", "Stream/Output/Audio" },
  }
}
links_om = ObjectManager {
  Interest {
    type = "SiLink",
    -- only handle links created by this policy
    Constraint { "is.policy.endpoint.device.link", "=", true, type = "pw-global" },
  }
}

-- listen for default node changes if config.follow is enabled
if config.follow then
  default_nodes:connect("changed", function (p)
    scheduleRescan ()
  end)
end

linkables_om:connect("objects-changed", function (om)
  scheduleRescan ()
end)

endpoints_om:connect("object-added", function (om)
  scheduleRescan ()
end)

linkables_om:connect("object-removed", function (om, si)
  unhandleLinkable (si)
end)

endpoints_om:activate()
linkables_om:activate()
links_om:activate()
streams_om:activate()
