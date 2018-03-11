# peakrmsmeter

Peak and RMS meter for audio files. Takes an audio file and plots peaks and RMS, unweighted and a-weighted.
Bear with me, this is a quick and dirty hack, but with comments !

If only wave are used as input, ffmpeg is optional.

Since pictures tell a thousand words:
![Example picture](example.png?raw=true)

Prerequisites
-------------
- python3 (2 might work fine, too)
- ffmpeg (optional)

### Modules for python

- pip (package manager for python)
- matplotlib (version 2.x preferable)
- librosa
- numpy
- scipy


Installation
------------
Installation is straight forward, especially on linux systems (I know, not the usual domain for audio engineers).

### Arch Linux
```
sudo pacman -S python python-numpy python-scipy python-matplotlib python-pip ffmpeg
sudo pip install librosa
```
This should install python and all necessary prerequisites.


### Windows
Install [WinPython](https://winpython.github.io/) and add python to the path. Recommended is verson 3.6+ and x64.
Then open a command line by clicking start and typing "cmd", then press Enter.

Type the following command to install librosa (and press Enter):
```
python -m pip install librosa
```

Download and install [ffmpeg](https://www.ffmpeg.org/) (optional).
Add ffmpeg to the windows path, so it can be invoked by librosa.


Usage
-----
Usage for Linux and Windows. Replace the path to the audio file.

### Linux

Open a terminal, navigate to the git repository and type:
```
python peakrms.py path/to/someaudiofile.wav
```
For a help message type:
```
python -h
```

### Windows
Open a command line by clicking start and typing "cmd". Navigate to the git directory and type:
```
python peakrms.py path\to\someaudiofile.wav
```

