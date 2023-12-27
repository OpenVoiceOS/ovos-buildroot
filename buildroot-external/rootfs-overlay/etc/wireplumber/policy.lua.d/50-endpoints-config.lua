-- uncomment to enable role-based endpoints
-- this is not yet ready for desktop use
--
--[[

default_policy.policy.roles = {
  ["Capture"] = {
    ["alias"] = { "Multimedia", "Music", "Voice", "Capture" },
    ["priority"] = 25,
    ["action.default"] = "cork",
    ["action.capture"] = "mix",
    ["media.class"] = "Audio/Source",
  },
  ["Multimedia"] = {
    ["alias"] = { "Movie", "Music", "Game" },
    ["priority"] = 25,
    ["action.default"] = "cork",
  },
  ["Speech-Low"] = {
    ["priority"] = 30,
    ["action.default"] = "cork",
    ["action.Speech-Low"] = "mix",
  },
  ["Custom-Low"] = {
    ["priority"] = 35,
    ["action.default"] = "cork",
    ["action.Custom-Low"] = "mix",
  },
  ["Navigation"] = {
    ["priority"] = 50,
    ["action.default"] = "duck",
    ["action.Navigation"] = "mix",
  },
  ["Speech-High"] = {
    ["priority"] = 60,
    ["action.default"] = "cork",
    ["action.Speech-High"] = "mix",
  },
  ["Custom-High"] = {
    ["priority"] = 65,
    ["action.default"] = "cork",
    ["action.Custom-High"] = "mix",
  },
  ["Communication"] = {
    ["priority"] = 75,
    ["action.default"] = "cork",
    ["action.Communication"] = "mix",
  },
  ["Emergency"] = {
    ["alias"] = { "Alert" },
    ["priority"] = 99,
    ["action.default"] = "cork",
    ["action.Emergency"] = "mix",
  },
}

default_policy.endpoints = {
  ["endpoint.capture"] = {
    ["media.class"] = "Audio/Source",
    ["role"] = "Capture",
  },
  ["endpoint.multimedia"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Multimedia",
  },
  ["endpoint.speech_low"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Speech-Low",
  },
  ["endpoint.custom_low"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Custom-Low",
  },
  ["endpoint.navigation"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Navigation",
  },
  ["endpoint.speech_high"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Speech-High",
  },
  ["endpoint.custom_high"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Custom-High",
  },
  ["endpoint.communication"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Communication",
  },
  ["endpoint.emergency"] = {
    ["media.class"] = "Audio/Sink",
    ["role"] = "Emergency",
  },
}
]]--
