# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/stop-circle.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Better Stop
Stop mycroft by voice

![](./logo.png)

## About
Provides verbal interfaces for the "Stop" command. 

NOTE: This Skill is a little unusual in that it really doesn't do anything
directly, rather it emits messages for the device creator to capture.

What is wrong with [official mycroft skill](https://github.com/MycroftAI/skill-stop)?
- silently captures enclosure specific commands that do nothing
- conflicts with enclosure specific skills
- captures [every utterance with the word "stop"](https://github.com/MycroftAI/mycroft-core/issues/1566)
  
This skill uses padatious instead of adapt, this take the full utterance 
into account. It is also a fallback skill and will revert to the old 
behaviour if no other skill matches. 

NOTE: This conflicts with and blacklists the official skill!

Alternatives:
- [Upstream PR#37](https://github.com/MycroftAI/skill-stop/pull/37)
- [Upstream PR#8](https://github.com/MycroftAI/skill-stop/pull/8) 
  Abandoned

  
## Examples
* "Stop"

# Platform support

- :heavy_check_mark: - tested and confirmed working
- :x: - incompatible/non-functional
- :question: - untested
- :construction: - partial support

|     platform    |   status   |  tag  | version | last tested | 
|:---------------:|:----------:|:-----:|:-------:|:-----------:|
|    [Chatterbox](https://hellochatterbox.com)   | :question: |  dev  |         |    never    | 
|     [HolmesV](https://github.com/HelloChatterbox/HolmesV)     | :question: |  dev  |         |    never    | 
|    [LocalHive](https://github.com/JarbasHiveMind/LocalHive)    | :question: |  dev  |         |    never    |  
|  [Mycroft Mark1](https://github.com/MycroftAI/enclosure-mark1)    | :question: |  dev  |         |    never    | 
|  [Mycroft Mark2](https://github.com/MycroftAI/hardware-mycroft-mark-II)    | :question: |  dev  |         |    never    |  
|    [NeonGecko](https://neon.ai)      | :question: |  dev  |         |    never    |   
|       [OVOS](https://github.com/OpenVoiceOS)        | :question: |  dev  |         |    never    |    
|     [Picroft](https://github.com/MycroftAI/enclosure-picroft)       | :question: |  dev  |         |    never    |  
| [Plasma Bigscreen](https://plasma-bigscreen.org/)  | :question: |  dev  |         |    never    |  

- `tag` - link to github release / branch / commit
- `version` - link to release/commit of platform repo where this was tested



## Category
**Configuration**

## Tags
#system
