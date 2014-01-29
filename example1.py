#!/usr/bin/env python2

import musicplayer, os, fnmatch, random

class Song:
	def __init__(self, fn):
		self.url = fn
		self.f = open(fn)		
	def __eq__(self, other):
		return self.url == other.url
	def readPacket(self, bufSize):
		return self.f.read(bufSize)
	def seekRaw(self, offset, whence):
		r = self.f.seek(offset, whence)
		return self.f.tell()

path = os.path.expanduser("~/Music")
files = [os.path.join(path, f)
	for dirpath, dirnames, files in os.walk(path)
	for f in fnmatch.filter(files, '*.mp3')]
random.shuffle(files)

i = 0

def songs():
	global i, files
	while True:
		yield Song(files[i])
		i += 1
		if i >= len(files): i = 0

def peekSongs(n):
	nexti = i + 1
	if nexti >= len(files): nexti = 0
	return map(Song, (files[nexti:] + files[:nexti])[:n])

player = musicplayer.createPlayer()
player.outSamplerate = 96000 # support high quality :)
player.queue = songs()
player.peekQueue = peekSongs

player.playing = True
while True: pass # keep playing

