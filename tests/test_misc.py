from unittest import TestCase

import apptk.misc


class SlugifyTestCase(TestCase):
    def test_handles_slug(self):
        self.assertEqual(apptk.misc.slugify("a-b-c"), "a-b-c")

    def test_handles_replacement_chars(self):
        self.assertEqual(apptk.misc.slugify("a.b.c.3.Ag."), "a-b-c-3-ag")

    def test_handles_replacement_chars_in_series(self):
        self.assertEqual(apptk.misc.slugify("a.b.c._.Ag"), "a-b-c-ag")
