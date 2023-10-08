from unittest import TestCase

from apptk import images

from .helpers import get_test_data


class FileExtensionFromMimetypeTestCase(TestCase):
    def test_png(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/png"), ".png")

    def test_jpeg(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/jpg"), ".jpg")
        self.assertEqual(images.get_file_extension_for_mimetype("image/jpeg"), ".jpg")
        self.assertEqual(images.get_file_extension_for_mimetype("image/jp2"), ".jp2")

    def test_webp(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/webp"), ".webp")

    def test_gif(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/gif"), ".gif")

    def test_microsoft(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/vnd.microsoft.icon"), ".ico")
        self.assertEqual(images.get_file_extension_for_mimetype("image/bmp"), ".bmp")

    def test_svg(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/svg+xml"), ".svg")

    def test_tiff(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/tiff"), ".tiff")

    def test_djvu(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/vnd.djvu"), ".djvu")

    def test_mng(self):
        self.assertEqual(images.get_file_extension_for_mimetype("image/mng"), ".mng")
        self.assertEqual(images.get_file_extension_for_mimetype("image/x-mng"), ".mng")


class CheckIfMngTestCase(TestCase):
    def test_sample_mng_file(self):
        mng_file = get_test_data("sample.mng", use_bytes=True)
        self.assertTrue(images.check_if_mng(mng_file))

    def test_rejects_png_file(self):
        png_file = get_test_data("sample.png", use_bytes=True)
        self.assertFalse(images.check_if_mng(png_file))


class CheckIfJpegTestCase(TestCase):
    def test_sample_jpeg(self):
        jpg_file = get_test_data("sample.jpg", use_bytes=True)
        self.assertTrue(images.check_if_jpeg(jpg_file))

    def test_rejects_png(self):
        png_file = get_test_data("sample.png", use_bytes=True)
        self.assertFalse(images.check_if_jpeg(png_file))

    def test_rejects_mng(self):
        mng_file = get_test_data("sample.mng", use_bytes=True)
        self.assertFalse(images.check_if_jpeg(mng_file))
