from ovos_utils.system import MycroftRootLocations
from ovos_utils.fingerprinting import detect_platform, MycroftPlatform
from enum import Enum
from os.path import exists


class MycroftEnclosures(str, Enum):
    PICROFT = "picroft"
    BIGSCREEN = "kde"
    OVOS = "OpenVoiceOS"
    OLD_MARK1 = "mycroft_mark_1(old)"
    MARK1 = "mycroft_mark_1"
    MARK2 = "mycroft_mark_2"
    HOLMESV = "HolmesV"
    OLD_HOLMES = "mycroft-lib"
    GENERIC = "generic"
    OTHER = "unknown"


def enclosure2rootdir(enclosure=None):
    enclosure = enclosure or detect_enclosure()
    if enclosure == MycroftEnclosures.OLD_MARK1:
        return MycroftRootLocations.OLD_MARK1
    elif enclosure == MycroftEnclosures.MARK1:
        return MycroftRootLocations.MARK1
    elif enclosure == MycroftEnclosures.MARK2:
        return MycroftRootLocations.MARK2
    elif enclosure == MycroftEnclosures.PICROFT:
        return MycroftPlatform.PICROFT
    elif enclosure == MycroftEnclosures.OVOS:
        return MycroftPlatform.OVOS
    elif enclosure == MycroftEnclosures.BIGSCREEN:
        return MycroftPlatform.BIGSCREEN
    return None


def detect_enclosure():
    platform = detect_platform()
    if platform == MycroftPlatform.MARK1:
        if exists(MycroftRootLocations.OLD_MARK1):
            return MycroftEnclosures.OLD_MARK1
        return MycroftEnclosures.MARK1
    elif platform == MycroftPlatform.MARK2:
        return MycroftEnclosures.MARK2
    elif platform == MycroftPlatform.PICROFT:
        return MycroftEnclosures.PICROFT
    elif platform == MycroftPlatform.OVOS:
        return MycroftEnclosures.OVOS
    elif platform == MycroftPlatform.BIGSCREEN:
        return MycroftEnclosures.BIGSCREEN
    elif platform == MycroftPlatform.HOLMESV:
        return MycroftEnclosures.HOLMESV
    elif platform == MycroftPlatform.OLD_HOLMES:
        return MycroftEnclosures.OLD_HOLMES

    return MycroftEnclosures.OTHER
