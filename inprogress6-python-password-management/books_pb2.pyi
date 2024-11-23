from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBooksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetBooksResponse(_message.Message):
    __slots__ = ("books",)
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[Book]
    def __init__(self, books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ...) -> None: ...

class Book(_message.Message):
    __slots__ = ("id", "title", "author", "price")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    author: str
    price: float
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., price: _Optional[float] = ...) -> None: ...

class GetBookByIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetBookByIdResponse(_message.Message):
    __slots__ = ("book",)
    BOOK_FIELD_NUMBER: _ClassVar[int]
    book: Book
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ...) -> None: ...

class AddBookRequest(_message.Message):
    __slots__ = ("title", "author", "price")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    title: str
    author: str
    price: int
    def __init__(self, title: _Optional[str] = ..., author: _Optional[str] = ..., price: _Optional[int] = ...) -> None: ...

class AddBookResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: GeneralResponse
    def __init__(self, response: _Optional[_Union[GeneralResponse, _Mapping]] = ...) -> None: ...

class GeneralResponse(_message.Message):
    __slots__ = ("message", "code")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    message: str
    code: int
    def __init__(self, message: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...

class DeleteBookRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteBookResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: GeneralResponse
    def __init__(self, response: _Optional[_Union[GeneralResponse, _Mapping]] = ...) -> None: ...

class EditBookRequest(_message.Message):
    __slots__ = ("id", "title", "author", "price")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    author: str
    price: int
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., price: _Optional[int] = ...) -> None: ...

class EditBookResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: GeneralResponse
    def __init__(self, response: _Optional[_Union[GeneralResponse, _Mapping]] = ...) -> None: ...
