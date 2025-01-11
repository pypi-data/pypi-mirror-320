from proto import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigFileResult(_message.Message):
    __slots__ = ("config_file", "error")
    CONFIG_FILE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    config_file: ConfigFile
    error: _common_pb2.ParseError
    def __init__(self, config_file: _Optional[_Union[ConfigFile, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.ParseError, _Mapping]] = ...) -> None: ...

class ConfigFile(_message.Message):
    __slots__ = ("path", "process_scopes")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PROCESS_SCOPES_FIELD_NUMBER: _ClassVar[int]
    path: str
    process_scopes: _containers.RepeatedCompositeFieldContainer[ProcessScope]
    def __init__(self, path: _Optional[str] = ..., process_scopes: _Optional[_Iterable[_Union[ProcessScope, _Mapping]]] = ...) -> None: ...

class ProcessScope(_message.Message):
    __slots__ = ("line_number", "directives", "named_scopes")
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DIRECTIVES_FIELD_NUMBER: _ClassVar[int]
    NAMED_SCOPES_FIELD_NUMBER: _ClassVar[int]
    line_number: int
    directives: _containers.RepeatedCompositeFieldContainer[DirectiveConfig]
    named_scopes: _containers.RepeatedCompositeFieldContainer[NamedScope]
    def __init__(self, line_number: _Optional[int] = ..., directives: _Optional[_Iterable[_Union[DirectiveConfig, _Mapping]]] = ..., named_scopes: _Optional[_Iterable[_Union[NamedScope, _Mapping]]] = ...) -> None: ...

class NamedScope(_message.Message):
    __slots__ = ("line_number", "name", "directives")
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DIRECTIVES_FIELD_NUMBER: _ClassVar[int]
    line_number: int
    name: str
    directives: _containers.RepeatedCompositeFieldContainer[DirectiveConfig]
    def __init__(self, line_number: _Optional[int] = ..., name: _Optional[str] = ..., directives: _Optional[_Iterable[_Union[DirectiveConfig, _Mapping]]] = ...) -> None: ...

class DirectiveConfig(_message.Message):
    __slots__ = ("line_number", "name", "options", "value")
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    line_number: int
    name: str
    options: _containers.RepeatedCompositeFieldContainer[NamedOption]
    value: DirectiveValue
    def __init__(self, line_number: _Optional[int] = ..., name: _Optional[str] = ..., options: _Optional[_Iterable[_Union[NamedOption, _Mapping]]] = ..., value: _Optional[_Union[DirectiveValue, _Mapping]] = ...) -> None: ...

class NamedOption(_message.Message):
    __slots__ = ("line_number", "name", "value")
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    line_number: int
    name: str
    value: DirectiveValue
    def __init__(self, line_number: _Optional[int] = ..., name: _Optional[str] = ..., value: _Optional[_Union[DirectiveValue, _Mapping]] = ...) -> None: ...

class DirectiveValue(_message.Message):
    __slots__ = ("params", "in_closure")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    IN_CLOSURE_FIELD_NUMBER: _ClassVar[int]
    params: _containers.RepeatedScalarFieldContainer[str]
    in_closure: bool
    def __init__(self, params: _Optional[_Iterable[str]] = ..., in_closure: bool = ...) -> None: ...
