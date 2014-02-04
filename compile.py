#!/usr/bin/env python
# MusicPlayer, https://github.com/albertz/music-player
# Copyright (c) 2012, Albert Zeyer, www.az2000.de
# All rights reserved.
# This code is under the 2-clause BSD license, see License.txt in the root directory of this project.

import os, sys
from glob import glob
os.chdir(os.path.dirname(__file__))

from compile_utils import *
import compile_utils as c

sysExec(["mkdir","-p","build"])
os.chdir("build")

staticChromaprint = False

print("* Building musicplayer.so")

ffmpegFiles = \
	glob("../*.cpp") + \
	(glob("../chromaprint/*.cpp") if staticChromaprint else [])

cc(
	ffmpegFiles,
	[
		"-DHAVE_CONFIG_H",
		"-g",
	] +
	get_python_ccopts() +
	(["-I", "../chromaprint"] if staticChromaprint else [])
)

link(
	"../musicplayer.so",
	[c.get_cc_outfilename(fn) for fn in ffmpegFiles],
	[
		"-lavutil",
		"-lavformat",
		"-lavcodec",
		"-lswresample",
		"-lportaudio",
	] +
	get_python_linkopts() +
	([] if staticChromaprint else ["-lchromaprint"])
)

