#!/bin/env python
# coding=utf-8

from myo.myo import MyoRaw
from myo.myo_raw import Pose
from sounds.generator import AudioFileManager
from menu import Branch, Leaf
from pydub.playback import play
import menu


class InputManager(object):
    class DefaultCallback(object):
        def __call__(self, pose):
            pass

    def __init__(self):
        self._callbacks = {pose: [InputManager.DefaultCallback()] for pose in Pose}

    def on_pose(self, pose):
        if pose in self._callbacks.keys():
            for action in self._callbacks[pose]:
                action(pose)

    def add_handler(self, pose, action):
        if pose in self._callbacks.keys():
            self._callbacks[pose].append(action)

    def add_generic_handler(self, action):
        for pose in self._callbacks.keys():
            self._callbacks[pose].append(action)

    def reset(self, pose):
        if pose in self._callbacks.keys():
            self._callbacks[pose] = [InputManager.DefaultCallback()]

    def disable(self, pose):
        self._callbacks.pop(pose)


def on_arm(arm, direction):
    print "Arm:", arm, "direction:", direction
    say_selected(None)


current_menu = menu.MenuFactory.create("default_menu.json")
print "Total menu items:", current_menu.get_len()
print "Menu depth:", current_menu.get_depth()

nav = menu.MenuNavigator(current_menu)
im = InputManager()
am = AudioFileManager("en", "/tmp/")


def vibrate_one(pose):
    m.vibrate(1)


def print_current_node(pose):
    print "Pose:", pose
    print "Current:", nav.get_selected().parent.name
    print "Selected:", nav.get_selected().name


def print_pose(pose):
    print "Pose:", pose


def print_pos(pose):
    print nav.get_selected().parent.name
    to_print = []
    for child in nav.get_selected().parent.children:
        if child == nav.get_selected():
            to_print.append("[{}]".format(child.name))
        else:
            to_print.append(child.name)
    print ' '.join(to_print)


def say_selected(pose):
    sound = am.get(nav.get_selected().name)
    play(sound)


def say_current(pose):
    sound = am.get(nav.get_selected().parent.name)
    play(sound)
    sound = am.get(nav.get_selected().name)
    play(sound)


def say_selected_desc(pose):
    sound = am.get(nav.get_selected().desc)
    play(sound)


def down_wrapper(pose):
    if isinstance(nav.get_selected(), Branch):
        nav.down()
        say_current(pose)
    else:
        if nav.get_selected().command_type == "execute":
            s = am.get("Executing command")
            play(s)
            nav.down()
        else:  # Read-output
            output = nav.down()
            if output:
                sound = am.get(output)
                play(sound)


to_build = current_menu.get_strings()
am.lazy_build_files(to_build)

im.disable(Pose.REST)

im.add_handler(Pose.FINGERS_SPREAD, nav.up)
im.add_handler(Pose.FINGERS_SPREAD, say_current)

im.add_handler(Pose.THUMB_TO_PINKY, say_selected_desc)

im.add_handler(Pose.FIST, vibrate_one)
im.add_handler(Pose.FIST, down_wrapper)

im.add_handler(Pose.WAVE_IN, nav.left)
im.add_handler(Pose.WAVE_IN, say_selected)

im.add_handler(Pose.WAVE_OUT, nav.right)
im.add_handler(Pose.WAVE_OUT, say_selected)

im.add_generic_handler(print_pose)

m = MyoRaw()
m.add_arm_handler(on_arm)
m.add_pose_handler(im.on_pose)
m.connect()

try:
    while True:
        m.run(30)
except KeyboardInterrupt:
    print "Disconnecting..."
    m.disconnect()
    print "Exiting..."
    exit(0)