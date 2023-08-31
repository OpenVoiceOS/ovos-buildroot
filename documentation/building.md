# Building an image (or all images) yourself

## Getting started.

Only use x86_64 based architecture/ hardware to build the image(s). Other systems might work, however are untested and therefor unsupported. 

The following build environment has been tested :
- Architecture: x86_64 
- Hardware: Intel Core i5 processor, 8GB RAM, 240GB SSD (you can build on less RAM (2GB) and slower storage but more RAM, faster storage =  quicker image building)
- OS: Ubuntu 22.04 LTS server

### Installing System Build Dependencies
[Buildroot dependencies] must be installed as a prerequisite, assuming apt:

```
$ sudo apt-get install -y \
  bash \
  bc \
  binutils \
  build-essential \
  bzip2 \
  cpio \
  diffutils \
  file \
  findutils \
  gzip \
  libarchive-tools \
  make \
  patch \
  perl \
  rsync \
  sed \
  tar \
  unzip \
  wget \
  which
```
[Buildroot dependencies]: https://buildroot.org/downloads/manual/manual.html#requirement-mandatory

### The following firewall ports need to be allowed to the internet.
In addition to the usual http/https ports (tcp 80, tcp 443) a couple of other ports need to be allowed to the internet :
- tcp 9418 (git).
- tcp 21 (ftp PASV) and random ports for DATA channel. This can be optional but better to have this allowed along with the corresponding random data channel ports. (knowledge of firewalls required)

## Getting the code.
First, get the code on your system! The simplest method is via git.
<br>
- cd ~/
- git clone --recurse-submodules https://github.com/OpenVoiceOS/ovos-buildroot.git
- cd ovos-buildroot

## Building the image.
Building the image(s) can be done by utilizing a proper Makefile;
<br>
To see the available commands, just run:
```
$ make help
```

As example to build the rpi4 version;
```
$ make clean
$ make rpi4_64
```
Building an image on the above stated devlopment machne takes around 3-4 hours. If you have a higher specification build machine, the building time can be as fast (or slow, depending on your point of view) as ~2 hours.

When everything goes fine the following images/files will be available within the ./release directory;
#### OpenVoiceOS_<CONFIG>_<TIMESTAMP>.img
This is the raw flashable disk image that can be flashed to your to be used disk (SD-Card, USB-Stick, SSD, SATA, etc).
*At current time this file is about ~1.4GB.

#### OpenVoiceOS_<CONFIG>_<TIMESTAMP>.img.xz
This is the same raw flashable disk image that can be flashed to your to be used disk (SD-Card, USB-Stick, SSD, SATA, etc), however xz compressed. This save bandwith if it needs to be downloaded and certain disk image utilities such as the Raspberry Pi Disk imager have native support to flash these type of files without uncompressing them first.
*At current time this file is about ~450MB.

#### OpenVoiceOS_<CONFIG>_<TIMESTAMP>.swu
This is a firmware update file that can be used to update an already flashed device by utilizing its update system. This file basically contains a new rootfs as update.
*At current time this file is about ~340MB.

#### OpenVoiceOS_<CONFIG>_<TIMESTAMP>.swu.xz
This is the same firmware update file as above, however again xz compressed to save possible bandwith sharing it online. Be aware the on-device update system does not support compressed files, so it has to be uncompressed first to be used.
*At current time this file is about ~230MB.

#### OpenVoiceOS_<CONFIG>_<TIMESTAMP>.vdi & OpenVoiceOS_<CONFIG>_<TIMESTAMP>.vdi.xz
These files are Virtual Disk Images, where the .xz is again compressed for the same reasons as above. This VDI can be imported as virtual disk within Virtual Machine's. Bare in mind that these virtual disk images do not yet contain unused space, so for proper use of them make sure you extend them within the VM software to the disk size of choose (8 GB is more then enough).
*At current time these files are about ~700MB and ~450MB.