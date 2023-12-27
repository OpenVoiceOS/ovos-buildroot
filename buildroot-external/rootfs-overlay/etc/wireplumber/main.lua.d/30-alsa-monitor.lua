alsa_monitor = {}
alsa_monitor.properties = {}
alsa_monitor.rules = {}

function alsa_monitor.enable()
  if alsa_monitor.enabled == false then
    return
  end

  -- The "reserve-device" module needs to be loaded for reservation to work
  if alsa_monitor.properties["alsa.reserve"] then
    load_module("reserve-device")
  end

  load_monitor("alsa", {
    properties = alsa_monitor.properties,
    rules = alsa_monitor.rules,
  })

  if alsa_monitor.properties["alsa.midi"] then
    load_monitor("alsa-midi", {
      properties = alsa_monitor.properties,
    })
    -- The "file-monitor-api" module needs to be loaded for MIDI device monitoring
    if alsa_monitor.properties["alsa.midi.monitoring"] then
      load_module("file-monitor-api")
    end
  end
end
