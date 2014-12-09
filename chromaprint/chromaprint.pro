# This is mostly used by the musicplayer module atm.
# This is mostly for MacOSX now because it is the only OS
# where we link against this Chromaprint.

!mac {
	error( "Only tested for MacOSX yet." )
}

TEMPLATE = lib
CONFIG += staticlib

QMAKE_CXXFLAGS += -DHAVE_CONFIG_H
SOURCES += $$files(*.cpp)
HEADERS += $$files(*.h)

mac {
	INCLUDEPATH += ../external/ffmpeg/target/include
}
