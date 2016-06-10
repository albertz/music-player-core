#ifndef MP_PYTHREAD_HPP
#define MP_PYTHREAD_HPP

#include <Python.h>
#include <pythread.h>
#include <atomic>
#include <functional>
#include "NonCopyAble.hpp"


struct PyMutex {
	PyThread_type_lock l;
	bool enabled;
	PyMutex(); ~PyMutex();
	PyMutex(const PyMutex&) : PyMutex() {} // ignore
	PyMutex& operator=(const PyMutex&) { return *this; } // ignore
	void lock();
	bool lock_nowait();
	void unlock();
};

struct PyScopedLock : noncopyable {
	PyMutex& mutex;
	PyScopedLock(PyMutex& m);
	~PyScopedLock();
};

struct PyScopedUnlock : noncopyable {
	PyMutex& mutex;
	PyScopedUnlock(PyMutex& m);
	~PyScopedUnlock();
};

struct PyScopedGIL : noncopyable {
	PyGILState_STATE gstate;
	PyScopedGIL() { gstate = PyGILState_Ensure(); }
	~PyScopedGIL() {
		if(PyThreadState_Get()->gilstate_counter == 1) {
			// This means that the thread-state is going to be deleted.
			// This can happen when you created this thread state on a new
			// thread which was not registered in Python before.
			if(PyErr_Occurred())
				// Print exception. It would get lost otherwise.
				PyErr_Print();
		}
		PyGILState_Release(gstate);
	}
};

struct PyScopedGIUnlock : noncopyable {
	PyScopedGIL gstate; // in case we didn't had the GIL
	PyThreadState* _save;
	PyScopedGIUnlock() : _save(NULL) { Py_UNBLOCK_THREADS }
	~PyScopedGIUnlock() { Py_BLOCK_THREADS }
};


struct PyThread : noncopyable {
	PyMutex lock;
	std::atomic<bool> running;
	std::atomic<bool> stopSignal;
	std::function<void(std::atomic<bool>& stopSignal)> func;
	long ident;
	PyThread(); ~PyThread();
	bool start();
	void wait();
	void stop();
};

extern "C" {
// this is defined in <sys/mman.h>. systems which don't have that should provide a dummy/wrapper
int mlock(const void *addr, size_t len);
}


void setCurThreadName(const std::string& name);


#endif // PYTHREAD_HPP
