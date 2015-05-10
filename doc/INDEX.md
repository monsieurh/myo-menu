# Technical documentation

## Overview
### Diagrams
![classes](https://github.com/monsieurh/myo-menu/tree/documentation/doc/packages_myo_menu.png "Packages")

![classes](https://github.com/monsieurh/myo-menu/tree/documentation/doc/classes_myo_menu.png "Classes")

## Modules
### Myo
The ```myo/``` folder is a fork of dzhu's [myo-raw](https://github.com/dzhu/myo-raw) compatible with Myo's firmware version 1.X and up.

### Sounds
The ```sounds/``` folder is a wrapper for Hung Truong's [GoogleTTS hack](https://github.com/hungtruong/Google-Translate-TTS). It adds a few neat features.
1. Ability to generate multiple files using Threads (see GoogleTTSGenerator.generate_sounds_threaded)
2. Ability to lazily generate sounds:
    - For each sound a hash is calculated (see Hasher object)
    - If the file with this hash exists reuse it
    - If not, generate it
3. Ability to handle different file format (Conversion from mp3 to X using pydub)

### Menu
the ```menu.py``` file holds the classes responsible for the menu management. A Menu holds an instance of MenuItem as a root.
A MenuItem is an abstract class that can be either a Branch (having children) or a Leaf (no children but a command).

Each node has a few convenient function to get all the strings ('name' and 'desc') the depth and the size of the tree/subtree.

*To be continued*