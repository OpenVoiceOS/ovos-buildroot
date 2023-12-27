default_access.enabled = true

default_access.properties = {
  -- Enable the use of the flatpak portal integration.
  -- Disable if you are running a system-wide instance, which
  -- doesn't have access to the D-Bus user session
  ["enable-flatpak-portal"] = true,
}

default_access.rules = {
  {
    matches = {
      {
        { "pipewire.access", "=", "flatpak" },
        { "media.category", "=", "Manager" },
      },
    },
    default_permissions = "all",
  },
  {
    matches = {
      {
        { "pipewire.access", "=", "flatpak" },
      },
    },
    default_permissions = "rx",
  },
  {
    matches = {
      {
        { "pipewire.access", "=", "restricted" },
      },
    },
    default_permissions = "rx",
  },
}
