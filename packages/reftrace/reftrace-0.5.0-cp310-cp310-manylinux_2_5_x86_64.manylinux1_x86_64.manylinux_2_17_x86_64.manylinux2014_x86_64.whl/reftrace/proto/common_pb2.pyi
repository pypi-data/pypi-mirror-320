from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ParseError(_message.Message):
    __slots__ = ("error", "likely_rt_bug")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    LIKELY_RT_BUG_FIELD_NUMBER: _ClassVar[int]
    error: str
    likely_rt_bug: bool
    def __init__(self, error: _Optional[str] = ..., likely_rt_bug: bool = ...) -> None: ...
