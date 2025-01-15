import femtum_sdk.core.component_pb2 as _component_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpticalSpectralAnalyserSweepResultArray(_message.Message):
    __slots__ = ("Items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[OpticalSpectralAnalyserSweepResult]
    def __init__(self, Items: _Optional[_Iterable[_Union[OpticalSpectralAnalyserSweepResult, _Mapping]]] = ...) -> None: ...

class NewOpticalSpectralAnalyserSweepResult(_message.Message):
    __slots__ = ("WavelengthsArray", "PowersArray", "Name", "Tags", "WaferName", "ReticleName", "DieName", "CircuitName")
    WAVELENGTHSARRAY_FIELD_NUMBER: _ClassVar[int]
    POWERSARRAY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    WAFERNAME_FIELD_NUMBER: _ClassVar[int]
    RETICLENAME_FIELD_NUMBER: _ClassVar[int]
    DIENAME_FIELD_NUMBER: _ClassVar[int]
    CIRCUITNAME_FIELD_NUMBER: _ClassVar[int]
    WavelengthsArray: _containers.RepeatedScalarFieldContainer[float]
    PowersArray: _containers.RepeatedScalarFieldContainer[float]
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    WaferName: str
    ReticleName: str
    DieName: str
    CircuitName: str
    def __init__(self, WavelengthsArray: _Optional[_Iterable[float]] = ..., PowersArray: _Optional[_Iterable[float]] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ..., WaferName: _Optional[str] = ..., ReticleName: _Optional[str] = ..., DieName: _Optional[str] = ..., CircuitName: _Optional[str] = ...) -> None: ...

class OpticalSpectralAnalyserSweepResult(_message.Message):
    __slots__ = ("WavelengthsArray", "PowersArray", "Name", "Tags", "WaferName", "ReticleName", "DieName", "CircuitName", "Id")
    WAVELENGTHSARRAY_FIELD_NUMBER: _ClassVar[int]
    POWERSARRAY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    WAFERNAME_FIELD_NUMBER: _ClassVar[int]
    RETICLENAME_FIELD_NUMBER: _ClassVar[int]
    DIENAME_FIELD_NUMBER: _ClassVar[int]
    CIRCUITNAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    WavelengthsArray: _containers.RepeatedScalarFieldContainer[float]
    PowersArray: _containers.RepeatedScalarFieldContainer[float]
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    WaferName: str
    ReticleName: str
    DieName: str
    CircuitName: str
    Id: str
    def __init__(self, WavelengthsArray: _Optional[_Iterable[float]] = ..., PowersArray: _Optional[_Iterable[float]] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ..., WaferName: _Optional[str] = ..., ReticleName: _Optional[str] = ..., DieName: _Optional[str] = ..., CircuitName: _Optional[str] = ..., Id: _Optional[str] = ...) -> None: ...

class ResultsFilterRequest(_message.Message):
    __slots__ = ("ResultName", "WaferName", "ReticleName", "DieName", "CircuitName", "Tags")
    RESULTNAME_FIELD_NUMBER: _ClassVar[int]
    WAFERNAME_FIELD_NUMBER: _ClassVar[int]
    RETICLENAME_FIELD_NUMBER: _ClassVar[int]
    DIENAME_FIELD_NUMBER: _ClassVar[int]
    CIRCUITNAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    ResultName: str
    WaferName: str
    ReticleName: str
    DieName: str
    CircuitName: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    def __init__(self, ResultName: _Optional[str] = ..., WaferName: _Optional[str] = ..., ReticleName: _Optional[str] = ..., DieName: _Optional[str] = ..., CircuitName: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ListByPageResultsRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: ResultsFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[ResultsFilterRequest, _Mapping]] = ...) -> None: ...

class ResultsPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[_component_pb2.Result]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[_component_pb2.Result, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class FindResultByIdRequest(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...

class OptionalSingleResults(_message.Message):
    __slots__ = ("Result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    Result: _component_pb2.Result
    def __init__(self, Result: _Optional[_Union[_component_pb2.Result, _Mapping]] = ...) -> None: ...

class WafersFilterRequest(_message.Message):
    __slots__ = ("Name", "Tags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    def __init__(self, Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ListByPageWafersRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: WafersFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[WafersFilterRequest, _Mapping]] = ...) -> None: ...

class WafersPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[_component_pb2.Wafer]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[_component_pb2.Wafer, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class DiesFilterRequest(_message.Message):
    __slots__ = ("Name", "Tags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    def __init__(self, Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ListByPageDiesRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: DiesFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[DiesFilterRequest, _Mapping]] = ...) -> None: ...

class DiesPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[_component_pb2.Die]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[_component_pb2.Die, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class ReticlesFilterRequest(_message.Message):
    __slots__ = ("Name", "Tags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    def __init__(self, Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ListByPageReticlesRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: ReticlesFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[ReticlesFilterRequest, _Mapping]] = ...) -> None: ...

class ReticlesPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[_component_pb2.Reticle]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[_component_pb2.Reticle, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class CircuitsFilterRequest(_message.Message):
    __slots__ = ("Name", "Tags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_component_pb2.Tag]
    def __init__(self, Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_component_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ListByPageCircuitsRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: CircuitsFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[CircuitsFilterRequest, _Mapping]] = ...) -> None: ...

class CircuitsPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[_component_pb2.Circuit]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[_component_pb2.Circuit, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...
