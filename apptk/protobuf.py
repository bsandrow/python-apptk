from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ValueTypes(Enum):
    VARINT = 0
    FIXED64 = 1
    STRING = 2
    FIXED32 = 5

    @classmethod
    def from_int(cls, value: int) -> Optional["ValueTypes"]:
        for enum_value in cls:
            if enum_value.value == value:
                return enum_value
        return None


class ProtoBufFields(list):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert all(isinstance(item, Data) for item in self)

    def get_fields(self, field_no: int):
        return [item for item in self if item.field_no == field_no]

    def get_field(self, field_no: int):
        for item in self:
            if item.field_no == field_no:
                return item


@dataclass
class Data:
    field_no: int
    value: Any
    value_type: ValueTypes
    sub_fields: ProtoBufFields = field(default_factory=ProtoBufFields)


class BufferReader:
    checkpoint: int
    offset: int
    buffer: bytes

    def __init__(self, buffer: bytes) -> None:
        self.buffer = buffer
        self.offset = 0

    def read_varint(self):
        value, length = decode_varint(self.buffer, self.offset)
        self.offset += length
        return value

    @property
    def bytes_left(self):
        return len(self.buffer) - self.offset

    def set_checkpoint(self):
        self.checkpoint = self.offset

    def rollback_checkpoint(self):
        self.offset = self.checkpoint

    def read_buffer(self, length):
        if length > self.bytes_left:
            raise OverflowError(f"Not enough bytes left to honor request: length={length} bytes_left={self.bytes_left}")
        result = self.buffer[self.offset : self.offset + length]
        self.offset += length
        return result

    def skip_grc_header(self):
        _offset = self.offset
        if len(self.buffer) > 0 and self.buffer[self.offset] == 0 and self.bytes_left >= 5:
            self.offset += 1
            length = int.from_bytes(self.buffer[self.offset : self.offset + 4], byteorder="big")
            self.offset += 4
            if length > self.bytes_left:
                self.offset = _offset


def decode_varint(buffer: bytes, offset: int) -> tuple[int, int]:
    shift: int = 0
    result = 0
    byte = None

    while byte is None or byte >= 0x80:
        if offset >= len(buffer):
            raise OverflowError()
        byte = buffer[offset]
        offset += 1
        multiplier = 2**shift
        this_byte_value = (byte & 0x7F) * multiplier
        shift += 7
        result = result + this_byte_value

    return result, int(shift / 7)  # note: shift will always be a multiple of 7


def decode_buffer_segment(buffer: bytes) -> tuple[list, bytes]:
    reader = BufferReader(buffer)
    parts = []

    reader.skip_grc_header()

    try:
        while reader.bytes_left > 0:
            # print(f"BytesLeft: {reader.bytes_left}")
            reader.set_checkpoint()
            index_type = reader.read_varint()
            value_type_int = index_type & 0b111
            value_type = ValueTypes.from_int(value_type_int)
            value_index = index_type >> 3

            # print(f"index_type = {index_type}")
            # print(f"value_type_int = {value_type_int}")
            # print(f"value_type = {value_type}")
            # print(f"value_index = {value_index}")

            if value_type == ValueTypes.VARINT:
                value = reader.read_varint()

            elif value_type == ValueTypes.STRING:
                length = reader.read_varint()
                value = reader.read_buffer(length)

            elif value_type == ValueTypes.FIXED32:
                value = reader.read_buffer(4)

            elif value_type == ValueTypes.FIXED64:
                value = reader.read_buffer(8)

            else:
                raise ValueError(f"Unknown Type: {value_type_int}")

            parts.append({"index": value_index, "type": value_type, "value": value})

    except (ValueError, OverflowError):
        reader.rollback_checkpoint()

    return parts, reader.read_buffer(reader.bytes_left)


def decode_buffer(buffer):
    parts, leftovers = decode_buffer_segment(buffer)
    result = ProtoBufFields()

    for part in parts:
        if part["type"] == ValueTypes.STRING:
            sub_parts, _leftovers = decode_buffer_segment(part["value"])
            if len(part["value"]) > 0 and len(_leftovers) == 0:
                part["sub_fields"] = decode_buffer(part["value"])

        result.append(Data(field_no=part["index"], value=part["value"], value_type=part["type"]))

    return result
