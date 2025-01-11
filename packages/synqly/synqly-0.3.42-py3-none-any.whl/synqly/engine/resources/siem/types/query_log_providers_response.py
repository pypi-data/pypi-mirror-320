# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from ...common.types.query_status import QueryStatus
from .log_provider import LogProvider

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class QueryLogProvidersResponse(pydantic.BaseModel):
    result: typing.List[LogProvider] = pydantic.Field()
    """
    List of available metadata.log_provider values available for querying events
    """

    cursor: str = pydantic.Field()
    """
    Cursor to use to retrieve the next page of results
    """

    status: QueryStatus = pydantic.Field()
    """
    If the provider supports asynchronous queries and the query is still running, this will be PENDING. There will be a value in the `cursor` field allowing you to continue polling for results.
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
