# This builds the Python module musicplayer.so.
# It is mainly used by the MusicPlayer app (https://github.com/albertz/music-player).
# On MacOSX, to build a proper app bundle:
#   It links statically to portaudio and chromaprint.
#   It links dynamically to the custom build FFmpeg.
#   It expects Python in ../python-embedded/CPython.
#   It also searches in /usr/local/include (e.g. for Boost).
# Otherwise, it uses the system libs.

# A Python module is named xyz.so, not libxyz.dylib or sth else.
# The following config/template does that.
# From here: http://lists.qt-project.org/pipermail/interest/2012-June/002798.html
CONFIG += plugin no_plugin_name_prefix
TEMPLATE = lib
QMAKE_EXTENSION_SHLIB = so
TARGET = musicplayer

SOURCES = $$files(../*.cpp)
HEADERS = $$files(../*.h)
HEADERS += $$files(../*.hpp)

CONFIG += thread
CONFIG -= qt
QMAKE_CXXFLAGS += -std=c++11

mac {
	INCLUDEPATH += ../external/ffmpeg/target/include
	INCLUDEPATH += ../external/portaudio/include
	INCLUDEPATH += ../chromaprint
	INCLUDEPATH += ../../python-embedded/CPython/Include
	INCLUDEPATH += ../../python-embedded/pylib
	INCLUDEPATH += /usr/local/include

	# Link against the dylibs.
	QMAKE_LFLAGS += -L../external/ffmpeg/target/lib
	QMAKE_LFLAGS += -lavformat -lavutil -lavcodec -lswresample

	# Link against the static libs.
	QMAKE_LFLAGS += -L $$DESTDIR -lchromaprint -lportaudio

	# We don't link against Python.
	QMAKE_LFLAGS += -undefined dynamic_lookup
}

!mac {
	CONFIG += link_pkgconfig
	PKGCONFIG += chromaprint portaudio
	PKGCONFIG += avformat avutil avcodec swresample
}
