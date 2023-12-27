libcamera_monitor = {}
libcamera_monitor.properties = {}
libcamera_monitor.rules = {}

function libcamera_monitor.enable()
  if libcamera_monitor.enabled == false then
    return
  end

  load_monitor("libcamera", {
    properties = libcamera_monitor.properties,
    rules = libcamera_monitor.rules,
  })
end
