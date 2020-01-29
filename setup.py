
import time
import setuptools
from subprocess import check_output
from distutils.core import setup, Extension
from glob import glob


# on fedora (23)
# dnf install ffmpeg-devel portaudio-devel libchromaprint-devel

def pkgconfig(*packages, **kw):
	"""
	:param str packages: list like 'libavutil', 'libavformat', ...
	:rtype: dict[str]
	"""
	kw = kw.copy()
	flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}  # kwargs of :class:`Extension`
	for token in check_output(["pkg-config", "--libs", "--cflags"] + list(packages)).split():
		if token[:2] in flag_map:
			kw.setdefault(flag_map[token[:2]], []).append(token[2:])
		else:  # throw others to extra_link_args
			kw.setdefault('extra_link_args', []).append(token.decode("utf-8")) # decode() is needed because tokens are bytes

	return kw


mod = Extension(
	'musicplayer',
	sources=glob("*.cpp"),
	depends=glob("*.h") + glob("*.hpp"),
	extra_compile_args=["-std=c++11"],
	undef_macros=['NDEBUG'],
	**pkgconfig('libavutil', 'libavformat', 'libavcodec', 'libswresample', 'portaudio-2.0', 'libchromaprint'))

setup(
	name='musicplayer',
	version=time.strftime("1.%Y%m%d.%H%M%S", time.gmtime()),
	description='Music player core Python module',
	author='Albert Zeyer',
	author_email='albzey@gmail.com',
	url='https://github.com/albertz/music-player-core',
	license='2-clause BSD license',
	long_description=open('README.rst').read(),
	classifiers=[
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
	ext_modules=[mod])
