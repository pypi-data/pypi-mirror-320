# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from .scan_schedule import ScanSchedule
from .user import User

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class ScanConfiguration(pydantic.BaseModel):
    """
    Configuration options of a scan.
    """

    uid: str = pydantic.Field()
    """
    ID of the scan.
    """

    name: str = pydantic.Field()
    """
    Name of the scan.
    """

    creation_time: typing.Optional[int] = pydantic.Field(default=None)
    """
    Time when the scan was created.
    """

    last_modified_time: typing.Optional[int] = pydantic.Field(default=None)
    """
    Time when the scan was last modified.
    """

    owner: typing.Optional[User] = pydantic.Field(default=None)
    """
    User that owns the scan.
    """

    schedule: typing.Optional[ScanSchedule] = pydantic.Field(default=None)
    """
    Schedule of the scan if it is a recurring scan.
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
