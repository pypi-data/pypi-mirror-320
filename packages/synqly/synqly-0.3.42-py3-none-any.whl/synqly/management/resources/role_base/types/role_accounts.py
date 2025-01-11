# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from ...integration_base.types.integration_id import IntegrationId
from ...organization_base.types.environment import Environment

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class RoleAccounts(pydantic.BaseModel):
    ids: typing.List[IntegrationId] = pydantic.Field()
    """
    List of account ids that this role definition grants access to. Use "\*" to grant access to all account ids.
    """

    labels: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    List of account labels this role definition grants access to. If both labels and environments are specified both must pass
    """

    environments: typing.Optional[typing.List[Environment]] = pydantic.Field(default=None)
    """
    Account environments this role definition grants access to. If both labels and environments are specified both must pass
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
