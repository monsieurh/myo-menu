# myo-menu
A simple audio menu handler for Linux using Myo.
Create a menu in JSON, use it for anything. No graphical feedback, no screen needed !
Released under MIT license

Developed under Fedora Linux 21. Tested on personal laptop and Raspberry Pi B+

# Overview
This is a program that provides a simple way to interact with a Linux computer using Thalmic lab's Myo armband. 
The goal is to provide a simple way to describe a menu (using JSON file) and be able to navigate through it with 
audio feedback from the computer. For now it can handle two type of actions :
- Running an arbitrary command
- Running a command and reading the output back to the user

# Requirements
The following software are required to make the app run:
- avplay (or ffmpeg)
- pySerial
- enum34
- python 2.7+
- pyAudio
- pydub

Myo armband firmwmare >= 1.X

# Installation
```
git clone https://github.com/monsieurh/myo-menu.git
cd myo-menu
git submodule init
sudo pip install -r requirements.txt
```
Additional packages may be needed depending on your Linux installation (ffmpeg/avplay). 
Feel free to contact me to add them in this readme.

## Optional
Open and edit the file 'default_menu.json' to fit your needs

# Usage
Simply run ```python main.py``` or ```./main.py``` to start the program. 
Perform the synchronisation gesture, and navigate the menu.

## Controls
- WAVE-IN : Previous item
- WAVE-OUT : Next item
- FINGERSPREAD : Parent node
- FIST : Enter submenu/execute action

# Future
## Known bugs
The Myo seems to loose synchronisation when the output of an action is read back to the user [FIXED]

## Features
- Controls configuration through JSON file
- Locale configuration through JSON file
- Action callback to launch an arbitrary python command in the main loop
- Handle parameters in JSON menu file
- Visualization of some kind ?

# Libs
This program uses 
[GoogleTTS by Hung Truong](http://www.hung-truong.com/blog/2013/04/26/hacking-googles-text-to-speech-api/) 
released under the MIT license to generate spoken sounds. ([source](https://github.com/hungtruong/Google-Translate-TTS))


It also relies on [myo-raw](https://github.com/dzhu/myo-raw) for Linux-Myo communication in python (MIT license). It had
to be tweaked to match most recent's firmware though


