# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from .tenable_cloud_credential import TenableCloudCredential

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class VulnerabilitiesTenableCloud(pydantic.BaseModel):
    """
    Configuration for Tenable Cloud as a Vulnerabilities Provider
    """

    credential: TenableCloudCredential
    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    URL for the Tenable Cloud API. This should be the base URL for the API, without any path components and must be HTTPS. If not provided, defaults to "https://cloud.tenable.com".
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
