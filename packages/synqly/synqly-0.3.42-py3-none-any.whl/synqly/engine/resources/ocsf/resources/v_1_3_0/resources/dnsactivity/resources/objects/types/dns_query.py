# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..........core.datetime_utils import serialize_datetime
from ...base.types.hostname import Hostname
from .dns_query_opcode_id import DnsQueryOpcodeId

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class DnsQuery(pydantic.BaseModel):
    """
    The DNS query object represents a specific request made to the Domain Name System (DNS) to retrieve information about a domain or perform a DNS operation. This object encapsulates the necessary attributes and methods to construct and send DNS queries, specify the query type (e.g., A, AAAA, MX). Defined by D3FEND <a target='_blank' href='https://d3fend.mitre.org/dao/artifact/d3f:DNSLookup/'>d3f:DNSLookup</a>.
    """

    class_: typing.Optional[str] = pydantic.Field(alias="class", default=None)
    """
    The class of resource records being queried. See <a target='_blank' href='https://www.rfc-editor.org/rfc/rfc1035.txt'>RFC1035</a>. For example: <code>IN</code>.
    """

    hostname: Hostname = pydantic.Field()
    """
    The hostname or domain being queried. For example: <code>www.example.com</code>
    """

    opcode: typing.Optional[str] = pydantic.Field(default=None)
    """
    The DNS opcode specifies the type of the query message.
    """

    opcode_id: typing.Optional[DnsQueryOpcodeId] = pydantic.Field(default=None)
    """
    The DNS opcode ID specifies the normalized query message type as defined in <a target='_blank' href='https://www.rfc-editor.org/rfc/rfc5395.html'>RFC-5395</a>.
    """

    packet_uid: typing.Optional[int] = pydantic.Field(default=None)
    """
    The DNS packet identifier assigned by the program that generated the query. The identifier is copied to the response.
    """

    type: typing.Optional[str] = pydantic.Field(default=None)
    """
    The type of resource records being queried. See <a target='_blank' href='https://www.rfc-editor.org/rfc/rfc1035.txt'>RFC1035</a>. For example: A, AAAA, CNAME, MX, and NS.
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
