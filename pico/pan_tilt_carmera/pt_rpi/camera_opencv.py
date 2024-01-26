import time
import os

import cv2
import numpy as np
from collections import deque
import math

from base_camera import BaseCamera
from base_ctrl import BaseController
import datetime

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

import threading
import imutils
import yaml

# import audio_ctrl

curpath = os.path.realpath(__file__)
thisPath = os.path.dirname(curpath)
with open(thisPath + '/config.yaml', 'r') as yaml_file:
    f = yaml.safe_load(yaml_file)

base = BaseController('/dev/serial0', 115200)
base.lights_ctrl(0, 0)

faceCascade = cv2.CascadeClassifier(thisPath + '/haarcascade_frontalface_default.xml')

default_resolutions = {
    "1944P": (2592, 1944),
    "1080P": (1920, 1080),
     "960P": (1280, 960),
     "480P": (640, 480),
     "240P": (320, 240)
}

resolution_to_set = default_resolutions["480P"]

set_new_resolution_flag = False
video_path = thisPath + '/videos/'
photo_path = thisPath + '/static/'
photo_filename = '/static/'

video_record_fps = 30
video_filename = '/videos/video.mp4'
set_video_record_flag = False
get_frame_flag = False
frame_scale = 1.0

cv_mode = f['code']['cv_none']
feedback_interval = f['sbc_config']['feedback_interval']

led_mode_fb = 0 # 0:off 1:auto 2:on
base_light_fb = 0
detection_reaction_flag = f['code']['re_none']
frame_rate = 0
base_light_pwm = 0
head_light_pwm = 0
cv_movtion_lock_flag = True
gimbal_x = 0
gimbal_y = 0

base_info_feedback_json = {'pan':0,'tilt':0,'v':0}


def get_feedback():
    global base_info_feedback_json
    while True:
        try:
            data_recv_buffer = base.on_data_received()
            if 'v' in data_recv_buffer:
                base_info_feedback_json = data_recv_buffer
        except KeyError as e:
            # print(f"KeyError: {e}")
            pass
        except Exception as e:
            # print(f"An exception occurred: {e}")
            pass
        time.sleep(feedback_interval)


class RobotCtrlMiddleWare:
    def __init__(self):
        self.base_ctrl_speed = 25

    def json_command_handler(self, input_json):
        base.base_json_ctrl(input_json)

    def base_oled(self, line_input, text_input):
        base.base_oled(line_input, text_input)

    def set_led_mode_off(self):
        global led_mode_fb, head_light_pwm
        led_mode_fb = 0
        head_light_pwm = 0
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def set_led_mode_auto(self):
        global led_mode_fb, head_light_pwm
        led_mode_fb = 1
        head_light_pwm = 0
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def set_led_mode_on(self):
        global led_mode_fb, head_light_pwm
        led_mode_fb = 2
        head_light_pwm = 255
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def set_base_led_on(self):
        global base_light_pwm, base_light_fb
        base_light_pwm = 255
        base_light_fb = 1
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def set_base_led_off(self):
        global base_light_pwm, base_light_fb
        base_light_pwm = 0
        base_light_fb = 0
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def base_led_ctrl(self):
        global base_light_pwm, base_light_fb
        if base_light_fb:
            base_light_fb = 0
            base_light_pwm = 0
        else:
            base_light_fb = 1
            base_light_pwm = 255
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def head_led_ctrl(self):
        global head_light_pwm, led_mode_fb
        if head_light_pwm != 0:
            head_light_pwm = 0
            led_mode_fb = 0
        else:
            head_light_pwm = 255
            led_mode_fb = 2
        base.lights_ctrl(base_light_pwm, head_light_pwm)

    def play_random_audio(self, input_dirname, force_flag):
        return
        # audio_ctrl.play_random_audio(input_dirname, force_flag)



class Camera(BaseCamera):
    video_source = 0
    # frame_scale = 1
    video_record_status_flag = False
    force_record_stop_flag = False

    # opencv values
    overlay = None
    last_frame_capture_time = datetime.datetime.now()
    led_status = False
    avg = None
    last_movtion_captured = datetime.datetime.now()
    color_list = {
        'red':  [np.array([160, 20, 70]), np.array([190, 255, 255])],
        'green':[np.array([ 60, 90,100]), np.array([ 80, 255, 255])],
        'blue': [np.array([101, 50, 70]), np.array([116, 255, 210])]
    }
    if f['cv']['default_color'] in color_list:
        color_lower = color_list[f['cv']['default_color']][0]
        color_upper = color_list[f['cv']['default_color']][1]
    else:
        color_lower = np.array(f['cv']['color_lower'])
        color_upper = np.array(f['cv']['color_upper'])
    points = deque(maxlen=32)
    min_radius = f['cv']['min_radius']
    sampling_rad = f['cv']['sampling_rad']
    CMD_GIMBAL = f['cmd_config']['cmd_gimbal_ctrl']
    p1 = f['cv']['p1']
    p2 = f['cv']['p2']
    p3 = f['cv']['p3']
    aimed_error = f['cv']['aimed_error']

    cv_event = threading.Event()
    cv_event.clear()

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        global set_new_resolution_flag, photo_filename, video_filename, frame_rate, get_frame_flag

        encoder = H264Encoder(1000000)
        picam2 = Picamera2()
        picam2.configure(picam2.create_video_configuration(main={"format": 'XRGB8888', "size": (resolution_to_set[0], resolution_to_set[1])}))
        picam2.start()

        feedback_thread = threading.Thread(target=get_feedback, daemon=True)
        feedback_thread.start()

        base.gimbal_base_ctrl(2, 2, 0)
        fps_start_time = time.time()
        fps_frame_count = 0

        while True:
            if set_new_resolution_flag:
                picam2.stop()
                try:
                    picam2.configure(picam2.create_video_configuration(main={"format": 'XRGB8888', "size": (resolution_to_set[0], resolution_to_set[1])}))
                    set_new_resolution_flag = False
                    picam2.start()
                except:
                    picam2.stop()
                    picam2.start()
            else:
                pass

            img = picam2.capture_array()

            # photo corp
            if frame_scale == 1:
                pass
            elif frame_scale > 1.0:
                img_height, img_width = img.shape[:2]
                img_width_d2  = img_width/2
                img_height_d2 = img_height/2
                x_start = int(img_width_d2 - (img_width_d2//frame_scale))
                x_end   = int(img_width_d2 + (img_width_d2//frame_scale))
                y_start = int(img_height_d2 - (img_height_d2//frame_scale))
                y_end   = int(img_height_d2 + (img_height_d2//frame_scale))
                img = img[y_start:y_end, x_start:x_end]

            # opencv render
            if cv_mode != f['code']['cv_none']:
                if not Camera.cv_event.is_set():
                    Camera.cv_event.set()
                    Camera.opencv_threading(Camera, img)
                try:
                    mask = Camera.overlay.astype(bool)
                    img[mask] = Camera.overlay[mask]
                    cv2.addWeighted(Camera.overlay, 1, img, 1, 0, img)
                except:
                    pass

            # video capture
            if not set_video_record_flag and not Camera.video_record_status_flag:
                pass
            elif set_video_record_flag and not Camera.video_record_status_flag:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                video_filename = f'{video_path}video_{current_time}.mp4'
                picam2.start_recording(encoder, FfmpegOutput(video_filename))
                Camera.video_record_status_flag = True
            elif not set_video_record_flag and Camera.video_record_status_flag:
                picam2.stop_recording()
                picam2.start()
                Camera.video_record_status_flag = False

            # photo capture
            if get_frame_flag:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                photo_filename = f'{photo_path}photo_{current_time}.jpg'
                try:
                    cv2.imwrite(photo_filename, img)
                    get_frame_flag = False
                    print(photo_filename)
                except:
                    pass

            # record render
            if Camera.video_record_status_flag:
                cv2.circle(img, (15, 15), 5, (64, 64, 255), -1)

            yield cv2.imencode('.jpg', img)[1].tobytes()
            
            # get fps
            fps_frame_count += 1
            fps_current_time = time.time()
            fps_elapsed_time = fps_current_time - fps_start_time
            if fps_elapsed_time >= 2.0:
                frame_rate = fps_frame_count / fps_elapsed_time
                fps_frame_count = 0
                fps_start_time = fps_current_time


    def set_video_resolution(self, input_resolution):
        global set_new_resolution_flag, resolution_to_set
        if self.video_record_status_flag:
            return
        if input_resolution in ["1944P", "1080P", "960P", "480P", "240P"]:
            resolution_to_set = default_resolutions[input_resolution]
            set_new_resolution_flag = True
            return True
        return False


    def capture_frame(self, input_path):
        global photo_path, get_frame_flag
        photo_path = input_path
        get_frame_flag = True


    def record_video(self, input_cmd, input_path):
        global video_path, set_video_record_flag
        video_path = input_path
        if input_cmd == 1:
            set_video_record_flag = True
        else:
            set_video_record_flag = False


    def scale_frame(self, input_scale_rate):
        global frame_scale
        if input_scale_rate >= 1.0:
            frame_scale = input_scale_rate


    def set_cv_mode(self, input_mode):
        global cv_mode, set_video_record_flag
        cv_mode = input_mode
        if cv_mode == f['code']['cv_none']:
            set_video_record_flag = False
            base.lights_ctrl(base_light_pwm, 0)


    def set_detection_reaction(self, input_reaction):
        global detection_reaction_flag, set_video_record_flag
        detection_reaction_flag = input_reaction
        if detection_reaction_flag == f['code']['re_none']:
            set_video_record_flag = False


    def get_status(self):
        # try:
            # feedback_json = {
            # f['fb']['led_mode']:    led_mode_fb,
            # f['fb']['detect_type']: cv_mode,
            # f['fb']['detect_react']:detection_reaction_flag,
            # f['fb']['pan_angle']:   base_info_feedback_json['pan'],
            # f['fb']['tilt_angle']:  base_info_feedback_json['tilt'],
            # f['fb']['base_voltage']:base_info_feedback_json['v'],
            # f['fb']['video_fps']:   frame_rate,
            # f['fb']['cv_movtion_mode']: cv_movtion_lock_flag,
            # f['fb']['base_light']:  base_light_fb
            # }
        feedback_json = {
        f['fb']['led_mode']:    led_mode_fb,
        f['fb']['detect_type']: cv_mode,
        f['fb']['detect_react']:detection_reaction_flag,
        f['fb']['pan_angle']:   base_info_feedback_json['pa'],
        f['fb']['tilt_angle']:  base_info_feedback_json['ta'],
        f['fb']['base_voltage']:base_info_feedback_json['v'],
        f['fb']['video_fps']:   frame_rate,
        f['fb']['cv_movtion_mode']: cv_movtion_lock_flag,
        f['fb']['base_light']:  base_light_fb
        }

        return feedback_json
        # except:
        #     pass


    def set_pan_id(self):
        base.bus_servo_id_set(254, 2)


    def release_torque(self):
        base.bus_servo_torque_lock(254, 0)


    def middle_set(self):
        base.bus_servo_mid_set(254)


    def set_tilt_id(self):
        base.bus_servo_id_set(254, 1)


    def set_movtion_lock(self, cmd):
        global cv_movtion_lock_flag, gimbal_x, gimbal_y
        if cmd == f['code']['mc_lock']:
            cv_movtion_lock_flag = True
            gimbal_x = 0
            gimbal_y = 0
        elif cmd == f['code']['mc_unlo']:
            cv_movtion_lock_flag = False

    def gimbal_track(self, fx, fy, gx, gy):
        global gimbal_x, gimbal_y
        distance = math.sqrt((fx - gx) ** 2 + (gy - fy) ** 2)
        gimbal_x += (gx - fx)/self.p1
        gimbal_y += (fy - gy)/self.p1
        if gimbal_x > 180:
            gimbal_x = 180
        elif gimbal_x < -180:
            gimbal_x = -180
        if gimbal_y > 90:
            gimbal_y = 90
        elif gimbal_y < -30:
            gimbal_y = -30
        gimbal_spd = int(distance*self.p2)
        gimbal_acc = int(distance/self.p3)
        if gimbal_acc < 1:
            gimbal_acc = 1
        if gimbal_spd < 1:
            gimbal_spd = 1
        base.base_json_ctrl({"T":self.CMD_GIMBAL,"X":gimbal_x,"Y":gimbal_y,"SPD":gimbal_spd,"ACC":gimbal_acc})
        return distance


    def cv_detect_movition(self, img):
        global set_video_record_flag, get_frame_flag
        timestamp = datetime.datetime.now()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.avg is None:
            self.avg = gray.copy().astype("float")
            return
        try:
            cv2.accumulateWeighted(gray, self.avg, 0.5)
        except:
            return
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # loop over the contours
        overlay_buffer = np.zeros_like(img)
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 2000:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (mov_x, mov_y, mov_w, mov_h) = cv2.boundingRect(c)
            cv2.rectangle(overlay_buffer, (mov_x, mov_y), (mov_x + mov_w, mov_y + mov_h), (128, 255, 0), 1)
            self.last_movtion_captured = timestamp

            if(timestamp - self.last_frame_capture_time).seconds >= 1:
                if detection_reaction_flag == f['code']['re_none']:
                    pass
                elif detection_reaction_flag == f['code']['re_capt']: 
                    get_frame_flag = True
                elif detection_reaction_flag == f['code']['re_reco']:
                    set_video_record_flag = True
                self.last_frame_capture_time = datetime.datetime.now()
            
        if (timestamp - self.last_movtion_captured).seconds >= 1.5:
            if detection_reaction_flag == f['code']['re_reco']:
                if(timestamp - self.last_frame_capture_time).seconds >= 5:
                    set_video_record_flag = False
        self.overlay = overlay_buffer


    def cv_detect_faces(self, img):
        global set_video_record_flag, get_frame_flag
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
                gray_img,     
                scaleFactor=1.2,
                minNeighbors=5,     
                minSize=(20, 20)
            )
        overlay_buffer = np.zeros_like(img)
        if len(faces):
            if led_mode_fb == 1:
                if not self.led_status:
                    base.lights_ctrl(base_light_pwm, 255)
                    self.led_status = True

            for (x,y,w,h) in faces:
                cv2.rectangle(overlay_buffer,(x,y),(x+w,y+h),(64,128,255),1)

            if(datetime.datetime.now() - self.last_frame_capture_time).seconds >= 3:
                if detection_reaction_flag == f['code']['re_none']:
                    pass
                elif detection_reaction_flag == f['code']['re_capt']:
                    get_frame_flag = True
                elif detection_reaction_flag == f['code']['re_reco']:
                    set_video_record_flag = True
                self.last_frame_capture_time = datetime.datetime.now()
        else:
            if led_mode_fb == 1:
                if self.led_status:
                    base.lights_ctrl(base_light_pwm, 0)
                    self.led_status = False

            if detection_reaction_flag == f['code']['re_reco']:
                if(datetime.datetime.now() - self.last_frame_capture_time).seconds >= 5:
                    set_video_record_flag = False
        self.overlay = overlay_buffer


    def cv_detect_objects(self, img):
        overlay_buffer = np.zeros_like(img)
        cv2.putText(overlay_buffer, 'CV_OBJS', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self.overlay = overlay_buffer


    def cv_detect_color(self, img):
        global head_light_pwm
        blurred = cv2.GaussianBlur(img, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        mask = cv2.erode(mask, None, iterations=5)
        mask = cv2.dilate(mask, None, iterations=5)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        overlay_buffer = np.zeros_like(img)

        height, width = img.shape[:2]
        center_x, center_y = width // 2, height // 2

        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), self.sampling_rad, (255), thickness=-1)

        masked_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        masked_hsv_pixels = masked_hsv[mask == 255]
        lower_hsv = np.min(masked_hsv_pixels, axis=0)
        upper_hsv = np.max(masked_hsv_pixels, axis=0)

        cv2.putText(overlay_buffer, 'UPPER: {}'.format(upper_hsv), (center_x+50, center_y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(overlay_buffer, 'LOWER: {}'.format(lower_hsv), (center_x+50, center_y+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.circle(overlay_buffer, (center_x, center_y), self.sampling_rad, (64, 255, 64), 1)

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > self.min_radius:
                if not cv_movtion_lock_flag:
                    distance = self.gimbal_track(self, center_x, center_y, center[0], center[1])
                    if distance < self.aimed_error:
                        head_light_pwm = 3
                        base.lights_ctrl(base_light_pwm, head_light_pwm)
                    else:
                        head_light_pwm = 0
                        base.lights_ctrl(base_light_pwm, head_light_pwm)
                    cv2.putText(overlay_buffer, 'DIF: {}'.format(distance), (center_x+50, center_y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(overlay_buffer, (int(x), int(y)), int(radius),
                    (128, 255, 255), 1)
                cv2.circle(overlay_buffer, center, 3, (128, 255, 255), -1)
                cv2.line(overlay_buffer, center, (center_x, center_y), (0, 0, 255), 1)
                cv2.putText(overlay_buffer, 'RAD: {}'.format(radius), (center_x+50, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                self.points.appendleft(center)
            else:
                head_light_pwm = 0
                base.lights_ctrl(base_light_pwm, head_light_pwm)
                self.points.appendleft(None)

            for i in range(1, len(self.points)):
                if self.points[i-1] is None or self.points[i] is None:
                    continue
                cv2.line(overlay_buffer, self.points[i - 1], self.points[i], (255, 255, 128), 1)

        self.overlay = overlay_buffer


    def cv_detect_hand(self, img):
        overlay_buffer = np.zeros_like(img)
        cv2.putText(overlay_buffer, 'CV_HAND', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self.overlay = overlay_buffer


    def cv_auto_drive(self, img):
        overlay_buffer = np.zeros_like(img)
        cv2.putText(overlay_buffer, 'CV_DRIVE', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self.overlay = overlay_buffer


    def cv_process(self, frame):
        cv_mode_list = {
        f['code']['cv_moti']: self.cv_detect_movition,
        f['code']['cv_face']: self.cv_detect_faces,
        f['code']['cv_objs']: self.cv_detect_objects,
        f['code']['cv_clor']: self.cv_detect_color,
        f['code']['cv_hand']: self.cv_detect_hand,
        f['code']['cv_auto']: self.cv_auto_drive
        }
        cv_mode_list[cv_mode](self, frame)
        self.cv_event.clear()


    def opencv_threading(self, input_img):
        cv_thread = threading.Thread(target=self.cv_process, args=(self, input_img,))
        cv_thread.start()