import base64
from unittest import TestCase

from apptk.protobuf import Data, ValueTypes, decode_buffer, decode_buffer_segment, decode_varint


class DecodeVarIntTestCase(TestCase):
    def test_decode_valid_varint(self):
        buffer = b"\xAC\x02"
        result = decode_varint(buffer, offset=0)
        expected = (300, 2)
        self.assertEqual(result, expected)

    def test_decode_valid_varint_with_offset(self):
        buffer = b"\xAC\x02"
        result = decode_varint(buffer, offset=1)
        expected = (2, 1)
        self.assertEqual(result, expected)

    def test_raises_error_on_invalid_varint(self):
        buffer = b"\xAC\xAC"
        with self.assertRaises(OverflowError):
            decode_varint(buffer, offset=1)


class DecodeBufferSegmentTestCase(TestCase):
    def test_empty_protobuf(self):
        result = decode_buffer_segment(b"")
        expected = ([], b"")
        self.assertEqual(result, expected)

    def test_empty_grpc(self):
        result = decode_buffer_segment(b"\x00\x00\x00\x00\x00")
        expected = ([], b"")
        self.assertEqual(result, expected)

    def test_decode_int(self):
        result = decode_buffer_segment(b"\x08\x96\x01")
        expected = ([{"index": 1, "type": ValueTypes.VARINT, "value": 150}], b"")
        self.assertEqual(result, expected)

    def test_decode_string(self):
        result = decode_buffer_segment(b"\x12\x07\x74\x65\x73\x74\x69\x6e\x67")
        expected = ([{"index": 2, "type": ValueTypes.STRING, "value": b"testing"}], b"")
        self.assertEqual(result, expected)

    def test_decode_int_and_string(self):
        result = decode_buffer_segment(b"\x08\x96\x01\x12\x07\x74\x65\x73\x74\x69\x6e\x67")
        expected = (
            [
                {"index": 1, "type": ValueTypes.VARINT, "value": 150},
                {"index": 2, "type": ValueTypes.STRING, "value": b"testing"},
            ],
            b"",
        )
        self.assertEqual(result, expected)

    def test_decode_fixed64_value(self):
        result = decode_buffer_segment(b"\x11\xAB\xAA\xAA\xAA\xAA\xAA\x20\x40")
        expected = ([{"index": 2, "type": ValueTypes.FIXED64, "value": b"\xAB\xAA\xAA\xAA\xAA\xAA\x20\x40"}], b"")
        self.assertEqual(result, expected)

    def test_decode_fixed32_value(self):
        result = decode_buffer_segment(b"\x15\xAB\xAA\x20\x40")
        expected = ([{"index": 2, "type": ValueTypes.FIXED32, "value": b"\xAB\xAA\x20\x40"}], b"")
        self.assertEqual(result, expected)

    def test_decode_int_in_grpc(self):
        result = decode_buffer_segment(b"\x00\x00\x00\x00\x03\x08\x96\x01")
        expected = ([{"index": 1, "type": ValueTypes.VARINT, "value": 150}], b"")
        self.assertEqual(result, expected)

    def test_undecodable_elements_in_leftover(self):
        result = decode_buffer_segment(b"\x12\x34\x56")
        expected = ([], b"\x12\x34\x56")
        self.assertEqual(result, expected)
