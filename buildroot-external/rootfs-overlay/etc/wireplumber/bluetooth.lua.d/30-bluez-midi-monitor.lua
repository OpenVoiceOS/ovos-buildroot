bluez_midi_monitor = {}
bluez_midi_monitor.properties = {}
bluez_midi_monitor.rules = {}

function bluez_midi_monitor.enable()
  if bluez_midi_monitor.enabled == false then
    return
  end

  load_monitor("bluez-midi", {
    properties = bluez_midi_monitor.properties,
    rules = bluez_midi_monitor.rules,
  })

  if bluez_midi_monitor.properties["with-logind"] then
    load_optional_module("logind")
  end
end
