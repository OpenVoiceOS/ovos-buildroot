Feature: volume control

  Scenario Outline: turning up the volume
    Given an english speaking user
     And the volume is set to 5
     When the user says "<volume up>"
     Then "mycroft-volume" should increase the volume

  Examples: turning up the volume
    | volume up |
    | volume up |
    | increase volume |
    | volume up |
    | turn it up |
    | louder |
    | more sound |
    | more audio |
    | higher volume |
    | raise the volume |
    | boost volume |
    | turn up the volume |
    | crank it up |
    | crank volume |
    | make it louder |

  Scenario Outline: turning down the volume
    Given an english speaking user
     And the volume is set to 5
     When the user says "<volume down>"
     Then "mycroft-volume" should decrease the volume

  Examples: turning down the volume
    | volume down |
    | volume down |
    | decrease volume |
    | volume down |
    | turn it down |
    | quieter please |
    | less sound |
    | lower volume |
    | reduce volume |
    | quieter |
    | less volume |
    | lower sound |
    | make it quieter |
    | make it lower |
    | make it softer |

  Scenario Outline: change volume to a number between 1 and 10
    Given an english speaking user
     And the volume is set to 5
     When the user says "<change volume to a number>"
     Then "mycroft-volume" should reply with dialog from "set.volume.dialog"

  Examples: change volume to a number between 0 and 10
    | change volume to a number |
    | change volume to 7 |
    | change volume to 8 |
    | set volume to 9 |
    | set audio to 6 |
    | decrease volume to 4 |
    | raise volume to 8 |
    | lower volume to 4 |
    | volume 8 |

  Scenario Outline: change volume to a percent of 100
    Given an english speaking user
     And the volume is set to 5
     When the user says "<change volume to a percent>"
     Then "mycroft-volume" should reply with dialog from "set.volume.percent.dialog"

  Examples: change volume to a percent
    | change volume to a percent |
    | volume 80 percent |

  Scenario Outline: max volume
    Given an english speaking user
     And the volume is set to 5
     When the user says "<max volume>"
     Then "mycroft-volume" should reply with dialog from "max.volume.dialog"

  Examples: max volume
    | max volume |
    | max volume |
    | maximum volume |
    | loudest volume |
    | max audio |
    | maximum audio |
    | max sound |
    | maximum sound |
    | turn it up all the way |
    | set volume to maximum |
    | highest volume |
    | raise volume to max |
    | raise volume all the way |
    | increase volume  to 10 |

  Scenario Outline: volume status
    Given an english speaking user
     And the volume is set to 5
     When the user says "<volume status>"
     Then "mycroft-volume" should reply with dialog from "volume.is.dialog"

  Examples: volume status
    | volume status |
    | volume status |
    | what's your volume |
    | what's your current volume level |
    | what’s your sound level |
    | what's your audio level |
    | volume level |
    | volume status |
    | what volume are you set to |
    | how loud is it |
    | how loud is the volume |
    | how loud is that |
    | how high is the volume |
    | how high is the sound |
    | how high is the audio |
    | how high is the sound level |
    | how high is the audio level |
    | how high is the volume level |
    | what's the volume at |
    | what's the current volume |
    | what's the volume set to |
    | what is the volume at |
    | what level is the volume set to |
    | what level is the volume at |

  Scenario Outline: reset volume
    Given an english speaking user
     And the volume is set to 10
     When the user says "<reset volume>"
     Then "mycroft-volume" should reply with dialog from "reset.volume.dialog"

  Examples: reset volume
    | reset volume |
    | reset volume |
    | default volume |
    | go to default volume |
    | restore volume |
    | change volume to default volume |
    | set volume to default volume |

  Scenario Outline: mute audio
    Given an english speaking user
     And the volume is set to 5
     When the user says "<mute audio>"
     Then "mycroft-volume" should reply with dialog from "mute.volume.dialog"

  Examples: mute audio
    | mute audio |
    | mute audio |
    | mute volume |
    | mute all audio |
    | mute the sound |
    | silence the audio |

  @xfail
  Scenario Outline: mute audio
    Given an english speaking user
     And the volume is set to 5
     When the user says "<mute audio>"
     Then "mycroft-volume" should reply with dialog from "mute.volume.dialog"

  Examples: mute audio
    | mute audio |
    | be quiet |

  Scenario Outline: unmute audio
    Given an english speaking user
     And Mycroft audio is muted
     When the user says "<unmute audio>"
     Then "mycroft-volume" should reply with dialog from "reset.volume.dialog"

  Examples: unmute audio
    | unmute audio |
    | unmute audio |
    | unmute the volume |

  @xfail
  Scenario Outline: unmute audio
    Given an english speaking user
     And Mycroft audio is muted
     When the user says "<unmute audio>"
     Then "mycroft-volume" should reply with dialog from "reset.volume.dialog"

  Examples: unmute audio
    | unmute audio |
    | unmute |
    | turn sound back on |
    | turn on sound |
    | turn muting off |
    | turn mute off |
    | unmute all sound |
