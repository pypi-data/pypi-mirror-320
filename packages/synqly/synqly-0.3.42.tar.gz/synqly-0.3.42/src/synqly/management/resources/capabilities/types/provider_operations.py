# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from .provider_filter import ProviderFilter

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class ProviderOperations(pydantic.BaseModel):
    name: str = pydantic.Field()
    """
    Name of the operation.
    """

    supported: bool = pydantic.Field()
    """
    Whether the operation is supported by the provider.
    """

    required_fields: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    List of fields in the request body that are required by the provider for this
    operation. Due to limitations of the OpenAPI format these fields may be marked as
    optional, even though they are in fact required by this provider.
    """

    supported_response_fields: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    List of fields that may be returned in the response body. Any fields not listed in this array are not supported by this provider and will not be returned in the response body.
    """

    filters: typing.Optional[typing.List[ProviderFilter]] = pydantic.Field(default=None)
    """
    Filters that can be applied to this operation.
    """

    request_body: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default=None)
    """
    If this operation requires a request body, this field will contain the schema for
    the request. The is a json schema object. This field is only present when getting
    the capabilities for a specific provider.
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
