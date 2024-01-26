import pygame
import os
import random
import threading
import time
import yaml
import pyttsx3

curpath = os.path.realpath(__file__)
thisPath = os.path.dirname(curpath)
with open(thisPath + '/config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

current_path = os.path.abspath(os.path.dirname(__file__))
pygame.mixer.init()
pygame.mixer.music.set_volume(config['audio_config']['default_volume'])
play_audio_event = threading.Event()
min_time_bewteen_play = config['audio_config']['min_time_bewteen_play']

engine = pyttsx3.init()
engine.setProperty('rate', config['audio_config']['speed_rate'])


def play_audio(input_audio_file):
	pygame.mixer.music.load(input_audio_file)
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy():
		pass
	time.sleep(min_time_bewteen_play)
	play_audio_event.clear()


def play_random_audio(input_dirname, force_flag):
	if play_audio_event.is_set() and not force_flag:
		return
	audio_files = [f for f in os.listdir(current_path + "/sounds/" + input_dirname) if f.endswith((".mp3", ".wav"))]
	audio_file = random.choice(audio_files)
	play_audio_event.set()
	audio_thread = threading.Thread(target=play_audio, args=(current_path + "/sounds/" + input_dirname + "/" + audio_file,))
	audio_thread.start()


def get_mixer_status():
	return pygame.mixer.music.get_busy()


def set_audio_volume(input_volume):
	if input_volume > 1:
		input_volume = 1
	elif input_volume < 0:
		input_volume = 0
	pygame.mixer.music.set_volume(input_volume)


def set_min_time_between(input_time):
	global min_time_bewteen_play
	min_time_bewteen_play = input_time


def play_speech(input_text):
	engine.say(input_text)
	engine.runAndWait()
	play_audio_event.clear()


def play_speech_therad(input_text):
	if play_audio_event.is_set():
		return
	play_audio_event.set()
	speech_thread = threading.Thread(target=play_speech, args=(input_text,))
	speech_thread.start()


if __name__ == '__main__':
	while True:
		engine.say("this is a test")
		engine.runAndWait()
		time.sleep(1)