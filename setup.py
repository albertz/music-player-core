

from distutils.core import setup, Extension
from glob import glob
import time

mod = Extension(
	'musicplayer',
	sources = glob("*.cpp"),
	extra_compile_args = ["--std=c++11"],
	libraries = [
		'avutil',
		'avformat',
		'avcodec',
		'swresample',
		'portaudio',
		'chromaprint'
		]
	)

setup(
	name = 'musicplayer',
	version = time.strftime("1.%Y%m%d.%H%M%S", time.gmtime()),
	description = 'Music player core Python module',
	author = 'Albert Zeyer',
	author_email = 'albzey@gmail.com',
	url = 'https://github.com/albertz/music-player-core',
	license = '2-clause BSD license',
	long_description = open('README.rst').read(),
	ext_modules = [mod]
)

