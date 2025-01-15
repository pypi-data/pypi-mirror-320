from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BotRegion(_message.Message):
    __slots__ = ["id", "name", "languages"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    languages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., languages: _Optional[_Iterable[str]] = ...) -> None: ...

class Bot(_message.Message):
    __slots__ = ["id", "name", "secret_token", "regions"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SECRET_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    secret_token: str
    regions: _containers.RepeatedCompositeFieldContainer[BotRegion]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., secret_token: _Optional[str] = ..., regions: _Optional[_Iterable[_Union[BotRegion, _Mapping]]] = ...) -> None: ...

class RetrieveBotsResponse(_message.Message):
    __slots__ = ["bots"]
    BOTS_FIELD_NUMBER: _ClassVar[int]
    bots: _containers.RepeatedCompositeFieldContainer[Bot]
    def __init__(self, bots: _Optional[_Iterable[_Union[Bot, _Mapping]]] = ...) -> None: ...

class BotRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
