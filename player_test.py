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
import termios

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
        if i >= len(files): i = 0


def peek_songs(n):
    nexti = i + 1
    if nexti >= len(files): nexti = 0
    return map(Song, (files[nexti:] + files[:nexti])[:n])


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


def prepare_stdin():
    fd = sys.stdin.fileno()

    if os.isatty(fd):
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
        # http://www.unixguide.net/unix/programming/3.6.2.shtml
        new[6][termios.VMIN] = 0
        new[6][termios.VTIME] = 1

        termios.tcsetattr(fd, termios.TCSANOW, new)
        termios.tcsendbreak(fd, 0)

        import atexit
        atexit.register(lambda: termios.tcsetattr(fd, termios.TCSANOW, old))

        print("Console control:")
        print("  <space>:        play / pause")
        print("  <left>/<right>: seek back/forward by 10 secs")
        print("  <return>:       next song")
        print("  <q>:            quit")


def getchar():
    fd = sys.stdin.fileno()
    ch = os.read(fd, 7)
    return ch


prepare_stdin()

while True:
    sys.stdout.write("\r\033[K")  # clear line
    if player.playing:
        sys.stdout.write("playing, ")
    else:
        sys.stdout.write("paused, ")
    curSong = player.curSong
    if curSong:
        url = os.path.basename(curSong.url)
        if len(url) > 40: url = url[:37] + "..."
        sys.stdout.write(
            url + " : " +
            format_time(player.curSongPos) + " / " +
            format_time(player.curSongLen))
    else:
        sys.stdout.write("no song")
    sys.stdout.flush()

    ch = getchar()
    if ch == b"\x1b[D":  # left
        player.seekRel(-10)
    elif ch == b"\x1b[C":  # right
        player.seekRel(10)
    elif ch == b"\x1b[A":  # up
        pass
    elif ch == b"\x1b[B":  # down
        pass
    elif ch == b"\n":  # return
        player.nextSong()
    elif ch == b" ":
        player.playing = not player.playing
    elif ch == b"q":
        print()
        sys.exit(0)
    sys.stdout.flush()
