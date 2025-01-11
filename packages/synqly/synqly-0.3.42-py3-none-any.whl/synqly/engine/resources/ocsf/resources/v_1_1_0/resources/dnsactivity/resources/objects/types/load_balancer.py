# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..........core.datetime_utils import serialize_datetime
from .endpoint_connection import EndpointConnection
from .metric import Metric
from .network_endpoint import NetworkEndpoint

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class LoadBalancer(pydantic.BaseModel):
    """
    The load balancer object describes the load balancer entity and contains additional information regarding the distribution of traffic across a network.
    """

    classification: typing.Optional[str] = pydantic.Field(default=None)
    """
    The request classification as defined by the load balancer.
    """

    code: typing.Optional[int] = pydantic.Field(default=None)
    """
    The numeric response status code detailing the connection from the load balancer to the destination target.
    """

    dst_endpoint: typing.Optional[NetworkEndpoint] = pydantic.Field(default=None)
    """
    The destination to which the load balancer is distributing traffic.
    """

    endpoint_connections: typing.Optional[typing.List[EndpointConnection]] = pydantic.Field(default=None)
    """
    An object detailing the load balancer connection attempts and responses.
    """

    error_message: typing.Optional[str] = pydantic.Field(default=None)
    """
    The load balancer error message.
    """

    message: typing.Optional[str] = pydantic.Field(default=None)
    """
    The load balancer message.
    """

    metrics: typing.Optional[typing.List[Metric]] = pydantic.Field(default=None)
    """
    General purpose metrics associated with the load balancer.
    """

    name: typing.Optional[str] = pydantic.Field(default=None)
    """
    The name of the load balancer.
    """

    status_detail: typing.Optional[str] = pydantic.Field(default=None)
    """
    The status detail contains additional status information about the load balancer distribution event.
    """

    uid: typing.Optional[str] = pydantic.Field(default=None)
    """
    The unique identifier for the load balancer.
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
