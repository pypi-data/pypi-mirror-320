def __repr__(self, /) -> None:
    "This method implements repr(self)."
    cls = type(self)
    parts = list()
    for slot in cls.__slots__:
        value = getattr(self, slot)
        part = "%s=%r" % (slot, value)
        parts.append(part)
    body = ", ".join(parts)
    ans = "%s(%s)" % (cls.__name__, body)
    return ans


slotrepr = __repr__
