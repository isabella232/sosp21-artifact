import os
import json
import sys
import pprint as pp
import ray

from lifxlan import LifxLAN
from k8s import update_status

from flask import Flask
from flask import request

app = Flask(__name__)

global configs, lifx_devices, phl_devices


@app.route("/")
def hello():
    return "Hello from Python!"


"""lifx"""


def discover_lifx():
    print("lifx: discovering lights...")
    devices = LifxLAN().get_lights()
    device_by_mac = {d.get_mac_addr(): d for d in devices}
    print(f"lifx: found {len(devices)} light(s): "
          f"{device_by_mac}\n")

    device_by_id = dict()
    for k, v in configs.items():
        if v["provider"] == "lifx":
            device_by_id[k] = {
                "dev": device_by_mac[v["mac"]],
                "monitor": None,
            }

    return device_by_id


@ray.remote
def monitor_lifx_status(id):
    # source: https://github.com/mclarkk/lifxlan
    # power can be "on"/"off", True/False, 0/1, or 0/65535
    # color is a HSBK list of values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
    # duration is the transition time in milliseconds
    # rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
    # is_transient is 1/0. If 1, return to the original color after the specified number of cycles. If 0,
    # set light to specified color
    # period is the length of one cycle in milliseconds
    # cycles is the number of times to repeat the waveform
    # duty_cycle is an integer between -32768 and 32767. Its effect is most obvious with the Pulse waveform
    #     set duty_cycle to 0 to spend an equal amount of time on the original color and the new color
    #     set duty_cycle to positive to spend more time on the original color
    #     set duty_cycle to negative to spend more time on the new color
    # waveform can be 0 = Saw, 1 = Sine, 2 = HalfSine, 3 = Triangle, 4 = Pulse (strobe)
    # infrared_brightness (0-65535) - is the maximum infrared brightness when the lamp automatically
    # turns on infrared (0 = off)

    report_interval = 0.5

    dev = lifx_devices[id]["dev"]
    status = {
        "power": dev.get_power(),
        "color": dev.get_color(),
    }
    # TOOD:
    print(status)


@app.route("/lifx/<id>", methods=["GET", "POST"])
def serve_lifx(id):
    if id not in lifx_devices:
        return f"device {id} missing"
    dev_handle = lifx_devices[id]

    if request.method == 'GET':
        print("lifx: do GET")
        pass

    if request.method == 'POST':
        print("lifx: do POST")
        body = request.get_json(silent=True)
        print(body)

    # start the handler if needed
    if not dev_handle.get("monitor", None):
        dev_handle["monitor"] = ray.get(monitor_lifx_status.remote(id))
    return "succeed"


"""philips"""


def discover_philips():
    # from phue import Bridge
    # b = Bridge('ip_of_your_bridge')
    return []


# device discovery

if __name__ == "__main__":
    # load device configs
    _dir = os.path.dirname(os.path.abspath(__file__))
    _config = os.path.join(_dir, "..", "..", "device.json")
    with open(_config) as f:
        configs = json.load(f)

    ray.init()

    # discover devices
    lifx_devices = discover_lifx()
    phl_devices = discover_philips()

    app.run(host='0.0.0.0', port=8090)
