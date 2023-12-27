bluez_monitor = {}
bluez_monitor.properties = {}
bluez_monitor.rules = {}

function bluez_monitor.enable()
  if bluez_monitor.enabled == false then
    return
  end

  load_monitor("bluez", {
    properties = bluez_monitor.properties,
    rules = bluez_monitor.rules,
  })

  if bluez_monitor.properties["with-logind"] then
    load_optional_module("logind")
  end
end
