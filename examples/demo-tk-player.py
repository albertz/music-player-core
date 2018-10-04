#!/usr/bin/env python3

from __future__ import print_function
import sys
import os
import fnmatch
import random
import pprint
import tkinter

# Our parent path might contain a self-build musicplayer module. Use that one.
sys.path.insert(0, os.path.abspath((os.path.dirname(__file__) or ".") + "/.."))

import musicplayer

print("Module:", musicplayer.__file__)


class Song:
    def __init__(self, fn):
        self.url = fn
        self.f = open(fn, "rb")

    # `__eq__` is used for the peek stream management
    def __eq__(self, other):
        return self.url == other.url

    # this is used by the player as the data interface
    def readPacket(self, bufSize):
        return self.f.read(bufSize)

    def seekRaw(self, offset, whence):
        r = self.f.seek(offset, whence)
        return self.f.tell()


files = []


def get_files(path):
    for f in sorted(os.listdir(path), key=lambda k: random.random()):
        f = os.path.join(path, f)
        if os.path.isdir(f):
            get_files(f)  # recurse
        if len(files) > 1000:
            break  # break if we have enough
        if fnmatch.fnmatch(f, '*.mp3'):
            files.append(f)


get_files(os.path.expanduser("~/Music"))
random.shuffle(files)  # shuffle some more
files = sys.argv[1:] + files
assert files, "give me some files or fill-up ~/Music"

i = 0


def songs():
    global i, files
    while True:
        yield Song(files[i])
        i += 1
        if i >= len(files): i = 0


def peek_songs(n):
    next_i = i + 1
    if next_i >= len(files):
        next_i = 0
    return map(Song, (files[next_i:] + files[:next_i])[:n])


# Create our Music Player.
player = musicplayer.createPlayer()
player.outSamplerate = 96000  # support high quality :)
player.queue = songs()
player.peekQueue = peek_songs

# Setup a simple GUI.
tk_window = tkinter.Tk()
tk_window.title("Music Player")
tk_song_name = tkinter.StringVar()
tk_song_time = tkinter.StringVar()
tk_song_label = tkinter.StringVar()


def on_song_change(**kwargs):
    tk_song_name.set(os.path.basename(player.curSong.url))
    tk_song_label.set(pprint.pformat(player.curSongMetadata))


def cmd_play_pause(*args): player.playing = not player.playing


def cmd_seek_back(*args): player.seekRel(-10)


def cmd_seek_fwd(*args): player.seekRel(10)


def cmd_next(*args): player.nextSong()


def refresh_time():
    tk_song_time.set("Time: %.1f / %.1f" % (player.curSongPos or -1, player.curSongLen or -1))
    tk_window.after(10, refresh_time)  # every 10ms


tkinter.Button(tk_window, text="Play/Pause", command=cmd_play_pause).pack()
tkinter.Button(tk_window, text="Seek -10", command=cmd_seek_back).pack()
tkinter.Button(tk_window, text="Seek +10", command=cmd_seek_fwd).pack()
tkinter.Button(tk_window, text="Next", command=cmd_next).pack()
tkinter.Label(tk_window, textvariable=tk_song_name).pack()
tkinter.Label(tk_window, textvariable=tk_song_time).pack()
tkinter.Label(tk_window, textvariable=tk_song_label).pack()

refresh_time()

player.onSongChange = on_song_change
player.playing = True  # start playing
tk_window.mainloop()
