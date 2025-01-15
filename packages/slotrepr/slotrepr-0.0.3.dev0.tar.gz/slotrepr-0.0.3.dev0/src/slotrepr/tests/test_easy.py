import unittest

from slotrepr.core import slotrepr


class TestSlotRepr(unittest.TestCase):
    def test_slotrepr_basic(self):
        # Define a simple class with __slots__ and slotrepr
        class SimpleClass:
            __slots__ = ("a", "b")

            def __init__(self, a, b):
                self.a = a
                self.b = b

            __repr__ = slotrepr

        obj = SimpleClass(1, "test")
        self.assertEqual(repr(obj), "SimpleClass(a=1, b='test')")

    def test_slotrepr_empty_slots(self):
        # Define a class with no slots
        class NoSlotClass:
            __slots__ = ()

            __repr__ = slotrepr

        obj = NoSlotClass()
        self.assertEqual(repr(obj), "NoSlotClass()")

    def test_slotrepr_nested_objects(self):
        # Define a class that nests another class
        class NestedClass:
            __slots__ = ("value",)

            def __init__(self, value):
                self.value = value

            __repr__ = slotrepr

        class OuterClass:
            __slots__ = ("nested",)

            def __init__(self, nested):
                self.nested = nested

            __repr__ = slotrepr

        nested_obj = NestedClass(42)
        outer_obj = OuterClass(nested_obj)
        self.assertEqual(repr(outer_obj), "OuterClass(nested=NestedClass(value=42))")


if __name__ == "__main__":
    unittest.main()
