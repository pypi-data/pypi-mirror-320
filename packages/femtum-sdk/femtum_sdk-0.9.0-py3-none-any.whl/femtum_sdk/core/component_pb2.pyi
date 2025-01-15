from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tag(_message.Message):
    __slots__ = ("Key", "Value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    Key: str
    Value: str
    def __init__(self, Key: _Optional[str] = ..., Value: _Optional[str] = ...) -> None: ...

class Wafer(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[Tag]
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ...) -> None: ...

class Reticle(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[Tag]
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ...) -> None: ...

class Die(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[Tag]
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ...) -> None: ...

class Circuit(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[Tag]
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Type", "Tags", "Wafer", "Reticle", "Die", "Circuit", "DataJson")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    WAFER_FIELD_NUMBER: _ClassVar[int]
    RETICLE_FIELD_NUMBER: _ClassVar[int]
    DIE_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    DATAJSON_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Type: str
    Tags: _containers.RepeatedCompositeFieldContainer[Tag]
    Wafer: Wafer
    Reticle: Reticle
    Die: Die
    Circuit: Circuit
    DataJson: str
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Type: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ..., Wafer: _Optional[_Union[Wafer, _Mapping]] = ..., Reticle: _Optional[_Union[Reticle, _Mapping]] = ..., Die: _Optional[_Union[Die, _Mapping]] = ..., Circuit: _Optional[_Union[Circuit, _Mapping]] = ..., DataJson: _Optional[str] = ...) -> None: ...
