
import os
import time
import setuptools
import sys
from subprocess import check_output
from distutils.core import setup, Extension
from glob import glob
from pprint import pprint
from subprocess import Popen, check_output, PIPE


def debug_print_file(fn):
    print("%s:" % fn)
    if not os.path.exists(fn):
        print("<does not exist>")
        return
    if os.path.isdir(fn):
        print("<dir:>")
        pprint(os.listdir(fn))
        return
    print(open(fn).read())


def parse_pkg_info(fn):
    """
    :param str fn:
    :rtype: dict[str,str]
    """
    res = {}
    for ln in open(fn).read().splitlines():
        if not ln or not ln[:1].strip():
            continue
        key, value = ln.split(": ", 1)
        res[key] = value
    return res


def git_commit_date(commit="HEAD", git_dir="."):
    out = check_output(["git", "show", "-s", "--format=%ci", commit], cwd=git_dir).decode("utf8")
    out = out.strip()[:-6].replace(":", "").replace("-", "").replace(" ", ".")
    return out


def git_head_version(git_dir="."):
    commit_date = git_commit_date(git_dir=git_dir)  # like "20190202.154527"
    # Make this distutils.version.StrictVersion compatible.
    return "1.%s" % commit_date


if os.path.exists("PKG-INFO"):
    print("Found existing PKG-INFO.")
    info = parse_pkg_info("PKG-INFO")
    version = info["Version"]
    print("Version via PKG-INFO:", version)
else:
    try:
        version = git_head_version()
        print("Version via Git:", version)
    except Exception as exc:
        print("Exception while getting Git version:", exc)
        sys.excepthook(*sys.exc_info())
        version = time.strftime("1.%Y%m%d.%H%M%S", time.gmtime())
        print("Version via current time:", version)


if os.environ.get("DEBUG", "") == "1":
    debug_print_file(".")
    debug_print_file("PKG-INFO")


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
	version=version,
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
