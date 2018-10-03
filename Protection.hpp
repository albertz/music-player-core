#ifndef MP_PROTECTION_UNUSED_HPP
#define MP_PROTECTION_UNUSED_HPP

#include <memory>
#include "NonCopyAble.hpp"


struct ProtectionData : noncopyable {
	PyMutex mutex;
	uint16_t lockCounter;
	long lockThreadIdent;
	bool isValid;
	ProtectionData(); ~ProtectionData();
	void lock();
	void unlock();
};

typedef std::shared_ptr<ProtectionData> ProtectionPtr;
struct Protection : noncopyable {
	ProtectionPtr prot;
	Protection() : prot(new ProtectionData) {}
};

struct ProtectionScope : noncopyable {
	ProtectionPtr prot;
	ProtectionScope(const Protection& p);
	~ProtectionScope();
	void setInvalid();
	bool isValid();
};

#endif // PROTECTION_UNUSED_HPP
