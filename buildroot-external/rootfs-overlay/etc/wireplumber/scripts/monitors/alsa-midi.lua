-- WirePlumber
--
-- Copyright © 2021 Collabora Ltd.
--    @author Julian Bouzas <julian.bouzas@collabora.com>
--
-- SPDX-License-Identifier: MIT

-- Receive script arguments from config.lua
local config = ... or {}

-- ensure config.properties is not nil
config.properties = config.properties or {}

SND_PATH = "/dev/snd"
SEQ_NAME = "seq"
SND_SEQ_PATH = SND_PATH .. "/" .. SEQ_NAME

midi_node = nil
fm_plugin = nil

function CreateMidiNode ()
  -- Midi properties
  local props = {}
  if type(config.properties["alsa.midi.node-properties"]) == "table" then
     props = config.properties["alsa.midi.node-properties"]
  end
  props["factory.name"] = "api.alsa.seq.bridge"
  props["node.name"] = props["node.name"] or "Midi-Bridge"

  -- create the midi node
  local node = Node("spa-node-factory", props)
  node:activate(Feature.Proxy.BOUND, function (n)
    Log.info ("activated Midi bridge")
  end)

  return node;
end

if GLib.access (SND_SEQ_PATH, "rw") then
  midi_node = CreateMidiNode ()
elseif config.properties["alsa.midi.monitoring"] then
  fm_plugin = Plugin.find("file-monitor-api")
end

-- Only monitor the MIDI device if file does not exist and plugin API is loaded
if midi_node == nil and fm_plugin ~= nil then
  -- listen for changed events
  fm_plugin:connect ("changed", function (o, file, old, evtype)
    -- files attributes changed
    if evtype == "attribute-changed" then
      if file ~= SND_SEQ_PATH then
        return
      end
      if midi_node == nil and GLib.access (SND_SEQ_PATH, "rw") then
        midi_node = CreateMidiNode ()
        fm_plugin:call ("remove-watch", SND_PATH)
      end
    end

    -- directory is going to be unmounted
    if evtype == "pre-unmount" then
      fm_plugin:call ("remove-watch", SND_PATH)
    end
  end)

  -- add watch
  fm_plugin:call ("add-watch", SND_PATH, "m")
end
