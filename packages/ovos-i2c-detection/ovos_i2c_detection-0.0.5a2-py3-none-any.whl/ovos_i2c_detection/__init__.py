import subprocess
import serial
from time import sleep
from ovos_utils.log import LOG

def is_texas_tas5806():
    cmd = 'i2cdetect -y -a 1 0x2f 0x2f | egrep "(2f|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"2f" or out == b"UU":
        return True
    return False


def is_sj201_v6():
    cmd = 'i2cdetect -y -a 1 0x04 0x04 | egrep "(04|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"04" or out == b"UU":
        return True
    return False


def is_sj201_v10():
    if is_texas_tas5806() and not is_sj201_v6():
        return True
    return False


def is_wm8960():
    cmd = 'i2cdetect -y -a 1 0x1a 0x1a | egrep "(1a|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"1a" or out == b"UU":
        return True
    return False


def is_respeaker_4mic():
    cmd = 'i2cdetect -y -a 1 0x3b 0x3b | egrep "(3b|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"3b" or out == b"UU":
        return True
    return False


def is_respeaker_6mic():
    cmd = 'i2cdetect -y -a 1 0x35 0x35 | egrep "(35|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"35" or out == b"UU":
        return True
    return False


def is_adafruit_amp():
    cmd = 'i2cdetect -y -a 1 0x4b 0x4b | egrep "(4b|UU)" | awk \'{print $2}\''
    out = subprocess.check_output(cmd, shell=True).strip()
    if out == b"4b" or out == b"UU":
        return True
    return False

def is_mark_1():
    if is_wm8960():
        try:
            ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)
            ser.write(b'system.version')
            while ser.is_open:
                is_mk1 = ser.readline().decode().rstrip()
                if is_mk1 and "Command" in is_mk1:
                    # Check for a version
                    mk1_ver = ser.readline().decode().rstrip()
                    # New versions of the firmware will return a version that needs read to continue
                    if mk1_ver:
                        LOG.debug(f"Firmware version {mk1_ver}")
                    ser.close()
                    # This is a Mark 1
                    return True
                ser.close()
            ser.close()
            return False
        except Exception as e:
            LOG.error(e)
            return False
        
