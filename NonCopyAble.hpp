
#ifndef MP_NonCopyAble_hpp__
#define MP_NonCopyAble_hpp__

struct noncopyable {
	noncopyable() {}
	noncopyable(const noncopyable&) = delete;
	noncopyable& operator=(const noncopyable&) = delete;
};

#endif
