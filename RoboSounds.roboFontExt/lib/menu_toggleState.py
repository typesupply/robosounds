from mojo.roboFont import OpenWindow
from robosounds import RoboSoundsController


if RoboSoundsController.isListening():
	RoboSoundsController.stopListening()
else:
	RoboSoundsController.startListening()