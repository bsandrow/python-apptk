"""Utilities related to images."""

import imghdr

MIMETYPE_TO_EXTENSION_MAP = {
    "image/png": ".png",
    "image/jpg": ".jpg",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/vnd.djvu": ".djvu",
    "image/vnd.microsoft.icon": ".ico",
    "image/tiff": ".tiff",
    "image/jp2": ".jp2",
    "image/bmp": ".bmp",
    "image/mng": ".mng",
    "image/x-mng": ".mng",
}


def get_file_extension_for_mimetype(mimetype: str) -> str:
    """
    Return the file extension for a mimetype.

    :param mimetype: The mimetype to convert to a file extension.
    """
    return MIMETYPE_TO_EXTENSION_MAP.get(mimetype.lower().strip())


def check_if_mng(data: bytes) -> bool:
    """
    Check if the data belongs to a MNG file.

    source: https://en.wikipedia.org/wiki/Multiple-image_Network_Graphics

    :param data: The contents of the image file to check (or at least the header information).
    """
    MNG_HEADER = b"\x8A\x4D\x4E\x47\x0D\x0A\x1A\x0A"
    return data[: len(MNG_HEADER)] == MNG_HEADER


def check_if_jpeg(data: bytes) -> bool:
    """
    Check if data has a JPEG header.

    Source: https://stackoverflow.com/questions/36870661/imghdr-python-cant-detec-type-of-some-images-image-extension

    :param data: The contents of the image file (or at least just the header information)
    """
    JPEG_MARK = (
        b"\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07"
        b"\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f"
    )
    return (
        # JPEG data in JFIF format
        b"JFIF" in data[:23]
        # JPEG with small header
        or (len(data) >= 32 and 67 == data[5] and data[:32] == JPEG_MARK)
        # JPEG data in JFIF or Exif format
        or (data[6:10] in (b"JFIF", b"Exif") or data[:2] == b"\xff\xd8")
    )


def patch_imghdr():
    """
    Monkey patch in additional test for JPEG to imghdr to deal with buggy detection.

    Source: https://stackoverflow.com/questions/36870661/imghdr-python-cant-detec-type-of-some-images-image-extension
    """
    test_map = {
        "jpeg": check_if_jpeg,
        "mng": check_if_mng,
    }

    def check(h, f):
        for file_type, test in test_map.items():
            if test(h):
                return file_type

    imghdr.tests.append(check)
