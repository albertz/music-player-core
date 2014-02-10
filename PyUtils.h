#ifndef MP_PYUTILS_HPP
#define MP_PYUTILS_HPP

#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif

// this is mostly safe to call.
// returns a newly allocated c-string.
// doesn't need PyGIL
char* objStrDup(PyObject* obj);

// returns a newly allocated c-string.
// doesn't need PyGIL
char* objAttrStrDup(PyObject* obj, const char* attrStr);

#ifdef __cplusplus
}

#include <string>

// mostly safe, for debugging, dont need PyGIL
std::string objAttrStr(PyObject* obj, const std::string& attrStr);
std::string objStr(PyObject* obj);

// more correct. needs PyGIL
static inline
bool pyStr(PyObject* obj, std::string& str) {
	if(!obj) return false;
	if(PyString_Check(obj)) {
		str = std::string(PyString_AS_STRING(obj), PyString_GET_SIZE(obj));
		return true;
	}
	else if(PyUnicode_Check(obj)) {
		PyObject* strObj = PyUnicode_AsUTF8String(obj);
		if(!strObj) return false;
		bool res = false;
		if(PyString_Check(strObj))
			res = pyStr(strObj, str);
		Py_DECREF(strObj);
		return res;
	}
	else {
		PyObject* unicodeObj = PyObject_Unicode(obj);
		if(!unicodeObj) return false;
		bool res = false;
		if(PyString_Check(unicodeObj) || PyUnicode_Check(unicodeObj))
			res = pyStr(unicodeObj, str);
		Py_DECREF(unicodeObj);
		return res;
	}
	return false;	
}

#endif

#endif // PYUTILS_HPP
