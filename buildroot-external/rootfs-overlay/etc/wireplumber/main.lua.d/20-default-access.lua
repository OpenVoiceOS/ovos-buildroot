default_access = {}
default_access.properties = {}
default_access.rules = {}

function default_access.enable()
  if default_access.enabled == false then
    return
  end

  load_access("default", {
    rules = default_access.rules
  })

  if default_access.properties["enable-flatpak-portal"] then
    -- Enables portal permissions via org.freedesktop.impl.portal.PermissionStore
    load_module("portal-permissionstore")
    load_access("portal")
  end
end
