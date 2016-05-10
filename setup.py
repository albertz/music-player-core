

from distutils.core import setup, Extension
from glob import glob
import time, sys

# taken from http://code.activestate.com/recipes/502261-python-distutils-pkg-config/
import commands

# on fedora (23)
# dnf install ffmpeg-devel portaudio-devel libchromaprint-devel

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        if flag_map.has_key(token[:2]):
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else: # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)
    return kw

mod = Extension(
	'musicplayer',
	sources = glob("*.cpp"),
	depends = glob("*.h") + glob("*.hpp"),
	extra_compile_args = ["-std=c++11"],
	undef_macros = ['NDEBUG'],
        **pkgconfig('libavutil', 'libavformat', 'libavcodec', 'libswresample', 'portaudio-2.0', 'libchromaprint')
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
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Environment :: MacOS X',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: BSD License',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		'Operating System :: Unix',
		'Programming Language :: C++',
		'Programming Language :: Python',
		'Topic :: Multimedia :: Sound/Audio',
		'Topic :: Multimedia :: Sound/Audio :: Analysis',
		'Topic :: Multimedia :: Sound/Audio :: Players',
		'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
		'Topic :: Software Development :: Libraries :: Python Modules',
		],
	ext_modules = [mod]
)

