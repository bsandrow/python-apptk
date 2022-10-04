import os
import tempfile
from unittest import TestCase

import apptk.files


class TestWorkingDirectoryContextManager(TestCase):
    def test_cwd_ctx_manager(self):
        dir_path = tempfile.mkdtemp()
        current_wd = os.getcwd()

        actual = os.path.realpath(os.getcwd())
        expected = os.path.realpath(current_wd)
        self.assertEqual(actual, expected)

        with apptk.files.cwd(dir_path):
            actual = os.path.realpath(os.getcwd())
            expected = os.path.realpath(dir_path)
            self.assertEqual(actual, expected)

        actual = os.path.realpath(os.getcwd())
        expected = os.path.realpath(current_wd)
        self.assertEqual(actual, expected)
