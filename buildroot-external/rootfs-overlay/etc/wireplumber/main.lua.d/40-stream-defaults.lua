stream_defaults = {}
stream_defaults.enabled = true

stream_defaults.properties = {
  -- whether to restore the last stream properties or not
  ["restore-props"] = true,

  -- whether to restore the last stream target or not
  ["restore-target"] = true,

  -- the default channel volume for new streams whose props were never saved
  -- previously. This is only used if "restore-props" is set to true.
  ["default-channel-volume"] = 1.0,
}

stream_defaults.rules = {
  -- Rules to override settings per node
  -- {
  --   matches = {
  --     {
  --       { "application.name", "matches", "pw-play" },
  --     },
  --   },
  --   apply_properties = {
  --     ["state.restore-props"] = false,
  --     ["state.restore-target"] = false,
  --     ["state.default-channel-volume"] = 0.5,
  --   },
  -- },
}

function stream_defaults.enable()
  if stream_defaults.enabled == false then
    return
  end

  -- Save and restore stream-specific properties
  load_script("restore-stream.lua", {
    properties = stream_defaults.properties,
    rules = stream_defaults.rules,
  })
end
