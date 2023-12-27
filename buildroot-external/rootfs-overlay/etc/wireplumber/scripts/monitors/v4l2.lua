-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author George Kiagiadakis <george.kiagiadakis@collabora.com>
--
-- SPDX-License-Identifier: MIT

local config = ... or {}

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

function findDuplicate(parent, id, property, value)
  for i = 0, id - 1, 1 do
    local obj = parent:get_managed_object(i)
    if obj and obj.properties[property] == value then
      return true
    end
  end
  return false
end

function createNode(parent, id, type, factory, properties)
  local dev_props = parent.properties

  -- set the device id and spa factory name; REQUIRED, do not change
  properties["device.id"] = parent["bound-id"]
  properties["factory.name"] = factory

  -- set the default pause-on-idle setting
  properties["node.pause-on-idle"] = false

  -- set the node name
  local name =
      (factory:find("sink") and "v4l2_output") or
       (factory:find("source") and "v4l2_input" or factory)
      .. "." ..
      (dev_props["device.name"]:gsub("^v4l2_device%.(.+)", "%1") or
       dev_props["device.name"] or
       dev_props["device.nick"] or
       dev_props["device.alias"] or
       "v4l2-device")
  -- sanitize name
  name = name:gsub("([^%w_%-%.])", "_")

  properties["node.name"] = name

  -- deduplicate nodes with the same name
  for counter = 2, 99, 1 do
    if findDuplicate(parent, id, "node.name", properties["node.name"]) then
      properties["node.name"] = name .. "." .. counter
    else
      break
    end
  end

  -- set the node description
  local desc = dev_props["device.description"] or "v4l2-device"
  desc = desc .. " (V4L2)"
  -- sanitize description, replace ':' with ' '
  properties["node.description"] = desc:gsub("(:)", " ")

  -- set the node nick
  local nick = properties["node.nick"] or
               dev_props["device.product.name"] or
               dev_props["api.v4l2.cap.card"] or
               dev_props["device.description"] or
               dev_props["device.nick"]
  properties["node.nick"] = nick:gsub("(:)", " ")

  -- set priority
  if not properties["priority.session"] then
    local path = properties["api.v4l2.path"] or "/dev/video100"
    local dev = path:gsub("/dev/video(%d+)", "%1")
    properties["priority.session"] = 1000 - (tonumber(dev) * 10)
  end

  -- apply properties from config.rules
  rulesApplyProperties(properties)
  if properties["node.disabled"] then
    return
  end

  -- create the node
  local node = Node("spa-node-factory", properties)
  node:activate(Feature.Proxy.BOUND)
  parent:store_managed_object(id, node)
end

function createDevice(parent, id, type, factory, properties)
  -- ensure the device has an appropriate name
  local name = "v4l2_device." ..
      (properties["device.name"] or
       properties["device.bus-id"] or
       properties["device.bus-path"] or
       tostring(id)):gsub("([^%w_%-%.])", "_")

  properties["device.name"] = name

  -- deduplicate devices with the same name
  for counter = 2, 99, 1 do
    if findDuplicate(parent, id, "device.name", properties["device.name"]) then
      properties["device.name"] = name .. "." .. counter
    else
      break
    end
  end

  -- ensure the device has a description
  properties["device.description"] =
      properties["device.description"]
      or properties["device.product.name"]
      or "Unknown device"

  -- apply properties from config.rules
  rulesApplyProperties(properties)
  if properties["device.disabled"] then
    return
  end

  -- create the device
  local device = SpaDevice(factory, properties)
  if device then
    device:connect("create-object", createNode)
    device:activate(Feature.SpaDevice.ENABLED | Feature.Proxy.BOUND)
    parent:store_managed_object(id, device)
  else
    Log.warning ("Failed to create '" .. factory .. "' device")
  end
end

monitor = SpaDevice("api.v4l2.enum.udev", config.properties or {})
if monitor then
  monitor:connect("create-object", createDevice)
  monitor:activate(Feature.SpaDevice.ENABLED)
else
  Log.message("PipeWire's V4L SPA missing or broken. Video4Linux not supported.")
end
