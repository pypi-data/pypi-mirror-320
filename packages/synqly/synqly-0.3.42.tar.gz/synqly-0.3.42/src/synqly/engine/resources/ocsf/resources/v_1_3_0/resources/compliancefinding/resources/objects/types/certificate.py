# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..........core.datetime_utils import serialize_datetime
from ...base.types.timestamp import Timestamp
from .fingerprint import Fingerprint

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class Certificate(pydantic.BaseModel):
    """
    The Digital Certificate, also known as a Public Key Certificate, object contains information about the ownership and usage of a public key. It serves as a means to establish trust in the authenticity and integrity of the public key and the associated entity. Defined by D3FEND <a target='_blank' href='https://d3fend.mitre.org/dao/artifact/d3f:Certificate/'>d3f:Certificate</a>.
    """

    created_time: typing.Optional[Timestamp] = pydantic.Field(default=None)
    """
    The time when the certificate was created.
    """

    created_time_dt: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The time when the certificate was created.
    """

    expiration_time: typing.Optional[Timestamp] = pydantic.Field(default=None)
    """
    The expiration time of the certificate.
    """

    expiration_time_dt: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The expiration time of the certificate.
    """

    fingerprints: typing.List[Fingerprint] = pydantic.Field()
    """
    The fingerprint list of the certificate.
    """

    is_self_signed: typing.Optional[bool] = pydantic.Field(default=None)
    """
    Denotes whether a digital certificate is self-signed or signed by a known certificate authority (CA).
    """

    issuer: str = pydantic.Field()
    """
    The certificate issuer distinguished name.
    """

    serial_number: str = pydantic.Field()
    """
    The serial number of the certificate used to create the digital signature.
    """

    subject: typing.Optional[str] = pydantic.Field(default=None)
    """
    The certificate subject distinguished name.
    """

    uid: typing.Optional[str] = pydantic.Field(default=None)
    """
    The unique identifier of the certificate.
    """

    version: typing.Optional[str] = pydantic.Field(default=None)
    """
    The certificate version.
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
