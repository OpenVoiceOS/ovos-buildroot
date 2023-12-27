-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author George Kiagiadakis <george.kiagiadakis@collabora.com>
--
-- Based on restore-stream.c from pipewire-media-session
-- Copyright © 2020 Wim Taymans
--
-- SPDX-License-Identifier: MIT

-- Receive script arguments from config.lua
local config = ... or {}
config.properties = config.properties or {}
config_restore_props = config.properties["restore-props"] or false
config_restore_target = config.properties["restore-target"] or false
config_default_channel_volume = config.properties["default-channel-volume"] or 1.0

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

-- the state storage
state = State("restore-stream")
state_table = state:load()

-- simple serializer {"foo", "bar"} -> "foo;bar;"
function serializeArray(a)
  local str = ""
  for _, v in ipairs(a) do
    str = str .. tostring(v):gsub(";", "\\;") .. ";"
  end
  return str
end

-- simple deserializer "foo;bar;" -> {"foo", "bar"}
function parseArray(str, convert_value, with_type)
  local array = {}
  local val = ""
  local escaped = false
  for i = 1, #str do
    local c = str:sub(i,i)
    if c == '\\' then
      escaped = true
    elseif c == ';' and not escaped then
      val = convert_value and convert_value(val) or val
      table.insert(array, val)
      val = ""
    else
      val = val .. tostring(c)
      escaped = false
    end
  end
  if with_type then
    array["pod_type"] = "Array"
  end
  return array
end

function parseParam(param, id)
  local route = param:parse()
  if route.pod_type == "Object" and route.object_id == id then
    return route.properties
  else
    return nil
  end
end

function storeAfterTimeout()
  if timeout_source then
    timeout_source:destroy()
  end
  timeout_source = Core.timeout_add(1000, function ()
    local saved, err = state:save(state_table)
    if not saved then
      Log.warning(err)
    end
    timeout_source = nil
  end)
end

function findSuitableKey(properties)
  local keys = {
    "media.role",
    "application.id",
    "application.name",
    "media.name",
    "node.name",
  }
  local key = nil

  for _, k in ipairs(keys) do
    local p = properties[k]
    if p then
      key = string.format("%s:%s:%s",
          properties["media.class"]:gsub("^Stream/", ""), k, p)
      break
    end
  end
  return key
end

function saveTarget(subject, target_key, type, value)
  if target_key ~= "target.node" and target_key ~= "target.object" then
    return
  end

  local node = streams_om:lookup {
    Constraint { "bound-id", "=", subject, type = "gobject" }
  }
  if not node then
    return
  end

  local stream_props = node.properties
  rulesApplyProperties(stream_props)

  if stream_props["state.restore-target"] == false then
    return
  end

  local key_base = findSuitableKey(stream_props)
  if not key_base then
    return
  end

  local target_value = value
  local target_name = nil

  if not target_value then
    local metadata = metadata_om:lookup()
    if metadata then
      target_value = metadata:find(node["bound-id"], target_key)
    end
  end
  if target_value and target_value ~= "-1" then
    local target_node
    if target_key == "target.object" then
      target_node = allnodes_om:lookup {
        Constraint { "object.serial", "=", target_value, type = "pw-global" }
      }
    else
      target_node = allnodes_om:lookup {
        Constraint { "bound-id", "=", target_value, type = "gobject" }
      }
    end
    if target_node then
      target_name = target_node.properties["node.name"]
    end
  end
  state_table[key_base .. ":target"] = target_name

  Log.info(node, "saving stream target for " ..
    tostring(stream_props["node.name"]) ..
    " -> " .. tostring(target_name))

  storeAfterTimeout()
end

function restoreTarget(node, target_name)

  local stream_props = node.properties
  local target_in_props = nil

  if stream_props ["target.object"] ~= nil or
      stream_props ["node.target"] ~= nil then
    target_in_props = stream_props ["target.object"] or
        stream_props ["node.target"]

    Log.debug (string.format ("%s%s%s%s",
      "Not restoring the target for ",
      stream_props ["node.name"],
      " because it is already set to ",
      target_in_props))

    return
  end

  local target_node = allnodes_om:lookup {
    Constraint { "node.name", "=", target_name, type = "pw" }
  }

  if target_node then
    local metadata = metadata_om:lookup()
    if metadata then
      metadata:set(node["bound-id"], "target.node", "Spa:Id",
          target_node["bound-id"])
    end
  end
end

function jsonTable(val, name)
  local tmp = ""
  local count = 0

  if name then tmp = tmp .. string.format("%q", name) .. ": " end

  if type(val) == "table" then
    if val["pod_type"] == "Array" then
      tmp = tmp .. "["
      for _, v in ipairs(val) do
	if count > 0 then tmp = tmp .. "," end
        tmp = tmp .. jsonTable(v)
	count = count + 1
      end
      tmp = tmp .. "]"
    else
      tmp = tmp .. "{"
      for k, v in pairs(val) do
	if count > 0 then tmp = tmp .. "," end
        tmp = tmp .. jsonTable(v, k)
	count = count + 1
      end
      tmp = tmp .. "}"
    end
  elseif type(val) == "number" then
    tmp = tmp .. tostring(val)
  elseif type(val) == "string" then
    tmp = tmp .. string.format("%q", val)
  elseif type(val) == "boolean" then
    tmp = tmp .. (val and "true" or "false")
  else
    tmp = tmp .. "\"[type:" .. type(val) .. "]\""
  end
  return tmp
end

function moveToMetadata(key_base, metadata)
  local route_table = { }
  local count = 0

  key = "restore.stream." .. key_base
  key = string.gsub(key, ":", ".", 1);

  local str = state_table[key_base .. ":volume"]
  if str then
    route_table["volume"] = tonumber(str)
    count = count + 1;
  end
  local str = state_table[key_base .. ":mute"]
  if str then
    route_table["mute"] = str == "true"
    count = count + 1;
  end
  local str = state_table[key_base .. ":channelVolumes"]
  if str then
    route_table["volumes"] = parseArray(str, tonumber, true)
    count = count + 1;
  end
  local str = state_table[key_base .. ":channelMap"]
  if str then
    route_table["channels"] = parseArray(str, nil, true)
    count = count + 1;
  end

  if count > 0 then
    metadata:set(0, key, "Spa:String:JSON", jsonTable(route_table));
  end
end


function saveStream(node)
  local stream_props = node.properties
  rulesApplyProperties(stream_props)

  if config_restore_props and stream_props["state.restore-props"] ~= false then
    local key_base = findSuitableKey(stream_props)
    if not key_base then
      return
    end

    Log.info(node, "saving stream props for " ..
        tostring(stream_props["node.name"]))

    for p in node:iterate_params("Props") do
      local props = parseParam(p, "Props")
      if not props then
        goto skip_prop
      end

      if props.volume then
        state_table[key_base .. ":volume"] = tostring(props.volume)
      end
      if props.mute ~= nil then
        state_table[key_base .. ":mute"] = tostring(props.mute)
      end
      if props.channelVolumes then
        state_table[key_base .. ":channelVolumes"] = serializeArray(props.channelVolumes)
      end
      if props.channelMap then
        state_table[key_base .. ":channelMap"] = serializeArray(props.channelMap)
      end

      ::skip_prop::
    end

    storeAfterTimeout()
  end
end

function build_default_channel_volumes (node)
  local def_vol = config_default_channel_volume
  local channels = 2
  local res = {}

  local str = node.properties["state.default-channel-volume"]
  if str ~= nil then
    def_vol = tonumber (str)
  end

  for pod in node:iterate_params("Format") do
    local pod_parsed = pod:parse()
    if pod_parsed ~= nil then
      channels = pod_parsed.properties.channels
      break
    end
  end

  while (#res < channels) do
    table.insert(res, def_vol)
  end

  return res;
end

function restoreStream(node)
  local stream_props = node.properties
  rulesApplyProperties(stream_props)

  local key_base = findSuitableKey(stream_props)
  if not key_base then
    return
  end

  if config_restore_props and stream_props["state.restore-props"] ~= false then
    local props = { "Spa:Pod:Object:Param:Props", "Props" }

    local str = state_table[key_base .. ":volume"]
    props.volume = str and tonumber(str) or nil

    local str = state_table[key_base .. ":mute"]
    props.mute = str and (str == "true") or nil

    local str = state_table[key_base .. ":channelVolumes"]
    props.channelVolumes = str and parseArray(str, tonumber) or
        build_default_channel_volumes (node)

    local str = state_table[key_base .. ":channelMap"]
    props.channelMap = str and parseArray(str) or nil

    -- convert arrays to Spa Pod
    if props.channelVolumes then
      table.insert(props.channelVolumes, 1, "Spa:Float")
      props.channelVolumes = Pod.Array(props.channelVolumes)
    end
    if props.channelMap then
      table.insert(props.channelMap, 1, "Spa:Enum:AudioChannel")
      props.channelMap = Pod.Array(props.channelMap)
    end

    Log.info(node, "restore values from " .. key_base)
    local param = Pod.Object(props)
    Log.debug(param, "setting props on " .. tostring(node))
    node:set_param("Props", param)
  end

  if config_restore_target and stream_props["state.restore-target"] ~= false then
    local str = state_table[key_base .. ":target"]
    if str then
      restoreTarget(node, str)
    end
  end
end

if config_restore_target then
  metadata_om = ObjectManager {
    Interest {
      type = "metadata",
      Constraint { "metadata.name", "=", "default" },
    }
  }

  metadata_om:connect("object-added", function (om, metadata)
    -- process existing metadata
    for s, k, t, v in metadata:iterate(Id.ANY) do
      saveTarget(s, k, t, v)
    end
    -- and watch for changes
    metadata:connect("changed", function (m, subject, key, type, value)
      saveTarget(subject, key, type, value)
    end)
  end)
  metadata_om:activate()
end

function handleRouteSettings(subject, key, type, value)
  if type ~= "Spa:String:JSON" then
    return
  end
  if string.find(key, "^restore.stream.") == nil then
    return
  end
  if value == nil then
    return
  end
  local json = Json.Raw (value);
  if json == nil or not json:is_object () then
    return
  end

  local vparsed = json:parse()
  local key_base = string.sub(key, string.len("restore.stream.") + 1)
  local str;

  key_base = string.gsub(key_base, "%.", ":", 1);

  if vparsed.volume ~= nil then
    state_table[key_base .. ":volume"] = tostring (vparsed.volume)
  end
  if vparsed.mute ~= nil then
    state_table[key_base .. ":mute"] = tostring (vparsed.mute)
  end
  if vparsed.channels ~= nil then
    state_table[key_base .. ":channelMap"] = serializeArray (vparsed.channels)
  end
  if vparsed.volumes ~= nil then
    state_table[key_base .. ":channelVolumes"] = serializeArray (vparsed.volumes)
  end

  storeAfterTimeout()
end


rs_metadata = ImplMetadata("route-settings")
rs_metadata:activate(Features.ALL, function (m, e)
  if e then
    Log.warning("failed to activate route-settings metadata: " .. tostring(e))
    return
  end

  -- copy state into the metadata
  moveToMetadata("Output/Audio:media.role:Notification", m)
  -- watch for changes
  m:connect("changed", function (m, subject, key, type, value)
    handleRouteSettings(subject, key, type, value)
  end)
end)

allnodes_om = ObjectManager { Interest { type = "node" } }
allnodes_om:activate()

streams_om = ObjectManager {
  -- match stream nodes
  Interest {
    type = "node",
    Constraint { "media.class", "matches", "Stream/*", type = "pw-global" },
  },
  -- and device nodes that are not associated with any routes
  Interest {
    type = "node",
    Constraint { "media.class", "matches", "Audio/*", type = "pw-global" },
    Constraint { "device.routes", "is-absent", type = "pw" },
  },
  Interest {
    type = "node",
    Constraint { "media.class", "matches", "Audio/*", type = "pw-global" },
    Constraint { "device.routes", "equals", "0", type = "pw" },
  },
}
streams_om:connect("object-added", function (streams_om, node)
  node:connect("params-changed", saveStream)
  restoreStream(node)
end)
streams_om:activate()
