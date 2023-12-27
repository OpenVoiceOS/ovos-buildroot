-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author George Kiagiadakis <george.kiagiadakis@collabora.com>
--
-- SPDX-License-Identifier: MIT

local config = ... or {}
config.roles = config.roles or {}
config["duck.level"] = config["duck.level"] or 0.3

function findRole(role)
  if role and not config.roles[role] then
    for r, p in pairs(config.roles) do
      if type(p.alias) == "table" then
        for i = 1, #(p.alias), 1 do
          if role == p.alias[i] then
            return r
          end
        end
      end
    end
  end
  return role
end

function priorityForRole(role)
  local r = role and config.roles[role] or nil
  return r and r.priority or 0
end

function getAction(dominant_role, other_role)
  -- default to "mix" if the role is not configured
  if not dominant_role or not config.roles[dominant_role] then
    return "mix"
  end

  local role_config = config.roles[dominant_role]
  return role_config["action." .. other_role]
      or role_config["action.default"]
      or "mix"
end

function restoreVolume(role, media_class)
  if not mixer_api then return end

  local ep = endpoints_om:lookup {
    Constraint { "media.role", "=", role, type = "pw" },
    Constraint { "media.class", "=", media_class, type = "pw" },
  }

  if ep and ep.properties["node.id"] then
    Log.debug(ep, "restore role " .. role)
    mixer_api:call("set-volume", ep.properties["node.id"], {
      monitorVolume = 1.0,
    })
  end
end

function duck(role, media_class)
  if not mixer_api then return end

  local ep = endpoints_om:lookup {
    Constraint { "media.role", "=", role, type = "pw" },
    Constraint { "media.class", "=", media_class, type = "pw" },
  }

  if ep and ep.properties["node.id"] then
    Log.debug(ep, "duck role " .. role)
    mixer_api:call("set-volume", ep.properties["node.id"], {
      monitorVolume = config["duck.level"],
    })
  end
end

function getSuspendPlaybackMetadata ()
  local suspend = false
  local metadata = metadata_om:lookup()
  if metadata then
    local value = metadata:find(0, "suspend.playback")
    if value then
      suspend = value == "1" and true or false
    end
  end
  return suspend
end

function rescan()
  local links = {
    ["Audio/Source"] = {},
    ["Audio/Sink"] = {},
    ["Video/Source"] = {},
  }

  Log.info("Rescan endpoint links")

  -- deactivate all links if suspend playback metadata is present
  local suspend = getSuspendPlaybackMetadata()
  for silink in silinks_om:iterate() do
    if suspend then
      silink:deactivate(Feature.SessionItem.ACTIVE)
    end
  end

  -- gather info about links
  for silink in silinks_om:iterate() do
    local props = silink.properties
    local role = props["media.role"]
    local target_class = props["target.media.class"]
    local plugged = props["item.plugged.usec"]
    local active =
      ((silink:get_active_features() & Feature.SessionItem.ACTIVE) ~= 0)
    if links[target_class] then
      table.insert(links[target_class], {
        silink = silink,
        role = findRole(role),
        active = active,
        priority = priorityForRole(role),
        plugged = plugged and tonumber(plugged) or 0
      })
    end
  end

  local function compareLinks(l1, l2)
    return (l1.priority > l2.priority) or
        ((l1.priority == l2.priority) and (l1.plugged > l2.plugged))
  end

  for media_class, v in pairs(links) do
    -- sort on priority and stream creation time
    table.sort(v, compareLinks)

    -- apply actions
    local first_link = v[1]
    if first_link then
      for i = 2, #v, 1 do
        local action = getAction(first_link.role, v[i].role)
        if action == "cork" then
          if v[i].active then
            v[i].silink:deactivate(Feature.SessionItem.ACTIVE)
          end
        elseif action == "mix" then
          if not v[i].active and not suspend then
            v[i].silink:activate(Feature.SessionItem.ACTIVE, pendingOperation())
          end
          restoreVolume(v[i].role, media_class)
        elseif action == "duck" then
          if not v[i].active and not suspend then
            v[i].silink:activate(Feature.SessionItem.ACTIVE, pendingOperation())
          end
          duck(v[i].role, media_class)
        else
          Log.warning("Unknown action: " .. action)
        end
      end

      if not first_link.active and not suspend then
        first_link.silink:activate(Feature.SessionItem.ACTIVE, pendingOperation())
      end
      restoreVolume(first_link.role, media_class)
    end
  end
end

pending_ops = 0
pending_rescan = false

function pendingOperation()
  pending_ops = pending_ops + 1
  return function()
    pending_ops = pending_ops - 1
    if pending_ops == 0 and pending_rescan then
      pending_rescan = false
      rescan()
    end
  end
end

function maybeRescan()
  if pending_ops == 0 then
    rescan()
  else
    pending_rescan = true
  end
end

silinks_om = ObjectManager {
  Interest {
    type = "SiLink",
    Constraint { "is.policy.endpoint.client.link", "=", true },
  },
}
silinks_om:connect("objects-changed", maybeRescan)
silinks_om:activate()

-- enable ducking if mixer-api is loaded
mixer_api = Plugin.find("mixer-api")
if mixer_api then
  endpoints_om = ObjectManager {
    Interest { type = "endpoint" },
  }
  endpoints_om:activate()
end

metadata_om = ObjectManager {
  Interest {
    type = "metadata",
    Constraint { "metadata.name", "=", "default" },
  }
}
metadata_om:connect("object-added", function (om, metadata)
  metadata:connect("changed", function (m, subject, key, t, value)
    if key == "suspend.playback" then
      maybeRescan()
    end
  end)
end)
metadata_om:activate()
