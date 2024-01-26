#!/usr/bin/env python3
from importlib import import_module
import os, socket, psutil
import subprocess, re
from flask import Flask, render_template, Response, jsonify, request, send_from_directory, send_file
import json

from flask_socketio import SocketIO, emit

from camera_opencv import Camera
from camera_opencv import RobotCtrlMiddleWare

import time
import logging
import threading

import yaml

curpath = os.path.realpath(__file__)
thisPath = os.path.dirname(curpath)
with open(thisPath + '/config.yaml', 'r') as yaml_file:
    f = yaml.safe_load(yaml_file)

robot_name  = f['base_config']['robot_name']
sbc_version = f['base_config']['sbc_version']

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

socketio = SocketIO(app)
camera = Camera()
robot = RobotCtrlMiddleWare()

net_interface = "wlan0"
signal_strength_cache = None

pic_size = 0;
vid_size = 0;
cpu_read = 0;
cpu_temp = 0;
ram_read = 0;
ssid_read= 0;

cmd_actions = {
    f['code']['min_res']: lambda: camera.set_video_resolution("240P"),
    f['code']['mid_res']: lambda: camera.set_video_resolution("480P"),
    f['code']['max_res']: lambda: camera.set_video_resolution("960P"),
    f['code']['zoom_x1']: lambda: camera.scale_frame(1),
    f['code']['zoom_x2']: lambda: camera.scale_frame(2),
    f['code']['zoom_x4']: lambda: camera.scale_frame(4),
    f['code']['pic_cap']: lambda: camera.capture_frame(thisPath + '/static/'),
    f['code']['vid_sta']: lambda: camera.record_video(1, thisPath + '/videos/'),
    f['code']['vid_end']: lambda: camera.record_video(0, thisPath + '/videos/'),
    f['code']['cv_none']: lambda: camera.set_cv_mode(f['code']['cv_none']),
    f['code']['cv_moti']: lambda: camera.set_cv_mode(f['code']['cv_moti']),
    f['code']['cv_face']: lambda: camera.set_cv_mode(f['code']['cv_face']),
    f['code']['cv_objs']: lambda: camera.set_cv_mode(f['code']['cv_objs']),
    f['code']['cv_clor']: lambda: camera.set_cv_mode(f['code']['cv_clor']),
    f['code']['cv_hand']: lambda: camera.set_cv_mode(f['code']['cv_hand']),
    f['code']['cv_auto']: lambda: camera.set_cv_mode(f['code']['cv_auto']),
    f['code']['re_none']: lambda: camera.set_detection_reaction(f['code']['re_none']),
    f['code']['re_capt']: lambda: camera.set_detection_reaction(f['code']['re_capt']),
    f['code']['re_reco']: lambda: camera.set_detection_reaction(f['code']['re_reco']),
    f['code']['mc_lock']: lambda: camera.set_movtion_lock(f['code']['mc_lock']),
    f['code']['mc_unlo']: lambda: camera.set_movtion_lock(f['code']['mc_unlo']),
    f['code']['led_off']: robot.set_led_mode_off,
    f['code']['led_aut']: robot.set_led_mode_auto,
    f['code']['led_ton']: robot.set_led_mode_on,
    f['code']['base_of']: robot.set_base_led_off,
    f['code']['base_on']: robot.set_base_led_on,
    f['code']['head_ct']: robot.head_led_ctrl,
    f['code']['base_ct']: robot.base_led_ctrl,
    f['code']['s_panid']: camera.set_pan_id,
    f['code']['release']: camera.release_torque,
    f['code']['set_mid']: camera.middle_set,
    f['code']['s_tilid']: camera.set_tilt_id
}


@app.route('/config')
def get_config():
    with open(thisPath + '/config.yaml', 'r') as file:
        yaml_content = file.read()
    return yaml_content


def get_signal_strength(interface):
    global signal_strength_cache
    try:
        output = subprocess.check_output(["iwconfig", interface]).decode("utf-8")
        signal_strength = re.search(r"Signal level=(-\d+)", output)
        if signal_strength:
            signal_strength_cache = int(signal_strength.group(1))
        else:
            signal_strength_cache = 0
    except Exception as e:
        print(f"Error: {e}")
        signal_strength_cache = -1
    return signal_strength_cache


def get_ip_address():
    while(1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            time.sleep(1)


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_cpu_temperature():
    try:
        temperature_str = os.popen('vcgencmd measure_temp').readline()
        temperature = float(temperature_str.replace("temp=", "").replace("'C\n", ""))
        return temperature
    except Exception as e:
        print("Error reading CPU temperature:", str(e))
        return None


def get_memory_usage():
    return psutil.virtual_memory().percent


def update_device_info():
    global pic_size, vid_size, cpu_read, ram_read, ssid_read, cpu_temp
    while 1:
        pic_size = get_folder_size(thisPath + '/static')
        vid_size = get_folder_size(thisPath + '/videos')
        cpu_read = get_cpu_usage()
        cpu_temp = get_cpu_temperature()
        ram_read = get_memory_usage()
        ssid_read= get_signal_strength(net_interface)
        time.sleep(1)


def update_data_websocket():
    while 1:
        try:
            fb_json = camera.get_status()
        except:
            continue
        socket_data = {
                    f['fb']['picture_size']:pic_size,
                    f['fb']['video_size']:  vid_size,
                    f['fb']['cpu_load']:    cpu_read,
                    f['fb']['cpu_temp']:    cpu_temp,
                    f['fb']['ram_usage']:   ram_read,
                    f['fb']['wifi_rssi']:   ssid_read
                    }
        try:
            socket_data.update(fb_json)
            socketio.emit('update', socket_data, namespace='/ctrl')
        except:
            pass
        time.sleep(0.1)


@app.route('/')
def index():
    """Video streaming home page."""
    robot.play_random_audio("connected", False)
    date_update_thread = threading.Thread(target=update_data_websocket, daemon=True)
    date_update_thread.start()
    device_update_thread = threading.Thread(target=update_device_info, daemon=True)
    device_update_thread.start()
    return render_template('index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('templates', filename)


@app.route('/photo/<path:filename>')
def serve_static_photo(filename):
    return send_from_directory('templates', filename)


@app.route('/video/<path:filename>')
def serve_static_video(filename):
    return send_from_directory('templates', filename)
    

@app.route('/settings/<path:filename>')
def serve_static_settings(filename):
    return send_from_directory('templates', filename)


@app.route('/index')
def serve_static_home(filename):
    return redirect(url_for('index'))
    

def gen(cameraInput):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = cameraInput.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_photo_names')
def get_photo_names():
    photo_files = sorted(os.listdir(thisPath + '/static'), key=lambda x: os.path.getmtime(os.path.join(thisPath + '/static', x)), reverse=True)
    return jsonify(photo_files)


@app.route('/get_photo/<filename>')
def get_photo(filename):
    return send_from_directory(thisPath + '/static', filename)


@app.route('/delete_photo', methods=['POST'])
def delete_photo():
    filename = request.form.get('filename')
    try:
        os.remove(os.path.join(thisPath + '/static', filename))
        return jsonify(success=True)
    except Exception as e:
        print(e)
        return jsonify(success=False)


@app.route('/delete_video', methods=['POST'])
def delete_video():
    filename = request.form.get('filename')
    try:
        os.remove(os.path.join(thisPath + '/videos', filename))
        return jsonify(success=True)
    except Exception as e:
        print(e)
        return jsonify(success=False)


@app.route('/get_video_names')
def get_video_names():
    video_files = sorted(
        [filename for filename in os.listdir(thisPath + '/videos/') if filename.endswith('.mp4')],
        key=lambda filename: os.path.getctime(os.path.join(thisPath + '/videos/', filename)),
        reverse=True
    )
    return jsonify(video_files)


@app.route('/videos/<path:filename>')
def videos(filename):
    return send_from_directory(thisPath + '/videos', filename)


def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    # Convert total_size to MB
    size_in_mb = total_size / (1024 * 1024)
    return round(size_in_mb,2)


@socketio.on('message', namespace='/ctrl')
def handle_socket_cmd(message):
    try:
        json_data = json.loads(message)
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return
    cmd_a = float(json_data.get("A", 0))
    cmd_b = float(json_data.get("B", 0))
    cmd_c = float(json_data.get("C", 0))
    if cmd_a in cmd_actions:
        cmd_actions[cmd_a]()
    else:
        pass


@socketio.on('json', namespace='/json')
def handle_socket_json(json):
    print(json)
    try:
        robot.json_command_handler(json)
    except Exception as e:
        print("Error handling JSON data:", e)
        return


def oled_update():
    global server_ip
    while True:
        server_ip = get_ip_address()
        robot.base_oled(0, "IP:" + server_ip)
        robot.base_oled(1, "Port:5000" + str(signal_strength_cache) + "dBm")
        robot.base_oled(2, time.time())
        robot.base_oled(3, robot_name)
        time.sleep(1)


if __name__ == '__main__':
    robot.play_random_audio("robot_started", False)
    robot.set_led_mode_on()
    oled_update_thread = threading.Thread(target=oled_update, daemon=True)
    oled_update_thread.start()
    time.sleep(0.5)
    robot.set_led_mode_off()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)