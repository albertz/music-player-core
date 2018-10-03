#!/usr/bin/env python
"""
MusicPlayer, https://github.com/albertz/music-player
Copyright (c) 2012, Albert Zeyer, www.az2000.de
All rights reserved.
This code is under the 2-clause BSD license, see License.txt in the root directory of this project.
"""

from glob import glob
from compile_utils import *
import compile_utils as c

os.chdir(os.path.dirname(__file__))
sys_exec(["mkdir", "-p", "build"])
os.chdir("build")

StaticChromaprint = False

print("* Building musicplayer.so")

ffmpeg_files = \
	sorted(glob("../*.cpp")) + \
	(sorted(glob("../chromaprint/*.cpp")) if StaticChromaprint else [])

cc(
	ffmpeg_files,
	[
		"-DHAVE_CONFIG_H",
		"-g",
	] +
	get_python_ccopts() +
	(["-I", "../chromaprint"] if StaticChromaprint else [])
)

link(
	"../musicplayer.so",
	[c.get_cc_outfilename(fn) for fn in ffmpeg_files],
	[
		"-lavutil",
		"-lavformat",
		"-lavcodec",
		"-lswresample",
		"-lportaudio",
	] +
	get_python_linkopts() +
	([] if StaticChromaprint else ["-lchromaprint"])
)

