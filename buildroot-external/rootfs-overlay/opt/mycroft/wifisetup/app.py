from flask import Flask, render_template, request
import subprocess
import os
import time
from threading import Thread
import fileinput

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    wifi_ap_array = scan_wifi_networks()

    return render_template('app.html', wifi_ap_array = wifi_ap_array)


@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')


@app.route('/save_credentials', methods = ['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']

    create_wpa_supplicant(ssid, wifi_key)

    # Call reboot_device() in a thread otherwise the reboot will prevent
    # the response from getting to the browser
    def sleep_and_reboot():
        time.sleep(2)
        reboot_device()
    t = Thread(target=sleep_and_reboot)
    t.start()

    return render_template('save_credentials.html', ssid = ssid)

@app.route('/skip_wifi')
def skip_wifi():

    empty_wpa_supplicant()

    # Call reboot_device() in a thread otherwise the reboot will prevent
    # the response from getting to the browser
    def sleep_and_reboot():
        time.sleep(2)
        reboot_device()
    t = Thread(target=sleep_and_reboot)
    t.start()

    return render_template('cancelled_wifi.html')


######## FUNCTIONS ##########

def scan_wifi_networks():
    iwlist_raw = subprocess.Popen(['iw', 'dev', 'ap0', 'scan', 'ap-force'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'SSID' in line:
            ap_ssid = line[7:]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array

def create_wpa_supplicant(ssid, wifi_key):
    temp_conf_file = open('wpa_supplicant-wlan0.conf.tmp', 'w')

    temp_conf_file.write('ctrl_interface=DIR=/var/run/wpa_supplicant\n')
    temp_conf_file.write('update_config=1\n')
    temp_conf_file.write('\n')
    temp_conf_file.write('network={\n')
    temp_conf_file.write('	ssid="' + ssid + '"\n')

    if wifi_key == '':
        temp_conf_file.write('	key_mgmt=NONE\n')
    else:
        temp_conf_file.write('	psk="' + wifi_key + '"\n')

    temp_conf_file.write('}\n')

    temp_conf_file.close

    os.system('mv wpa_supplicant-wlan0.conf.tmp /etc/wpa_supplicant/wpa_supplicant-wlan0.conf')

def empty_wpa_supplicant():
    temp_conf_file = open('wpa_supplicant-wlan0.conf.tmp', 'w')

    temp_conf_file.write('ctrl_interface=DIR=/var/run/wpa_supplicant\n')
    temp_conf_file.write('update_config=1\n')
    temp_conf_file.write('\n')
    temp_conf_file.write('network={\n')

    temp_conf_file.write('}\n')

    temp_conf_file.close

    os.system('mv wpa_supplicant-wlan0.conf.tmp /etc/wpa_supplicant/wpa_supplicant-wlan0.conf')


def reboot_device():
    os.system('reboot')

if __name__ == '__main__':
    os.system("fbv -f -d 1 /opt/mycroft/wifisetup/static/images/wifi.png > /dev/null 2>&1")
    app.run(host = '0.0.0.0', port = '88')
