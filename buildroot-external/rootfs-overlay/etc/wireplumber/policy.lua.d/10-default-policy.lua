default_policy = {}
default_policy.enabled = true
default_policy.properties = {}
default_policy.endpoints = {}

default_policy.policy = {
  ["move"] = true,   -- moves session items when metadata target.node changes
  ["follow"] = true, -- moves session items to the default device when it has changed

  -- Whether to forward the ports format of filter stream nodes to their
  -- associated filter device nodes. This is needed for application to stream
  -- surround audio if echo-cancel is enabled.
  ["filter.forward-format"] = false,

  -- Set to 'true' to disable channel splitting & merging on nodes and enable
  -- passthrough of audio in the same format as the format of the device.
  -- Note that this breaks JACK support; it is generally not recommended
  ["audio.no-dsp"] = false,

  -- how much to lower the volume of lower priority streams when ducking
  -- note that this is a linear volume modifier (not cubic as in pulseaudio)
  ["duck.level"] = 0.3,
}

bluetooth_policy = {}

bluetooth_policy.policy = {
  -- Whether to store state on the filesystem.
  ["use-persistent-storage"] = true,

  -- Whether to use headset profile in the presence of an input stream.
  ["media-role.use-headset-profile"] = true,

  -- Application names correspond to application.name in stream properties.
  -- Applications which do not set media.role but which should be considered
  -- for role based profile switching can be specified here.
  ["media-role.applications"] = {
    "Firefox", "Chromium input", "Google Chrome input", "Brave input",
    "Microsoft Edge input", "Vivaldi input", "ZOOM VoiceEngine",
    "Telegram Desktop", "telegram-desktop", "linphone", "Mumble",
    "WEBRTC VoiceEngine", "Skype", "Firefox Developer Edition",
  },
}

dsp_policy = {}

dsp_policy.policy = {}

dsp_policy.policy.properties = {}

-- An array of matches/filters to apply.
-- `matches` are rules for matching a sink node. It is an array of
-- properties that all need to match the regexp. If any of the
-- matches in an array work, the filters are executed for the sink.
-- `filter_chain` is a JSON string of parameters to filter-chain module
-- `properties` table only has `pro_audio` boolean, which enables Pro Audio mode on the sink when applying DSP
dsp_policy.policy.rules = {}

function default_policy.enable()
  if default_policy.enabled == false then
    return
  end

  -- Session item factories, building blocks for the session management graph
  -- Do not disable these unless you really know what you are doing
  load_module("si-node")
  load_module("si-audio-adapter")
  load_module("si-standard-link")
  load_module("si-audio-endpoint")

  -- API to access default nodes from scripts
  load_module("default-nodes-api")

  -- API to access mixer controls, needed for volume ducking
  load_module("mixer-api")

  -- Create endpoints statically at startup
  load_script("static-endpoints.lua", default_policy.endpoints)

  -- Create items for nodes that appear in the graph
  load_script("create-item.lua", default_policy.policy)

  -- Link nodes to each other to make media flow in the graph
  load_script("policy-node.lua", default_policy.policy)

  -- Link client nodes with endpoints to make media flow in the graph
  load_script("policy-endpoint-client.lua", default_policy.policy)
  load_script("policy-endpoint-client-links.lua", default_policy.policy)

  -- Link endpoints with device nodes to make media flow in the graph
  load_script("policy-endpoint-device.lua", default_policy.policy)

  -- Switch bluetooth profile based on media.role
  load_script("policy-bluetooth.lua", bluetooth_policy.policy)

  -- Load filter chains for hardware requiring DSP
  load_script("policy-dsp.lua", dsp_policy.policy)
end
