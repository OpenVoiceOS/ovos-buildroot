-- WirePlumber
--
-- Copyright © 2023 Collabora Ltd.
--    @author George Kiagiadakis <george.kiagiadakis@collabora.com>
--
-- SPDX-License-Identifier: MIT
--
-- The script exposes a metadata object named "sm-objects" that clients can
-- use to load objects into the WirePlumber daemon process. The objects are
-- loaded as soon as the metadata is set and are destroyed when the metadata
-- is cleared.
--
-- To load an object, a client needs to set a metadata entry with:
--
--   * subject:
--  The ID of the owner of the object; you can use 0 here, but the
--  idea is to be able to restrict which clients can change and/or
--  delete these objects by using IDs of other objects appropriately
--
--   * key: "<UNIQUE-OBJECT-NAME>"
--  This is the name that will be used to identify the object.
--  If an object with the same name already exists, it will be destroyed.
--  Note that the keys are unique per subject, so you can have multiple
--  objects with the same name as long as they are owned by different subjects.
--
--   * type: "Spa:String:JSON"
--
--   * value: "{ type = <object-type>,
--               name = <object-name>,
--               args = { ...object arguments... } }"
--  The object type can be one of the following:
--   - "pw-module": loads a pipewire module: `name` and `args` are interpreted
--                  just like a module entry in pipewire.conf
--   - "metadata": loads a metadata object with `metadata.name` = `name`
--                 and any additional properties provided in `args`
--

on_demand_objects = {}

object_constructors = {
  ["pw-module"] = LocalModule,
  ["metadata"] = function (name, args)
    local m = ImplMetadata (name, args)
    m:activate (Features.ALL, function (m, e)
      if e then
        Log.warning ("failed to activate on-demand metadata `" .. name .. "`: " .. tostring (e))
      end
    end)
    return m
  end
}

function handle_metadata_changed (m, subject, key, type, value)
  -- destroy all objects when metadata is cleared
  if not key then
    on_demand_objects = {}
    return
  end

  local object_id = key .. "@" .. tostring(subject)

  -- destroy existing object instance, if needed
  if on_demand_objects[object_id] then
    Log.debug("destroy on-demand object: " .. object_id)
    on_demand_objects[object_id] = nil
  end

  if value then
    local json = Json.Raw(value)
    if not json:is_object() then
      Log.warning("loading '".. object_id .. "' failed: expected JSON object, got: '" .. value .. "'")
      return
    end

    local obj = json:parse(1)
    if not obj.type then
      Log.warning("loading '".. object_id .. "' failed: no object type specified")
      return
    end
    if not obj.name then
      Log.warning("loading '".. object_id .. "' failed: no object name specified")
      return
    end

    local constructor = object_constructors[obj.type]
    if not constructor then
      Log.warning("loading '".. object_id .. "' failed: unknown object type: " .. obj.type)
      return
    end

    Log.info("load on-demand object: " .. object_id .. " -> " .. obj.name)
    on_demand_objects[object_id] = constructor(obj.name, obj.args)
  end
end

objects_metadata = ImplMetadata ("sm-objects")
objects_metadata:activate (Features.ALL, function (m, e)
  if e then
    Log.warning ("failed to activate the sm-objects metadata: " .. tostring (e))
  else
    m:connect("changed", handle_metadata_changed)
  end
end)
