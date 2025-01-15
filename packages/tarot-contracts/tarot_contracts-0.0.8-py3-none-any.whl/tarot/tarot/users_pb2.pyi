from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TelegramUser(_message.Message):
    __slots__ = ["id", "username", "first_name", "last_name", "language_code", "is_bot", "is_premium", "profile_photos"]
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_CODE_FIELD_NUMBER: _ClassVar[int]
    IS_BOT_FIELD_NUMBER: _ClassVar[int]
    IS_PREMIUM_FIELD_NUMBER: _ClassVar[int]
    PROFILE_PHOTOS_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    first_name: str
    last_name: str
    language_code: str
    is_bot: bool
    is_premium: bool
    profile_photos: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., language_code: _Optional[str] = ..., is_bot: bool = ..., is_premium: bool = ..., profile_photos: _Optional[_Iterable[str]] = ...) -> None: ...

class SpreadProfile(_message.Message):
    __slots__ = ["tg_id", "full_name", "birth_date", "birth_time", "birth_place", "zodiac_sign", "chinese_zodiac_sign", "gender"]
    TG_ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    BIRTH_TIME_FIELD_NUMBER: _ClassVar[int]
    BIRTH_PLACE_FIELD_NUMBER: _ClassVar[int]
    ZODIAC_SIGN_FIELD_NUMBER: _ClassVar[int]
    CHINESE_ZODIAC_SIGN_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    tg_id: int
    full_name: str
    birth_date: str
    birth_time: str
    birth_place: str
    zodiac_sign: str
    chinese_zodiac_sign: str
    gender: str
    def __init__(self, tg_id: _Optional[int] = ..., full_name: _Optional[str] = ..., birth_date: _Optional[str] = ..., birth_time: _Optional[str] = ..., birth_place: _Optional[str] = ..., zodiac_sign: _Optional[str] = ..., chinese_zodiac_sign: _Optional[str] = ..., gender: _Optional[str] = ...) -> None: ...

class TelegramUserRequest(_message.Message):
    __slots__ = ["tg_id"]
    TG_ID_FIELD_NUMBER: _ClassVar[int]
    tg_id: int
    def __init__(self, tg_id: _Optional[int] = ...) -> None: ...
