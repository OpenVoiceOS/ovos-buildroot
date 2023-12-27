-- WirePlumber
--
-- Copyright © 2021 Asymptotic Inc.
--    @author Sanchayan Maity <sanchayan@asymptotic.io>
--
-- Based on bt-profile-switch.lua in tests/examples
-- Copyright © 2021 George Kiagiadakis
--
-- Based on bluez-autoswitch in media-session
-- Copyright © 2021 Pauli Virtanen
--
-- SPDX-License-Identifier: MIT
--
-- Checks for the existence of media.role and if present switches the bluetooth
-- profile accordingly. Also see bluez-autoswitch in media-session.
-- The intended logic of the script is as follows.
--
-- When a stream comes in, if it has a Communication or phone role in PulseAudio
-- speak in props, we switch to the highest priority profile that has an Input
-- route available. The reason for this is that we may have microphone enabled
-- non-HFP codecs eg. Faststream.
-- We track the incoming streams with Communication role or the applications
-- specified which do not set the media.role correctly perhaps.
-- When a stream goes away if the list with which we track the streams above
-- is empty, then we revert back to the old profile.

local config = ...
local use_persistent_storage = config["use-persistent-storage"] or false
local applications = {}
local use_headset_profile = config["media-role.use-headset-profile"] or false
local profile_restore_timeout_msec = 2000

local INVALID = -1
local timeout_source = nil
local restore_timeout_source = nil

local state = use_persistent_storage and State("policy-bluetooth") or nil
local headset_profiles = state and state:load() or {}
local last_profiles = {}

local active_streams = {}
local previous_streams = {}

for _, value in ipairs(config["media-role.applications"] or {}) do
  applications[value] = true
end

metadata_om = ObjectManager {
  Interest {
    type = "metadata",
    Constraint { "metadata.name", "=", "default" },
  }
}

devices_om = ObjectManager {
  Interest {
    type = "device",
    Constraint { "device.api", "=", "bluez5" },
  }
}

streams_om = ObjectManager {
  Interest {
    type = "node",
    Constraint { "media.class", "matches", "Stream/Input/Audio", type = "pw-global" },
    -- Do not consider monitor streams
    Constraint { "stream.monitor", "!", "true" }
  }
}

local function parseParam(param_to_parse, id)
  local param = param_to_parse:parse()
  if param.pod_type == "Object" and param.object_id == id then
    return param.properties
  else
    return nil
  end
end

local function storeAfterTimeout()
  if not use_persistent_storage then
    return
  end

  if timeout_source then
    timeout_source:destroy()
  end
  timeout_source = Core.timeout_add(1000, function ()
    local saved, err = state:save(headset_profiles)
    if not saved then
      Log.warning(err)
    end
    timeout_source = nil
  end)
end

local function saveHeadsetProfile(device, profile_name)
  local key = "saved-headset-profile:" .. device.properties["device.name"]
  headset_profiles[key] = profile_name
  storeAfterTimeout()
end

local function getSavedHeadsetProfile(device)
  local key = "saved-headset-profile:" .. device.properties["device.name"]
  return headset_profiles[key]
end

local function saveLastProfile(device, profile_name)
  last_profiles[device.properties["device.name"]] = profile_name
end

local function getSavedLastProfile(device)
  return last_profiles[device.properties["device.name"]]
end

local function isSwitched(device)
  return getSavedLastProfile(device) ~= nil
end

local function isBluez5AudioSink(sink_name)
  if sink_name and string.find(sink_name, "bluez_output.") ~= nil then
    return true
  end
  return false
end

local function isBluez5DefaultAudioSink()
  local metadata = metadata_om:lookup()
  local default_audio_sink = metadata:find(0, "default.audio.sink")
  return isBluez5AudioSink(default_audio_sink)
end

local function findProfile(device, index, name)
  for p in device:iterate_params("EnumProfile") do
    local profile = parseParam(p, "EnumProfile")
    if not profile then
      goto skip_enum_profile
    end

    Log.debug("Profile name: " .. profile.name .. ", priority: "
              .. tostring(profile.priority) .. ", index: " .. tostring(profile.index))
    if (index ~= nil and profile.index == index) or
        (name ~= nil and profile.name == name) then
      return profile.priority, profile.index, profile.name
    end

    ::skip_enum_profile::
  end

  return INVALID, INVALID, nil
end

local function getCurrentProfile(device)
  for p in device:iterate_params("Profile") do
    local profile = parseParam(p, "Profile")
    if profile then
      return profile.name
    end
  end

  return nil
end

local function highestPrioProfileWithInputRoute(device)
  local profile_priority = INVALID
  local profile_index = INVALID
  local profile_name = nil

  for p in device:iterate_params("EnumRoute") do
    local route = parseParam(p, "EnumRoute")
    -- Parse pod
    if not route then
      goto skip_enum_route
    end

    if route.direction ~= "Input" then
      goto skip_enum_route
    end

    Log.debug("Route with index: " .. tostring(route.index) .. ", direction: "
          .. route.direction .. ", name: " .. route.name .. ", description: "
          .. route.description .. ", priority: " .. route.priority)
    if route.profiles then
      for _, v in pairs(route.profiles) do
        local priority, index, name = findProfile(device, v)
        if priority ~= INVALID then
          if profile_priority < priority then
            profile_priority = priority
            profile_index = index
            profile_name = name
          end
        end
      end
    end

    ::skip_enum_route::
  end

  return profile_priority, profile_index, profile_name
end

local function hasProfileInputRoute(device, profile_index)
  for p in device:iterate_params("EnumRoute") do
    local route = parseParam(p, "EnumRoute")
    if route and route.direction == "Input" and route.profiles then
      for _, v in pairs(route.profiles) do
        if v == profile_index then
          return true
        end
      end
    end
  end
  return false
end

local function switchProfile()
  local index
  local name

  if restore_timeout_source then
    restore_timeout_source:destroy()
    restore_timeout_source = nil
  end

  for device in devices_om:iterate() do
    if isSwitched(device) then
      goto skip_device
    end

    local cur_profile_name = getCurrentProfile(device)
    saveLastProfile(device, cur_profile_name)

    _, index, name = findProfile(device, nil, cur_profile_name)
    if hasProfileInputRoute(device, index) then
      Log.info("Current profile has input route, not switching")
      goto skip_device
    end

    local saved_headset_profile = getSavedHeadsetProfile(device)
    index = INVALID
    if saved_headset_profile then
      _, index, name = findProfile(device, nil, saved_headset_profile)
    end
    if index == INVALID then
      _, index, name = highestPrioProfileWithInputRoute(device)
    end

    if index ~= INVALID then
      local pod = Pod.Object {
        "Spa:Pod:Object:Param:Profile", "Profile",
        index = index
      }

      Log.info("Setting profile of '"
            .. device.properties["device.description"]
            .. "' from: " .. cur_profile_name
            .. " to: " .. name)
      device:set_params("Profile", pod)
    else
      Log.warning("Got invalid index when switching profile")
    end

    ::skip_device::
  end
end

local function restoreProfile()
  for device in devices_om:iterate() do
    if isSwitched(device) then
      local profile_name = getSavedLastProfile(device)
      local cur_profile_name = getCurrentProfile(device)

      saveLastProfile(device, nil)

      if cur_profile_name then
        Log.info("Setting saved headset profile to: " .. cur_profile_name)
        saveHeadsetProfile(device, cur_profile_name)
      end

      if profile_name then
        local _, index, name = findProfile(device, nil, profile_name)

        if index ~= INVALID then
          local pod = Pod.Object {
            "Spa:Pod:Object:Param:Profile", "Profile",
            index = index
          }

          Log.info("Restoring profile of '"
                .. device.properties["device.description"]
                .. "' from: " .. cur_profile_name
                .. " to: " .. name)
          device:set_params("Profile", pod)
        else
          Log.warning("Failed to restore profile")
        end
      end
    end
  end
end

local function triggerRestoreProfile()
  if restore_timeout_source then
    return
  end
  if next(active_streams) ~= nil then
    return
  end
  restore_timeout_source = Core.timeout_add(profile_restore_timeout_msec, function ()
    restore_timeout_source = nil
    restoreProfile()
  end)
end

-- We consider a Stream of interest to have role Communication if it has
-- media.role set to Communication in props or it is in our list of
-- applications as these applications do not set media.role correctly or at
-- all.
local function checkStreamStatus(stream)
  local app_name = stream.properties["application.name"]
  local stream_role = stream.properties["media.role"]

  if not (stream_role == "Communication" or applications[app_name]) then
    return false
  end
  if not isBluez5DefaultAudioSink() then
    return false
  end

  -- If a stream we previously saw stops running, we consider it
  -- inactive, because some applications (Teams) just cork input
  -- streams, but don't close them.
  if previous_streams[stream["bound-id"]] and stream.state ~= "running" then
    return false
  end

  return true
end

local function handleStream(stream)
  if not use_headset_profile then
    return
  end

  if checkStreamStatus(stream) then
    active_streams[stream["bound-id"]] = true
    previous_streams[stream["bound-id"]] = true
    switchProfile()
  else
    active_streams[stream["bound-id"]] = nil
    triggerRestoreProfile()
  end
end

local function handleAllStreams()
  for stream in streams_om:iterate {
    Constraint { "media.class", "matches", "Stream/Input/Audio", type = "pw-global" },
    Constraint { "stream.monitor", "!", "true" }
  } do
    handleStream(stream)
  end
end

streams_om:connect("object-added", function (_, stream)
  stream:connect("state-changed", function (stream, old_state, cur_state)
    handleStream(stream)
  end)
  stream:connect("params-changed", handleStream)
  handleStream(stream)
end)

streams_om:connect("object-removed", function (_, stream)
  active_streams[stream["bound-id"]] = nil
  previous_streams[stream["bound-id"]] = nil
  triggerRestoreProfile()
end)

devices_om:connect("object-added", function (_, device)
  -- Devices are unswitched initially
  if isSwitched(device) then
    saveLastProfile(device, nil)
  end
  handleAllStreams()
end)

metadata_om:connect("object-added", function (_, metadata)
  metadata:connect("changed", function (m, subject, key, t, value)
    if (use_headset_profile and subject == 0 and key == "default.audio.sink"
        and isBluez5AudioSink(value)) then
      -- If bluez sink is set as default, rescan for active input streams
      handleAllStreams()
    end
  end)
end)

metadata_om:activate()
devices_om:activate()
streams_om:activate()
