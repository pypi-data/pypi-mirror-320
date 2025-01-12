"""
Specially annotated types used in cdataobject (Structure/Union) field annotations.
"""

import contextlib
import ctypes
import sys
import typing

from exactypes.array import offset_of

from ..types import PT as _PT
from ..types import XCT as _XCT
from ..types import CTypes, PyCPointerType


class CDataField(typing.Generic[_PT, _XCT]):
    """
    A symbol to store typed generic data with auto-conversion.
    Only benefits static type checkers by using descriptor methods.

    >>> CDataField[AutoConvertedPythonType, CType]
    """
    def __init__(self, ptype: type[_PT], ctype: type[_XCT]) -> None:
        self.ptype = ptype
        self.ctype = ctype

    def __get__(self, obj, type_=None) -> _PT:  # type: ignore[empty-body]
        ...

    def __set__(self, obj, value: typing.Union[_PT, _XCT]) -> None: ...


class CArrayField(CDataField[_PT, ctypes.Array[_XCT]], typing.Generic[_PT, _XCT]):
    """Similar to `CDataField`, but for C array types."""
    def __get__(self, obj, type_=None) -> _PT:  # type: ignore[empty-body]
        ...

    def __set__(self, obj, value: typing.Union[_PT, ctypes.Array[_XCT]]) -> None: ...


class CFlexibleArray(typing.Generic[_XCT]):
    """
    A real descriptor to help access C flexible array member.
    """
    def __init__(self, typ: type[_XCT]) -> None:
        self.type_ = typ

    def __get__(
        self, obj: typing.Union[ctypes.Structure, ctypes.Union], type_=None
    ) -> "PyCPointerType[_XCT]":
        return offset_of(ctypes.pointer(obj), 1, self.type_)


def value(default: typing.Any = None) -> typing.Any:
    """
    Stub value, used when you do not use .pyi stub (in which you can simply write `...` instead of
    this).
    """
    return default


py_object = CDataField[_PT, ctypes.py_object]
c_short = CDataField[int, ctypes.c_short]
c_ushort = CDataField[int, ctypes.c_ushort]
c_long = CDataField[int, ctypes.c_long]
c_ulong = CDataField[int, ctypes.c_ulong]
c_int = CDataField[int, ctypes.c_int]
c_uint = CDataField[int, ctypes.c_uint]
c_float = CDataField[float, ctypes.c_float]
c_double = CDataField[float, ctypes.c_double]
c_longdouble = CDataField[float, ctypes.c_longdouble]
c_longlong = CDataField[int, ctypes.c_longlong]
c_ulonglong = CDataField[int, ctypes.c_ulonglong]
c_ubyte = CDataField[int, ctypes.c_ubyte]
c_byte = CDataField[int, ctypes.c_byte]
c_char = CDataField[bytes, ctypes.c_char]
c_char_p = CDataField[typing.Optional[bytes], ctypes.c_char_p]
c_void_p = CDataField[int, ctypes.c_void_p]
c_bool = CDataField[bool, ctypes.c_bool]
c_wchar_p = CDataField[typing.Optional[str], ctypes.c_wchar_p]
c_wchar = CDataField[str, ctypes.c_wchar]
c_size_t = CDataField[int, ctypes.c_size_t]
c_ssize_t = CDataField[int, ctypes.c_ssize_t]
c_int8 = CDataField[int, ctypes.c_int8]
c_uint8 = CDataField[int, ctypes.c_uint8]

c_char_array = CArrayField[bytes, ctypes.c_char]
c_wchar_array = CArrayField[str, ctypes.c_wchar]


if sys.version_info >= (3, 12):
    c_time_t = CDataField[int, ctypes.c_time_t]

    HAS_TIME_T = True
else:
    HAS_TIME_T = False

if sys.version_info >= (3, 14):
    c_float_complex = CDataField[complex, ctypes.c_float_complex]
    c_double_complex = CDataField[complex, ctypes.c_double_complex]
    c_longdouble_complex = CDataField[complex, ctypes.c_longdouble_complex]

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_float_complex"], type[ctypes.c_float_complex]],
    ) -> type[ctypes.Array[ctypes.c_float_complex]]: ...

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_double_complex"], type[ctypes.c_double_complex]],
    ) -> type[ctypes.Array[ctypes.c_double_complex]]: ...

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_longdouble_complex"], type[ctypes.c_longdouble_complex]],
    ) -> type[ctypes.Array[ctypes.c_longdouble_complex]]: ...


HAS_INT16 = HAS_INT32 = HAS_INT64 = False
with contextlib.suppress(AttributeError):
    c_int16 = CDataField[int, ctypes.c_int16]
    c_uint16 = CDataField[int, ctypes.c_uint16]

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_int16"], type[ctypes.c_int16]],
    ) -> type[ctypes.Array[ctypes.c_int16]]: ...

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_uint16"], type[ctypes.c_uint16]],
    ) -> type[ctypes.Array[ctypes.c_uint16]]: ...

    HAS_INT16 = True
with contextlib.suppress(AttributeError):
    c_int32 = CDataField[int, ctypes.c_int32]
    c_uint32 = CDataField[int, ctypes.c_uint32]

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_int32"], type[ctypes.c_int32]],
    ) -> type[ctypes.Array[ctypes.c_int32]]: ...

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_uint32"], type[ctypes.c_uint32]],
    ) -> type[ctypes.Array[ctypes.c_uint32]]: ...

    HAS_INT32 = True
with contextlib.suppress(AttributeError):
    c_int64 = CDataField[int, ctypes.c_int64]
    c_uint64 = CDataField[int, ctypes.c_uint64]

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_int64"], type[ctypes.c_int64]],
    ) -> type[ctypes.Array[ctypes.c_int64]]: ...

    @typing.overload
    def array_of(
        tp: typing.Union[typing.Literal["c_uint64"], type[ctypes.c_uint64]],
    ) -> type[ctypes.Array[ctypes.c_uint64]]: ...

    HAS_INT64 = True


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["py_object"], type["ctypes.py_object[typing.Any]"]],
) -> type[ctypes.Array[ctypes.py_object]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_short"], type[ctypes.c_short]],
) -> type[ctypes.Array[ctypes.c_short]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_ushort"], type[ctypes.c_ushort]],
) -> type[ctypes.Array[ctypes.c_ushort]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_long"], type[ctypes.c_long]],
) -> type[ctypes.Array[ctypes.c_long]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_ulong"], type[ctypes.c_ulong]],
) -> type[ctypes.Array[ctypes.c_ulong]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_int"], type[ctypes.c_int]],
) -> type[ctypes.Array[ctypes.c_int]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_uint"], type[ctypes.c_uint]],
) -> type[ctypes.Array[ctypes.c_uint]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_float"], type[ctypes.c_float]],
) -> type[ctypes.Array[ctypes.c_float]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_double"], type[ctypes.c_double]],
) -> type[ctypes.Array[ctypes.c_double]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_longdouble"], type[ctypes.c_longdouble]],
) -> type[ctypes.Array[ctypes.c_longdouble]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_longlong"], type[ctypes.c_longlong]],
) -> type[ctypes.Array[ctypes.c_longlong]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_ulonglong"], type[ctypes.c_ulonglong]],
) -> type[ctypes.Array[ctypes.c_ulonglong]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_ubyte"], type[ctypes.c_ubyte]],
) -> type[ctypes.Array[ctypes.c_ubyte]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_byte"], type[ctypes.c_byte]],
) -> type[ctypes.Array[ctypes.c_byte]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_char"], type[ctypes.c_char]],
) -> type[c_char_array]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_char_p"], type[ctypes.c_char_p]],
) -> type[ctypes.Array[ctypes.c_char_p]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_void_p"], type[ctypes.c_void_p]],
) -> type[ctypes.Array[ctypes.c_void_p]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_bool"], type[ctypes.c_bool]],
) -> type[ctypes.Array[ctypes.c_bool]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_wchar_p"], type[ctypes.c_wchar_p]],
) -> type[ctypes.Array[ctypes.c_wchar_p]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_wchar"], type[ctypes.c_wchar]],
) -> type[c_wchar_array]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_size_t"], type[ctypes.c_size_t]],
) -> type[ctypes.Array[ctypes.c_size_t]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_ssize_t"], type[ctypes.c_ssize_t]],
) -> type[ctypes.Array[ctypes.c_ssize_t]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_int8"], type[ctypes.c_int8]],
) -> type[ctypes.Array[ctypes.c_int8]]: ...


@typing.overload
def array_of(
    tp: typing.Union[typing.Literal["c_uint8"], type[ctypes.c_uint8]],
) -> type[ctypes.Array[ctypes.c_uint8]]: ...


@typing.overload
def array_of(tp: type[_XCT]) -> type[ctypes.Array[_XCT]]: ...


@typing.overload
def array_of(
    tp: str,
) -> typing.Union[type[ctypes.Array[typing.Any]], type[CArrayField[typing.Any, typing.Any]]]: ...


def array_of(tp):
    """
    A shortcut to get specific array type for given type or name.

    :param tp: Type or name of the type to get array for.
    :return: Array type or CArrayField for given type or name, without array size.
    """
    if isinstance(tp, str):
        from inspect import currentframe

        fr = currentframe()
        if fr is not None:
            fr = fr.f_back
        ctx: dict[str, CTypes] = fr.f_globals if fr is not None else {}
        if tp not in ctx:
            return globals().get(tp + "_array", ctypes.Array[getattr(ctypes, tp)])
        return globals().get(tp + "_array", ctypes.Array[getattr(ctypes, tp, ctx[tp])])
    elif isinstance(tp, ctypes._SimpleCData):
        return globals().get(getattr(tp, "__name__") + "_array", ctypes.Array[tp])
    return ctypes.Array[tp]
