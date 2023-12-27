v4l2_monitor = {}
v4l2_monitor.properties = {}
v4l2_monitor.rules = {}

function v4l2_monitor.enable()
  if v4l2_monitor.enabled == false then
    return
  end

  load_monitor("v4l2", {
    properties = v4l2_monitor.properties,
    rules = v4l2_monitor.rules,
  })
end
