from unittest import TestCase

import apptk.func


class CachedPropertyTestCase(TestCase):
    def test_cached_property(self):
        class TestClass:
            call_count = 0

            @apptk.func.cached_property
            def test_property(self):
                self.call_count += 1
                return "abc"

        instance = TestClass()

        self.assertEqual(instance.call_count, 0)
        self.assertNotIn("test_property", instance.__dict__)
        self.assertEqual(instance.call_count, 0)

        self.assertEqual(instance.test_property, "abc")
        self.assertEqual(instance.call_count, 1, "Should be called for the first time since it was accessed.")
        self.assertIn("test_property", instance.__dict__, "Not cached in __dict__ for some reason")

        self.assertEqual(instance.test_property, "abc")
        self.assertEqual(instance.call_count, 1, "Called a second time when it should be cached")

        del instance.test_property
        self.assertNotIn("test_property", instance.__dict__, "Should be removed")
        self.assertEqual(instance.call_count, 1, "Call count shouldn't change yet.")

        self.assertEqual(instance.test_property, "abc")
        self.assertEqual(instance.call_count, 2, "Should have been called a second time to regen and cache the value.")
