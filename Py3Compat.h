
#ifndef MusicPlayer_Py3Compat_h
#define MusicPlayer_Py3Compat_h

#include <Python.h>

// functions for some bytes type (in Python 3: bytes; in Python 2: str)
#if PY_MAJOR_VERSION == 2
#define PyBytes_AS_STRING PyString_AS_STRING
#define PyBytes_FromStringAndSize PyString_FromStringAndSize
#define _PyBytes_Resize _PyString_Resize
#define PyBytes_Check PyString_Check
#define PyBytes_Size PyString_Size
#endif

// functions for some string type (in Python 3: str; in Python 2: str)
#if PY_MAJOR_VERSION >= 3
#define PyString_FromString PyUnicode_FromString
#endif

// functions for some int type (in Python 3: long; in Python 2: int)
#if PY_MAJOR_VERSION >= 3
#define PyInt_FromLong PyLong_FromLong
// Also, just treat non-existing int-type as long-type.
#define PyInt_Check PyLong_Check
#define PyInt_AsLong PyLong_AsLong
#endif

// some flags, non-existing in Python 3
// see https://github.com/encukou/py3c/blob/master/include/py3c/tpflags.h
#if PY_MAJOR_VERSION >= 3
#define Py_TPFLAGS_HAVE_CLASS 0
#endif


#endif
