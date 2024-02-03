Overview
--------

UCM works on top of the standard ALSA subsystem. If there is something
missing or non-working, it usually means that UCM describes the devices
and required control sequences in an incomplete or a wrong way.

It is not required to be a developer to test your hardware.

Use latest UCM configuration
----------------------------

The archive can be obtained from
https://github.com/alsa-project/alsa-ucm-conf/archive/refs/heads/master.tar.gz
or fetched from github https://github.com/alsa-project/alsa-ucm-conf .

The default path for ucm2 configuration is `/usr/share/alsa/ucm2`. This
path may be redirected temporary to the latest configuration tree like:

````
mv /usr/share/alsa/ucm2 /usr/share/alsa/ucm2.distro
ln -s /NEW/UCM2/TREE/PATH /usr/share/alsa/ucm2
````

It is necessary to restart pulseaudio or pipewire to use the new ucm2
configuration.

The configuration revert is simple:

````
rm /usr/share/alsa/ucm2
mv /usr/share/alsa/ucm2.distro /usr/share/alsa/ucm2
````

Useful commands and tools
-------------------------

````
alsa-info.sh --no-upload	# dump the system / ALSA state information
aplay -l			# dump playback ALSA cards and PCM devices
arecord -l			# dump capture ALSA cards and PCM devices
amixer -c 0 contents		# dump all controls for the ALSA card (zero = card number)
amixer -c 0 events		# dump events for controls (zero = card number)
				# useful for Jack detection
amixer -c 0 scontents		# dump simple mixer controls for the ALSA card (zero = card number)
alsamixer -c 0			# set native ALSA mixer (zero = card number) 
speaker-test -c hw:CARD=0,DEV=0	                 # playback test
arecord -D hw:CARD=0,DEV=0 -f dat -vvv a.wav     # capture test
alsaucm -c hw:0 dump text	# dump the UCM configuration (zero = card number)
spa-acp-tool -vvv -c 0		# pipewire audio profile test tool (zero = card number)
````

The components for the UCM device
---------------------------------

1) ALSA PCM device
2) ALSA Jack control name (optional, if available - for the presence detection)
3) Simple mixer control name (optional, if available - for the hardware volume control)

Example of the UCM configuration:

````
Value {
	PlaybackPCM "hw:${CardId},0"	# equivalent to hw:0,0 (for the first sound card)
	JackControl "Speakers Jack"	# should be in 'amixer -c 0 contents' dump
	PlaybackMixerElem "Speaker"	# Speaker bar should be in 'alsamixer -c 0'
}
````

Checking of the corresponding ALSA PCM device
---------------------------------------------

Use `aplay -l` or `capture -l` to list the PCM devices in the system. Pick
the device numbers for the tested ALSA soundcard and substitute those values
for the playback test (`speaker-test -c hw:CARD=0,DEV=0`) and capture test
(`arecord -D hw:CARD=0,DEV=0 -f dat -vvv a.wav`) commands.

Note: If a sound server is running, it should be suspended (see
`man pasuspender` for an example or manage appropriate services or
sockets using systemd - systemctl).

Checking of the corresponding ALSA Jack control
-----------------------------------------------

Use `amixer -c 0 events` (replace zero with the corresponding ALSA card
number) command and watch '??? Jack' control changes when you plug and
unplug the correspoding sound equipment to the tested physical jack.

Checking of the corresponding simple mixer name
-----------------------------------------------

Use `alsamixer -c 0` (replace zero with the corresponding ALSA card
number) command and try to find the corresponding bar which controls the
volume when the PCM device is active. It is recommended to open the
alsamixer tool in a separate terminal window and do the PCM tests in
another.

Testing changes in the UCM configuration
----------------------------------------

The sound server must be restarted to reload the UCM configuration. For
PipeWire, the command `systemctl --user restart wireplumber` is sufficient.

To check the configuration syntax, use `alsaucm -c hw:0 dump text` command 
(replace zero with the corresponding ALSA card number). This command should
not return an error.

Notes
-----

Some special hardware (mostly from the ASoC /ALSA SoC/ tree) may require
special ALSA control initialization sequences. In this case, the driver
developers should provide the hints.

The `_ucmXXXX.` prefixes in the UCM dumps are referring the private
ALSA device names - to test those devices, just remove this prefix. It
will not work for special devices defined only in UCM configuration files.
If you like to test this special alsa-lib configuration, you may dump the
alsa-lib configuration using `alsaucm -c hw:0 get _alibcfg` and put the
configuration to `~/.asoundrc` for example.

