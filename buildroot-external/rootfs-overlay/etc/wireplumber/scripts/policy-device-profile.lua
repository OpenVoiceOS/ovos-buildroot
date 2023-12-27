-- WirePlumber
--
-- Copyright © 2022 Collabora Ltd.
--    @author Julian Bouzas <julian.bouzas@collabora.com>
--
-- SPDX-License-Identifier: MIT

local self = {}
self.config = ... or {}
self.config.persistent = self.config.persistent or {}
self.config.priorities = self.config.priorities or {}
self.active_profiles = {}
self.default_profile_plugin = Plugin.find("default-profile")

function createIntrestObjects(t)
  for _, p in ipairs(t or {}) do
    p.interests = {}
    for _, i in ipairs(p.matches) do
      local interest_desc = { type = "properties" }
      for _, c in ipairs(i) do
        c.type = "pw"
        table.insert(interest_desc, Constraint(c))
      end
      local interest = Interest(interest_desc)
      table.insert(p.interests, interest)
    end
    p.matches = nil
  end
end

-- Preprocess persistent profiles and create Interest objects
createIntrestObjects(self.config.persistent)
-- Preprocess profile priorities and create Interest objects
createIntrestObjects(self.config.priorities)

-- Checks whether a device profile is persistent or not
function isProfilePersistent(device_props, profile_name)
  for _, p in ipairs(self.config.persistent or {}) do
    if p.profile_names then
      for _, interest in ipairs(p.interests) do
        if interest:matches(device_props) then
          for _, pn in ipairs(p.profile_names) do
            if pn == profile_name then
              return true
            end
          end
        end
      end
    end
  end
  return false
end

function parseParam(param, id)
  local parsed = param:parse()
  if parsed.pod_type == "Object" and parsed.object_id == id then
    return parsed.properties
  else
    return nil
  end
end

function setDeviceProfile (device, dev_id, dev_name, profile)
  if self.active_profiles[dev_id] and
      self.active_profiles[dev_id].index == profile.index then
    Log.info ("Profile " .. profile.name .. " is already set in " .. dev_name)
    return
  end

  local param = Pod.Object {
    "Spa:Pod:Object:Param:Profile", "Profile",
    index = profile.index,
  }
  Log.info ("Setting profile " .. profile.name .. " on " .. dev_name)
  device:set_param("Profile", param)
end

function findDefaultProfile (device)
  local def_name = nil

  if self.default_profile_plugin ~= nil then
    def_name = self.default_profile_plugin:call ("get-profile", device)
  end
  if def_name == nil then
    return nil
  end

  for p in device:iterate_params("EnumProfile") do
    local profile = parseParam(p, "EnumProfile")
    if profile.name == def_name then
      return profile
    end
  end

  return nil
end

-- returns the priorities, if defined
function getDevicePriorities(device_props, profile_name)
  for _, p in ipairs(self.config.priorities or {}) do
    for _, interest in ipairs(p.interests) do
      if interest:matches(device_props) then
        return p.priorities
      end
    end
  end

  return nil
end

-- find profiles based on user preferences.
function findPreferredProfile(device)
  local priority_table = getDevicePriorities(device.properties)

  if not priority_table or #priority_table == 0 then
    return nil
  else
    Log.info("priority table found for device " ..
      device.properties["device.name"])
  end

  for _, priority_profile in ipairs(priority_table) do
    for p in device:iterate_params("EnumProfile") do
      device_profile = parseParam(p, "EnumProfile")
      if device_profile.name == priority_profile then
        Log.info("Selected user preferred profile " ..
          device_profile.name .. " for " .. device.properties["device.name"])
        return device_profile
      end
    end
  end

  return nil
end

-- find profiles based on inbuilt priorities.
function findBestProfile(device)
  -- Takes absolute priority if available or unknown
  local profile_prop = device.properties["device.profile"]
  local off_profile = nil
  local best_profile = nil
  local unk_profile = nil
  local profile = nil

  for p in device:iterate_params("EnumProfile") do
    profile = parseParam(p, "EnumProfile")
    if profile and profile.name == profile_prop and profile.available ~= "no" then
      return profile
    elseif profile and profile.name ~= "pro-audio" then
      if profile.name == "off" then
        off_profile = profile
      elseif profile.available == "yes" then
        if best_profile == nil or profile.priority > best_profile.priority then
          best_profile = profile
        end
      elseif profile.available ~= "no" then
        if unk_profile == nil or profile.priority > unk_profile.priority then
          unk_profile = profile
        end
      end
    end
  end

  if best_profile ~= nil then
    profile = best_profile
  elseif unk_profile ~= nil then
    profile = unk_profile
  elseif off_profile ~= nil then
    profile = off_profile
  end

  if profile ~= nil then
    Log.info("Found best profile " .. profile.name .. " for " .. device.properties["device.name"])
    return profile
  else
    return nil
  end
end

function handleProfiles (device, new_device)
  local dev_id = device["bound-id"]
  local dev_name = device.properties["device.name"]

  local def_profile = findDefaultProfile (device)

  -- Do not do anything if active profile is both persistent and default
  if not new_device and
      self.active_profiles[dev_id] ~= nil and
      isProfilePersistent (device.properties, self.active_profiles[dev_id].name) and
      def_profile ~= nil and
      self.active_profiles[dev_id].name == def_profile.name
      then
    local active_profile = self.active_profiles[dev_id].name
    Log.info ("Device profile " .. active_profile .. " is persistent for " .. dev_name)
    return
  end

  if def_profile ~= nil then
    if def_profile.available == "no" then
      Log.info ("Default profile " .. def_profile.name .. " unavailable for " .. dev_name)
    else
      Log.info ("Found default profile " .. def_profile.name .. " for " .. dev_name)
      setDeviceProfile (device, dev_id, dev_name, def_profile)
      return
    end
  else
    Log.info ("Default profile not found for " .. dev_name)
  end

  local best_profile = findPreferredProfile(device)

  if not best_profile then
    best_profile = findBestProfile(device)
  end

  if best_profile ~= nil then
    setDeviceProfile (device, dev_id, dev_name, best_profile)
  else
    Log.info ("Best profile not found on " .. dev_name)
  end
end

function onDeviceParamsChanged (device, param_name)
  if param_name == "EnumProfile" then
    handleProfiles (device, false)
  end
end

self.om = ObjectManager {
  Interest {
    type = "device",
    Constraint { "device.name", "is-present", type = "pw-global" },
  }
}

self.om:connect("object-added", function (_, device)
  device:connect ("params-changed", onDeviceParamsChanged)
  handleProfiles (device, true)
end)

self.om:connect("object-removed", function (_, device)
  local dev_id = device["bound-id"]
  self.active_profiles[dev_id] = nil
end)

self.om:activate()
