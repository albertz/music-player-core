# QMake subdirs are a bit weird.
# http://qt-project.org/wiki/QMake-top-level-srcdir-and-builddir
# It seems as if we need a seperate pro-file to specify the dependencies
# and the subdirs.

TEMPLATE = subdirs

SUBDIRS = qmake_lib
