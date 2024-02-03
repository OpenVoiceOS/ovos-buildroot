Use Case Configuration files
----------------------------

Library directories:

  platforms/
  codecs/
  dsps/

Those directories are not inspected for the list of available UCM
configurations. They contain files included from other UCMs.

UCM master configuration path lookup is defined in the top level
ucm.conf file. This file allows custom directory layout. The new
ucm2 layout is based on the ALSA driver name with the kernel driver
name as fallback. The virtual cards (no direct hw bound) lookups are
placed to the separate conf.virt.d directory.

The lookup configuration:

  https://git.alsa-project.org/?p=alsa-ucm-conf.git;a=blob;f=ucm2/ucm.conf

Example paths - new conf.d scheme:

- conf.d/USB-Audio/Dell-WD15-Dock.conf
-- special configuration for the Dell docking station with USB soundcard
- conf.virt.d/TwoCardsMix.conf
-- virtual UCM from two soundcards

Example paths - no conf.d scheme (may be invalidated):

- USB-Audio/Dell-WD15-Dock.conf
-- special configuration for the Dell docking station with USB soundcard
- TwoCardsMix/TwoCardsMix.conf
-- virtual UCM from two soundcards

Note: For the driver configurations, use always the ALSA driver name or
the real kernel driver name - not the ucm card name configuration paths!

The kernel driver name is obtained using sysfs like (last
part of the path is used from the symlink):

````
  /sys/class/sound/card0/device/driver
````

The ALSA driver name can be obtained using procfs like:

````
  cat /proc/asound/cards
  1 [NVidia         ]: HDA-Intel - HDA NVidia
                       HDA NVidia at 0xb5080000 irq 17

  driver name: HDA-Intel
  card short name: HDA NVidia
  card long name: HDA NVidia at 0xb5080000 irq 17
````

Syntax, value names
-------------------

https://git.alsa-project.org/?p=alsa-lib.git;a=blob;f=include/use-case.h
