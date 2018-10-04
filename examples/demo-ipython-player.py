#!/usr/bin/env python3
# MusicPlayer, https://github.com/albertz/music-player
# Copyright (c) 2012, Albert Zeyer, www.az2000.de
# All rights reserved.
# This code is under the 2-clause BSD license, see License.txt in the root directory of this project.

from __future__ import print_function
import sys
import os
import random
import fnmatch
import IPython

try:
    import better_exchook
    better_exchook.install()
except ImportError:
    pass  # doesnt matter

try:
    import faulthandler
    faulthandler.enable(all_threads=True)
except ImportError:
    print("note: module faulthandler not available")

# Our parent path might contain a self-build musicplayer module. Use that one.
sys.path.insert(0, os.path.abspath((os.path.dirname(__file__) or ".") + "/.."))

import musicplayer

print("Module:", musicplayer.__file__)

# FFmpeg log levels: {0:panic, 8:fatal, 16:error, 24:warning, 32:info, 40:verbose}
musicplayer.setFfmpegLogLevel(20)


class Song:
    def __init__(self, fn):
        self.url = fn
        self.f = open(fn, "rb")

    def __eq__(self, other):
        return self.url == other.url

    def readPacket(self, bufSize):
        s = self.f.read(bufSize)
        # print "readPacket", self, bufSize, len(s)
        return s

    def seekRaw(self, offset, whence):
        r = self.f.seek(offset, whence)
        # print "seekRaw", self, offset, whence, r, self.f.tell()
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
        if i >= len(files):
            i = 0


def peek_songs(n):
    next_i = i + 1
    if next_i >= len(files):
        next_i = 0
    return map(Song, (files[next_i:] + files[:next_i])[:n])


player = musicplayer.createPlayer()
player.outSamplerate = 48000
player.queue = songs()
player.peekQueue = peek_songs
player.playing = True


def format_time(t):
    if t is None:
        return "?"
    mins = int(t // 60)
    t -= mins * 60
    hours = mins // 60
    mins -= hours * 60
    if hours:
        return "%02i:%02i:%02.0f" % (hours, mins, t)
    return "%02i:%02.0f" % (mins, t)


if __name__ == "__main__":
    print("Starting IPython shell.")
    print("Try setting/calling these:")
    for attr in dir(player):
        print("  player.%s = %r" % (attr, getattr(player, attr)))
    for attr in dir(musicplayer):
        print("  musicplayer.%s = %r" % (attr, getattr(musicplayer, attr)))
    IPython.start_ipython(user_ns=locals())
