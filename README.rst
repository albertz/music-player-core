==========================
Music player Python module
==========================

This Python module provides a high-level core Music player interface where you are supposed to provide all the remaining high-level logic like the user interface, the playlist logic and the audio data.

Example
=======

A very simple player with gapless playback:

.. code-block:: python

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



Description
===========

It provides a player object which represents the player. It needs a generator `player.queue` which yields `Song` objects which provide a way to read file data and seek in the file. See the source code for further detailed reference.

It has the following functionality:

* open source (simplified BSD license, see `License.txt <https://github.com/albertz/music-player-core/blob/master/License.txt>`_)
* very simple interface
* support of most important sound formats (MP3, Flac, Ogg Vorbis, WMA, AAC / ALAC m4a, ...)

* Plays audio data via the player object. Uses `FFmpeg <http://ffmpeg.org/>`_ for decoding and `PortAudio <http://www.portaudio.com/>`_ for playing.
* Of course, the decoding and playback is done in seperate threads. You can read about that `here <http://sourceforge.net/p/az-music-player/blog/2014/01/improving-the-audio-callback-removing-audio-glitches/>`_.
* Supports any sample rate via ``player.outSamplerate``. The preferred sound device is set via ``player.preferredSoundDevice``. Get a list of all sound devices via ``getSoundDevices()``.
* Can modify the volume via ``player.volume`` and also ``song.gain`` (see source code for details).
* Prevents clipping via a smooth limiting functions which still leaves most sounds unaffected and keeps the dynamic range (see ``smoothClip``).
* `ReplayGain <http://www.replaygain.org/>`_ (for audio volume normalization) (see ``pyCalcReplayGain``). This is as far as I know the only other implementation of ReplayGain despite the original from `mp3gain <http://mp3gain.sourceforge.net/>`_ (`gain_analysis.c <http://mp3gain.cvs.sourceforge.net/viewvc/mp3gain/mp3gain/gain_analysis.c?view=markup>`_).
* `AcoustId <http://acoustid.org/>`_ audio fingerprint (see ``pyCalcAcoustIdFingerprint``). This one is also used by `MusicBrainz <http://musicbrainz.org/>`_. It uses the `Chromaprint <http://acoustid.org/chromaprint>`_ lib for implementation.
* Provides a simple way to access the song metadata.
* Provides a way to calculate a visual thumbnail for a song which shows the amplitude and the spectral centroid of the frequencies per time (see ``pyCalcBitmapThumbnail``). Inspired by `this project <https://github.com/endolith/freesound-thumbnailer/>`_.
* `Gapless playback <http://en.wikipedia.org/wiki/Gapless_playback>`_


Usages
======

The main usage is probably in the `MusicPlayer project <http://albertz.github.io/music-player/>`_ - a full featured high-quality music player.


Installation
============

To get the source working, you need these requirements:

* boost >=1.55.0
* ffmpeg >= 2.0 (including libswresample)
* portaudio >=v19
* chromaprint

Debian/Ubuntu
+++++++++++++

::

    apt-get install python-dev libsnappy-dev libtool yasm libchromaprint-dev portaudio19-dev libboost-dev

FFmpeg in Debian/Ubuntu is too old (lacks libswresample), so either do::

    add-apt-repository ppa:jon-severinsson/ffmpeg
    apt-get update
    apt-get install libavformat-dev libswresample-dev
    
or install it from source.

MacOSX
++++++

::

	brew install boost	
	brew install portaudio
	brew install ffmpeg
	brew install chromaprint

Other notes
+++++++++++

`Chromaprint <http://acoustid.org/chromaprint>`_ depends on FFmpeg, so if you have a custom FFmpeg install, you might also want to install that manually. ``./configure && make && sudo make install`` should work for FFmpeg and PortAudio. You might also want to use ``--enable-shared`` for FFmpeg. ``cmake . && sudo make install`` for Chromaprint.)

Building
++++++++

Then call ``python setup.py build`` or ``./compile.py`` to build the Python modules (it will build the Python module ``musicplayer.so``).

The module is also registered `on PyPI <https://pypi.python.org/pypi/musicplayer>`_, so you can also install via::

	easy_install musicplayer

.. image:: https://travis-ci.org/albertz/music-player-core.png
   :target: https://travis-ci.org/albertz/music-player-core


Similar projects
================

* *Overview* in Python Wiki: `Audio modules <https://wiki.python.org/moin/Audio>`_ and `Music software <https://wiki.python.org/moin/PythonInMusic>`_.

* `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/>`_. MIT License. PortAudio wrapper. Thus, pretty low-level and no decoding functionality. Last update from 2012.
* `PyFFmpeg <http://code.google.com/p/pyffmpeg/>`_. LGPL. FFmpeg wrapper. Thus, prettylow-level and no sound output. You could probably glue PyFFmpeg and PyAudio together for something useful but I expect it to be quite unstable and too slow. Basically, tis glue is done in C++ in this module.
* `GStreamer Python Bindings <http://gstreamer.freedesktop.org/modules/gst-python.html>`_. GStreamer is powerful but still too limited as a cross-platform music player backend solution. Quite heavy. That was my intuition. Maybe it's wrong and it would have been a perfect solution. But I think, in contrast, this module does a lot of things in a more compact and automatic/simpler way and at the same time provides more music player centric features.
* `Beets <http://beets.radbox.org/>`_. In its core, it is a music library manager and manages the metadata. It can calculate ReplayGain and AcoustID fingerprint. Via BPD plugin, it becomes a MPD compatible daemon player, based on GStreamer.

Probably dead projects:

* `PyMedia <http://pymedia.org/>`_. LGPL, GPL. FFmpeg-based encoding/decoding of audio+video, sound input/output via OSS/Waveout/Wavein. Unfornutaley not well tuned for usage in a high-quality music player. Last update from 2006.
* `Audiere <http://audiere.sourceforge.net/>`_. LGPL. High-level audio API, supports many sound formats and sound output on Windows/Linux. Last update from 2006.


