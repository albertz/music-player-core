# QMake subdirs are a bit weird.
# http://qt-project.org/wiki/QMake-top-level-srcdir-and-builddir
# It seems as if we need a seperate pro-file to specify the dependencies
# and the subdirs.

TEMPLATE = subdirs

mac {
	# We build against our own FFmpeg.
	# FFmpeg is not build via qmake; it comes with its own build script.
	# Just check its existence.
	!exists( external/ffmpeg/target/lib/libavcodec.dylib ) {
		error( "FFmpeg libs not found" )
	}
}

SUBDIRS = lib
lib.subdir = qmake_lib

mac {
	# We link against our own portaudio and chromaprint.
	SUBDIRS += portaudio chromaprint
	portaudio.subdir = external/portaudio
	qmake_lib.depends = portaudio chromaprint
}
