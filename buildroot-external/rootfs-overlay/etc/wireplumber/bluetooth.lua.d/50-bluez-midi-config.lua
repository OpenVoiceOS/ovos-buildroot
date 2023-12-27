-- BLE MIDI is currently disabled by default, because it conflicts with
-- the SELinux policy on Fedora 37 and potentially other systems using
-- SELinux. For a workaround, see
-- https://gitlab.freedesktop.org/pipewire/pipewire/-/blob/master/spa/plugins/bluez5/README-MIDI.md
bluez_midi_monitor.enabled = false

bluez_midi_monitor.properties = {
  -- Enable the logind module, which arbitrates which user will be allowed
  -- to have bluetooth audio enabled at any given time (particularly useful
  -- if you are using GDM as a display manager, as the gdm user also launches
  -- pipewire and wireplumber).
  -- This requires access to the D-Bus user session; disable if you are running
  -- a system-wide instance of wireplumber.
  ["with-logind"] = true,

  -- List of MIDI server node names. Each node name given will create a new instance
  -- of a BLE MIDI service. Typical BLE MIDI instruments have on service instance,
  -- so adding more than one here may confuse some clients. The node property matching
  -- rules below apply also to these servers.
  --["servers"] = { "bluez_midi.server" },
}

bluez_midi_monitor.rules = {
  -- An array of matches/actions to evaluate.
  {
    matches = {
      {
        -- Matches all nodes.
        { "node.name", "matches", "bluez_midi.*" },
      },
    },
    apply_properties = {
      --["node.nick"] = "My Node",
      --["priority.driver"] = 100,
      --["priority.session"] = 100,
      --["node.pause-on-idle"] = false,
      --["session.suspend-timeout-seconds"] = 5,  -- 0 disables suspend
      --["monitor.channel-volumes"] = false,
      --["node.latency-offset-msec"] = -10,  -- delay (<0) input to reduce jitter
    },
  },
}
