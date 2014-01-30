# Music player Python module

This Python module provides a high-level core Music player interface where you are supposed to provide all the remaining high-level logic like the user interface, the playlist logic and the audio data.

## Example

A very simple player:

```
import musicplayer, sys, os, fnmatch, random, pprint, Tkinter

class Song:
	def __init__(self, fn):
		self.url = fn
		self.f = open(fn)
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
def getFiles(path):
	for f in sorted(os.listdir(path), key=lambda k: random.random()):
		f = os.path.join(path, f)
		if os.path.isdir(f): getFiles(f) # recurse
		if len(files) > 1000: break # break if we have enough
		if fnmatch.fnmatch(f, '*.mp3'): files.append(f)
getFiles(os.path.expanduser("~/Music"))
random.shuffle(files) # shuffle some more

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

# Create our Music Player.
player = musicplayer.createPlayer()
player.outSamplerate = 96000 # support high quality :)
player.queue = songs()
player.peekQueue = peekSongs

# Setup a simple GUI.
window = Tkinter.Tk()
window.title("Music Player")
songLabel = Tkinter.StringVar()

def onSongChange(**kwargs): songLabel.set(pprint.pformat(player.curSongMetadata))
def cmdPlayPause(*args): player.playing = not player.playing
def cmdNext(*args): player.nextSong()

Tkinter.Label(window, textvariable=songLabel).pack()
Tkinter.Button(window, text="Play/Pause", command=cmdPlayPause).pack()
Tkinter.Button(window, text="Next", command=cmdNext).pack()

player.onSongChange = onSongChange
player.playing = True # start playing
window.mainloop()

```


## Description

It provides a player object which represents the player. It needs a generator `player.queue` which yields `Song` objects which provide a way to read file data and seek in the file. See the source code for further detailed reference.

It has the following functionality:

* Plays audio data via the player object. Uses [FFmpeg](http://ffmpeg.org/) for decoding and [PortAudio](http://www.portaudio.com/) for playing.
* Of course, the decoding and playback is done in seperate threads. You can read about that [here](http://sourceforge.net/p/az-music-player/blog/2014/01/improving-the-audio-callback-removing-audio-glitches/).
* Supports any sample rate via `player.outSamplerate`. The preferred sound device is set via `player.preferredSoundDevice`. Get a list of all sound devices via `getSoundDevices()`.
* Can modify the volume via `player.volume` and also `song.gain` (see source code for details).
* Prevents clipping via a smooth limiting functions which still leaves most sounds unaffected and keeps the dynamic range (see `smoothClip`).
* Can calculate the [ReplayGain](http://www.replaygain.org/) value for a song (see `pyCalcReplayGain`). This is as far as I know the only other implementation of ReplayGain despite the original from [mp3gain](http://mp3gain.sourceforge.net/) ([gain_analysis.c](http://mp3gain.cvs.sourceforge.net/viewvc/mp3gain/mp3gain/gain_analysis.c?view=markup)).
* Can calculate the [AcoustId](http://acoustid.org/) audio fingerprint (see `pyCalcAcoustIdFingerprint`). This one is also used by [MusicBrainz](http://musicbrainz.org/). It uses the [Chromaprint](http://acoustid.org/chromaprint) lib for implementation.
* Provides a simple way to access the song metadata.
* Provides a way to calculate a visual thumbnail for a song which shows the amplitude and the spectral centroid of the frequencies per time (see `pyCalcBitmapThumbnail`). Inspired by [this project](https://github.com/endolith/freesound-thumbnailer/).


## Features

* open source (simplified BSD license, see [License.txt](https://github.com/albertz/music-player/blob/master/License.txt))
* very simple interface
* support of most important sound formats (MP3, Flac, Ogg Vorbis, WMA, AAC / ALAC m4a, ...)
* ReplayGain / audio volume normalization
* [AcoustID](http://acoustid.org) fingerprint
* [Gapless playback](http://en.wikipedia.org/wiki/Gapless_playback)


## Installation

To get the source working, you need these requirements (e.g. install on MacOSX via Homebrew):

* ffmpeg
* portaudio
* chromaprint

(Debian/Ubuntu: `apt-get install python-dev libsnappy-dev libtool yasm libchromaprint-dev portaudio19-dev libboost-dev`. FFmpeg in Debian/Ubuntu is too old (lacks libswresample), so either do `add-apt-repository ppa:jon-severinsson/ffmpeg && apt-get update && apt-get install libavformat-dev libswresample-dev` or install it from source. [Chromaprint](http://acoustid.org/chromaprint) depends on FFmpeg, so if you have a custom FFmpeg install, you might also want to install that manually. `./configure && make && sudo make install` should work for FFmpeg and PortAudio. You might also want to use `--enable-shared` for FFmpeg. `cmake . && sudo make install` for Chromaprint.)

Then call `./compile.py` to build the Python modules (it will build the Python modules `ffmpeg.so` and `leveldb.so`).


## Similar projects

* *Overview* in Python Wiki: [Audio modules](https://wiki.python.org/moin/Audio) and [Music software](https://wiki.python.org/moin/PythonInMusic).

* [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/). MIT License. PortAudio wrapper. Thus, pretty low-level and no decoding functionality. Last update from 2012.
* [PyFFmpeg](http://code.google.com/p/pyffmpeg/). LGPL. FFmpeg wrapper. Thus, prettylow-level and no sound output. You could probably glue PyFFmpeg and PyAudio together for something useful but I expect it to be quite unstable and too slow. Basically, tis glue is done in C++ in this module.
* [GStreamer Python Bindings](http://gstreamer.freedesktop.org/modules/gst-python.html). GStreamer is powerful but still too limited as a cross-platform music player backend solution. Quite heavy. That was my intuition. Maybe it's wrong and it would have been a perfect solution. But I think, in contrast, this module does a lot of things in a more compact and automatic/simpler way and at the same time provides more music player centric features.
* [Beets](http://beets.radbox.org/). In it's core, it is a music library manager and manages the metadata. It can calculate ReplayGain and AcoustID fingerprint. Via BPD plugin, it becomes a MPD compatible daemon player, based on GStreamer.

### Probably dead projects

* [PyMedia](http://pymedia.org/). LGPL, GPL. FFmpeg-based encoding/decoding of audio+video, sound input/output via OSS/Waveout/Wavein. Unfornutaley not well tuned for usage in a high-quality music player. Last update from 2006.
* [Audiere](http://audiere.sourceforge.net/). LGPL. High-level audio API, supports many sound formats and sound output on Windows/Linux. Last update from 2006.


