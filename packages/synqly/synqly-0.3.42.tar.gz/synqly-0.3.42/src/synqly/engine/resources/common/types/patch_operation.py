# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ....core.datetime_utils import serialize_datetime
from .patch_op import PatchOp

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class PatchOperation(pydantic.BaseModel):
    """
    JSON patch to apply. A JSON patch is a list of patch operations. (see https://jsonpatch.com/)
    """

    op: PatchOp = pydantic.Field()
    """
    The operation to perform. Supported values are `add`, `copy`, `move`, `replace`, `remove`, and `test`.
    """

    path: str = pydantic.Field()
    """
    The path to the field to update. The path is a JSON Pointer.
    """

    from_: typing.Optional[str] = pydantic.Field(alias="from", default=None)
    """
    The path to the field to copy from. This is required for `copy` and `move` operations.
    """

    value: typing.Optional[typing.Any] = pydantic.Field(default=None)
    """
    The value to set the field to. This is required for `add`, `replace` and `test` operations.
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
