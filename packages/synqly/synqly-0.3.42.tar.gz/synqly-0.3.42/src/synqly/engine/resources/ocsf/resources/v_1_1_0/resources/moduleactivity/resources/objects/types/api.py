# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..........core.datetime_utils import serialize_datetime
from .group import Group
from .request import Request
from .response import Response
from .service import Service

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class Api(pydantic.BaseModel):
    """
    The API, or Application Programming Interface, object represents information pertaining to an API request and response.
    """

    group: typing.Optional[Group] = pydantic.Field(default=None)
    """
    The information pertaining to the API group.
    """

    operation: str = pydantic.Field()
    """
    Verb/Operation associated with the request
    """

    request: typing.Optional[Request] = pydantic.Field(default=None)
    """
    Details pertaining to the API request.
    """

    response: typing.Optional[Response] = pydantic.Field(default=None)
    """
    Details pertaining to the API response.
    """

    service: typing.Optional[Service] = pydantic.Field(default=None)
    """
    The information pertaining to the API service.
    """

    version: typing.Optional[str] = pydantic.Field(default=None)
    """
    The version of the API service.
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
