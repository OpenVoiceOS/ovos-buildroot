RELEASE_DIR = release

BUILDROOT=buildroot
BUILDROOT_EXTERNAL=buildroot-external
DEFCONFIG_DIR = $(BUILDROOT_EXTERNAL)/configs

TARGETS := $(notdir $(patsubst %_defconfig,%,$(wildcard $(DEFCONFIG_DIR)/*_defconfig)))
TARGETS_CONFIG := $(notdir $(patsubst %_defconfig,%-config,$(wildcard $(DEFCONFIG_DIR)/*_defconfig)))

.NOTPARALLEL: $(TARGETS) $(TARGETS_CONFIG) all

.PHONY: $(TARGETS) $(TARGETS_CONFIG) all clean help

all: $(TARGETS)

$(RELEASE_DIR):
	mkdir -p $(RELEASE_DIR)

$(TARGETS_CONFIG): %-config:
	@echo "config $*"
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) "$*_defconfig"

$(TARGETS): %: $(RELEASE_DIR) %-config
	@echo "build $@"
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) 2>&1 | tee logs/buildroot_$@_output.txt
	rsync -ah --progress $(BUILDROOT)/output/images/disk.img $(RELEASE_DIR)/OpenVoiceOS_$@.img
	xz -3 -T0 -v -f $(RELEASE_DIR)/OpenVoiceOS_$@.img

	# Do not clean when building for one target
ifneq ($(words $(filter $(TARGETS),$(MAKECMDGOALS))), 1)
	@echo "clean $@"
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) clean
endif
	@echo "finished $@"

clean:
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) clean

menuconfig:
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) menuconfig

linux-menuconfig:
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) linux-menuconfig

busybox-menuconfig:
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) busybox-menuconfig

savedefconfig:
	$(MAKE) -C $(BUILDROOT) BR2_EXTERNAL=../$(BUILDROOT_EXTERNAL) savedefconfig

help:
	@echo "Supported targets: $(TARGETS)"
	@echo "Run 'make <target>' to build a target image."
	@echo "Run 'make all' to build all target images."
	@echo "Run 'make clean' to clean the build output."
	@echo "Run 'make <target>-config' to configure OpenVoiceOS for a target."
	@echo "Run 'make menuconfig' to update current config utilising a menu based program."
	@echo "Run 'make savedefconfig' to save current config back to config directory."
