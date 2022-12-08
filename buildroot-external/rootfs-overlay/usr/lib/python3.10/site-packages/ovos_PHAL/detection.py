import subprocess


def is_mycroft_sj201():
    cmd = 'i2cdetect -y -a 1 0x04 0x04 | egrep "(04|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"04" or out == b"UU":
        return True
    return False


def is_respeaker_2mic():
    cmd = 'i2cdetect -y -a 1 0x1a 0x1a | egrep "(1a|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"1a" or out == b"UU":
        return True
    return False


def is_respeaker_4mic():
    cmd = 'i2cdetect -y -a 0x35 0x35 | egrep "(35|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"35" or out == b"UU":
        return True
    return False


def is_respeaker_6mic():
    cmd = 'i2cdetect -y -a 0x3b 0x3b | egrep "(3b|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"3b" or out == b"UU":
        return True
    return False


def is_adafruit():
    cmd = 'i2cdetect -y -a 0x4b 0x4b | egrep "(4b|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"4b" or out == b"UU":
        return True
    return False


def is_texas_tas5806():
    cmd = 'i2cdetect -y -a 0x2f 0x2f | egrep "(2f|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"2f" or out == b"UU":
        return True
    return False
