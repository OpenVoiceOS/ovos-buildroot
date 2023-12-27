bluez_monitor.enabled = true

bluez_monitor.properties = {
  -- Enabled roles (default: [ a2dp_sink a2dp_source bap_sink bap_source hfp_hf hfp_ag ])
  --
  -- Currently some headsets (Sony WH-1000XM3) are not working with
  -- both hsp_ag and hfp_ag enabled, so by default we enable only HFP.
  --
  -- Supported roles: hsp_hs (HSP Headset),
  --                  hsp_ag (HSP Audio Gateway),
  --                  hfp_hf (HFP Hands-Free),
  --                  hfp_ag (HFP Audio Gateway)
  --                  a2dp_sink (A2DP Audio Sink)
  --                  a2dp_source (A2DP Audio Source)
  --                  bap_sink (LE Audio Basic Audio Profile Sink)
  --                  bap_source (LE Audio Basic Audio Profile Source)
  --["bluez5.roles"] = "[ a2dp_sink a2dp_source bap_sink bap_source hsp_hs hsp_ag hfp_hf hfp_ag ]",

  -- Enabled A2DP codecs (default: all).
  --["bluez5.codecs"] = "[ sbc sbc_xq aac ldac aptx aptx_hd aptx_ll aptx_ll_duplex faststream faststream_duplex ]",

  -- HFP/HSP backend (default: native).
  -- Available values: any, none, hsphfpd, ofono, native
  --["bluez5.hfphsp-backend"] = "native",

  -- HFP/HSP native backend modem (default: none).
  -- Available values: none, any or the modem device string as found in
  --   'Device' property of org.freedesktop.ModemManager1.Modem interface
  --["bluez5.hfphsp-backend-native-modem"] = "none",

  -- HFP/HSP hardware offload SCO support (default: false).
  --["bluez5.hw-offload-sco"] = false,

  -- Properties for the A2DP codec configuration
  --["bluez5.default.rate"] = 48000,
  --["bluez5.default.channels"] = 2,

  -- Register dummy AVRCP player, required for AVRCP volume function.
  -- Disable if you are running mpris-proxy or equivalent.
  --["bluez5.dummy-avrcp-player"] = true,

  -- Opus Pro Audio mode settings
  --["bluez5.a2dp.opus.pro.channels"] = 3,  -- no. channels
  --["bluez5.a2dp.opus.pro.coupled-streams"] = 1,  -- no. joint stereo pairs, see RFC 7845 Sec. 5.1.1
  --["bluez5.a2dp.opus.pro.locations"] = "FL,FR,LFE",  -- audio locations
  --["bluez5.a2dp.opus.pro.max-bitrate"] = 600000,
  --["bluez5.a2dp.opus.pro.frame-dms"] = 50,  -- frame duration in 1/10 ms: 25, 50, 100, 200, 400
  --["bluez5.a2dp.opus.pro.bidi.channels"] = 1,  -- same settings for the return direction
  --["bluez5.a2dp.opus.pro.bidi.coupled-streams"] = 0,
  --["bluez5.a2dp.opus.pro.bidi.locations"] = "FC",
  --["bluez5.a2dp.opus.pro.bidi.max-bitrate"] = 160000,
  --["bluez5.a2dp.opus.pro.bidi.frame-dms"] = 400,

  -- Enable the logind module, which arbitrates which user will be allowed
  -- to have bluetooth audio enabled at any given time (particularly useful
  -- if you are using GDM as a display manager, as the gdm user also launches
  -- pipewire and wireplumber).
  -- This requires access to the D-Bus user session; disable if you are running
  -- a system-wide instance of wireplumber.
  ["with-logind"] = true,

  -- The settings below can be used to override feature enabled status. By default
  -- all of them are enabled. They may also be disabled via the hardware quirk
  -- database, see bluez-hardware.conf
  --["bluez5.enable-sbc-xq"] = true,
  --["bluez5.enable-msbc"] = true,
  --["bluez5.enable-hw-volume"] = true,
}

bluez_monitor.rules = {
  -- An array of matches/actions to evaluate.
  {
    -- Rules for matching a device or node. It is an array of
    -- properties that all need to match the regexp. If any of the
    -- matches work, the actions are executed for the object.
    matches = {
      {
        -- This matches all cards.
        { "device.name", "matches", "bluez_card.*" },
      },
    },
    -- Apply properties on the matched object.
    apply_properties = {
      -- Auto-connect device profiles on start up or when only partial
      -- profiles have connected. Disabled by default if the property
      -- is not specified.
      --["bluez5.auto-connect"] = "[ hfp_hf hsp_hs a2dp_sink hfp_ag hsp_ag a2dp_source ]",

      -- Hardware volume control (default: [ hfp_ag hsp_ag a2dp_source ])
      --["bluez5.hw-volume"] = "[ hfp_hf hsp_hs a2dp_sink hfp_ag hsp_ag a2dp_source ]",

      -- LDAC encoding quality
      -- Available values: auto (Adaptive Bitrate, default)
      --                   hq   (High Quality, 990/909kbps)
      --                   sq   (Standard Quality, 660/606kbps)
      --                   mq   (Mobile use Quality, 330/303kbps)
      --["bluez5.a2dp.ldac.quality"] = "auto",

      -- AAC variable bitrate mode
      -- Available values: 0 (cbr, default), 1-5 (quality level)
      --["bluez5.a2dp.aac.bitratemode"] = 0,

      -- Profile connected first
      -- Available values: a2dp-sink (default), headset-head-unit
      --["device.profile"] = "a2dp-sink",

      -- Opus Pro Audio encoding mode: audio, voip, lowdelay
      --["bluez5.a2dp.opus.pro.application"] = "audio",
      --["bluez5.a2dp.opus.pro.bidi.application"] = "audio",
    },
  },
  {
    matches = {
      {
        -- Matches all sources.
        { "node.name", "matches", "bluez_input.*" },
      },
      {
        -- Matches all sinks.
        { "node.name", "matches", "bluez_output.*" },
      },
    },
    apply_properties = {
      --["node.nick"] = "My Node",
      --["priority.driver"] = 100,
      --["priority.session"] = 100,
      --["node.pause-on-idle"] = false,
      --["resample.quality"] = 4,
      --["channelmix.normalize"] = false,
      --["channelmix.mix-lfe"] = false,
      --["session.suspend-timeout-seconds"] = 5,  -- 0 disables suspend
      --["monitor.channel-volumes"] = false,

      -- Media source role, "input" or "playback"
      -- Defaults to "playback", playing stream to speakers
      -- Set to "input" to use as an input for apps
      --["bluez5.media-source-role"] = "input",
    },
  },
}
