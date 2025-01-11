# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..........core.datetime_utils import serialize_datetime

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class KeyboardInfo(pydantic.BaseModel):
    """
    The Keyboard Information object contains details and attributes related to a computer or device keyboard. It encompasses information that describes the characteristics, capabilities, and configuration of the keyboard.
    """

    function_keys: typing.Optional[int] = pydantic.Field(default=None)
    """
    The number of function keys on client keyboard.
    """

    ime: typing.Optional[str] = pydantic.Field(default=None)
    """
    The Input Method Editor (IME) file name.
    """

    keyboard_layout: typing.Optional[str] = pydantic.Field(default=None)
    """
    The keyboard locale identifier name (e.g., en-US).
    """

    keyboard_subtype: typing.Optional[int] = pydantic.Field(default=None)
    """
    The keyboard numeric code.
    """

    keyboard_type: typing.Optional[str] = pydantic.Field(default=None)
    """
    The keyboard type (e.g., xt, ico).
    """

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        extra = pydantic.Extra.allow
        json_encoders = {dt.datetime: serialize_datetime}
