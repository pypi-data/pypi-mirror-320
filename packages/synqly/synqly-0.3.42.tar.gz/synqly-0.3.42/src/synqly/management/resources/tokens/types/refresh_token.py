# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from ...common.types.base import Base
from ...common.types.id import Id
from ...token_base.types.token_id import TokenId
from ...token_base.types.token_owner_type import TokenOwnerType
from ...token_base.types.token_pair import TokenPair

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class RefreshToken(Base):
    id: TokenId
    member_id: typing.Optional[Id] = pydantic.Field(default=None)
    """
    Member Id
    """

    owner_id: Id = pydantic.Field()
    """
    ID of the entity that owns this token
    """

    owner_type: TokenOwnerType = pydantic.Field()
    """
    Type of the entity that owns this token
    """

    expires: dt.datetime = pydantic.Field()
    """
    Time when this token expires and can no longer be used again.
    """

    token_ttl: str = pydantic.Field()
    """
    Token time-to-live
    """

    primary: TokenPair = pydantic.Field()
    """
    Primary running access and refresh tokens
    """

    secondary: typing.Optional[TokenPair] = pydantic.Field(default=None)
    """
    Temporary secondary TokenPair created after a RefreshToken operation
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
