from com.terraquantum.credits.v1alpha1 import get_balance_pb2 as _get_balance_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CheckPermissionRequest(_message.Message):
    __slots__ = ("object_type", "relation", "user_id", "object_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    relation: str
    user_id: str
    object_id: str
    def __init__(self, object_type: _Optional[str] = ..., relation: _Optional[str] = ..., user_id: _Optional[str] = ..., object_id: _Optional[str] = ...) -> None: ...

class CheckPermissionResponse(_message.Message):
    __slots__ = ("has_permission",)
    HAS_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    has_permission: bool
    def __init__(self, has_permission: bool = ...) -> None: ...
