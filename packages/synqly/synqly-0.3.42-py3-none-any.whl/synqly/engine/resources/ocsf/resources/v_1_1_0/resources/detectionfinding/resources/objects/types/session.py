# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..........core.datetime_utils import serialize_datetime
from ...base.types.timestamp import Timestamp

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class Session(pydantic.BaseModel):
    """
    The Session object describes details about an authenticated session. e.g. Session Creation Time, Session Issuer. Defined by D3FEND <a target='_blank' href='https://d3fend.mitre.org/dao/artifact/d3f:Session/'>d3f:Session</a>.
    """

    count: typing.Optional[int] = pydantic.Field(default=None)
    """
    The number of identical sessions spawned from the same source IP, destination IP, application, and content/threat type seen over a period of time.
    """

    created_time: typing.Optional[Timestamp] = pydantic.Field(default=None)
    """
    The time when the session was created.
    """

    created_time_dt: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The time when the session was created.
    """

    credential_uid: typing.Optional[str] = pydantic.Field(default=None)
    """
    The unique identifier of the user's credential. For example, AWS Access Key ID.
    """

    expiration_reason: typing.Optional[str] = pydantic.Field(default=None)
    """
    The reason which triggered the session expiration.
    """

    expiration_time: typing.Optional[Timestamp] = pydantic.Field(default=None)
    """
    The session expiration time.
    """

    expiration_time_dt: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The session expiration time.
    """

    is_mfa: typing.Optional[bool] = pydantic.Field(default=None)
    """
    Indicates whether Multi Factor Authentication was used during authentication.
    """

    is_remote: typing.Optional[bool] = pydantic.Field(default=None)
    """
    The indication of whether the session is remote.
    """

    is_vpn: typing.Optional[bool] = pydantic.Field(default=None)
    """
    The indication of whether the session is a VPN session.
    """

    issuer: typing.Optional[str] = pydantic.Field(default=None)
    """
    The identifier of the session issuer.
    """

    terminal: typing.Optional[str] = pydantic.Field(default=None)
    """
    The Pseudo Terminal associated with the session. Ex: the tty or pts value.
    """

    uid: typing.Optional[str] = pydantic.Field(default=None)
    """
    The unique identifier of the session.
    """

    uid_alt: typing.Optional[str] = pydantic.Field(default=None)
    """
    The alternate unique identifier of the session. e.g. AWS ARN - <code>arn:aws:sts::123344444444:assumed-role/Admin/example-session</code>.
    """

    uuid_: typing.Optional[str] = pydantic.Field(alias="uuid", default=None)
    """
    The universally unique identifier of the session.
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
        allow_population_by_field_name = True
        extra = pydantic.Extra.allow
        json_encoders = {dt.datetime: serialize_datetime}
