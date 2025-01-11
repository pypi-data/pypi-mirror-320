# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.jsonable_encoder import jsonable_encoder
from ...core.remove_none_from_dict import remove_none_from_dict
from ...core.request_options import RequestOptions
from ..common.errors.bad_gateway_error import BadGatewayError
from ..common.errors.bad_request_error import BadRequestError
from ..common.errors.conflict_error import ConflictError
from ..common.errors.forbidden_error import ForbiddenError
from ..common.errors.gateway_timeout_error import GatewayTimeoutError
from ..common.errors.internal_server_error import InternalServerError
from ..common.errors.method_not_allowed_error import MethodNotAllowedError
from ..common.errors.not_found_error import NotFoundError
from ..common.errors.not_implemented_error import NotImplementedError
from ..common.errors.service_unavailable_error import ServiceUnavailableError
from ..common.errors.too_many_requests_error import TooManyRequestsError
from ..common.errors.unauthorized_error import UnauthorizedError
from ..common.errors.unsupported_media_type_error import UnsupportedMediaTypeError
from ..common.types.error_body import ErrorBody
from .types.create_notification_request import CreateNotificationRequest
from .types.create_notification_response import CreateNotificationResponse
from .types.get_notification_response import GetNotificationResponse
from .types.notification_id import NotificationId

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class NotificationsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def get_message(
        self, notification_id: NotificationId, *, request_options: typing.Optional[RequestOptions] = None
    ) -> GetNotificationResponse:
        """
        Returns the `Notification` object matching `{notificationId}` from the token-linked
        `Integration`.

        Parameters:
            - notification_id: NotificationId.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"v1/notifications/get/{jsonable_encoder(notification_id)}"
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else 60,
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(GetNotificationResponse, _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise ForbiddenError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 415:
            raise UnsupportedMediaTypeError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 429:
            raise TooManyRequestsError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 501:
            raise NotImplementedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 502:
            raise BadGatewayError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 503:
            raise ServiceUnavailableError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 504:
            raise GatewayTimeoutError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def create_message(
        self, *, request: CreateNotificationRequest, request_options: typing.Optional[RequestOptions] = None
    ) -> CreateNotificationResponse:
        """
        Creates a `Notification` object in the token-linked `Integration`.

        Parameters:
            - request: CreateNotificationRequest.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "v1/notifications/create"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            json=jsonable_encoder(request)
            if request_options is None or request_options.get("additional_body_parameters") is None
            else {
                **jsonable_encoder(request),
                **(jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))),
            },
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else 60,
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(CreateNotificationResponse, _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise ForbiddenError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 415:
            raise UnsupportedMediaTypeError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 429:
            raise TooManyRequestsError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 501:
            raise NotImplementedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 502:
            raise BadGatewayError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 503:
            raise ServiceUnavailableError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 504:
            raise GatewayTimeoutError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def clear_message(
        self, notification_id: NotificationId, *, request_options: typing.Optional[RequestOptions] = None
    ) -> None:
        """
        Resolves a `Notification` object in the token-linked `Integration`.

        Parameters:
            - notification_id: NotificationId.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"v1/notifications/clear/{jsonable_encoder(notification_id)}"
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            json=jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))
            if request_options is not None
            else None,
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else 60,
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise ForbiddenError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 415:
            raise UnsupportedMediaTypeError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 429:
            raise TooManyRequestsError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 501:
            raise NotImplementedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 502:
            raise BadGatewayError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 503:
            raise ServiceUnavailableError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 504:
            raise GatewayTimeoutError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncNotificationsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def get_message(
        self, notification_id: NotificationId, *, request_options: typing.Optional[RequestOptions] = None
    ) -> GetNotificationResponse:
        """
        Returns the `Notification` object matching `{notificationId}` from the token-linked
        `Integration`.

        Parameters:
            - notification_id: NotificationId.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = await self._client_wrapper.httpx_client.request(
            "GET",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"v1/notifications/get/{jsonable_encoder(notification_id)}"
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else 60,
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(GetNotificationResponse, _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise ForbiddenError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 415:
            raise UnsupportedMediaTypeError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 429:
            raise TooManyRequestsError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 501:
            raise NotImplementedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 502:
            raise BadGatewayError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 503:
            raise ServiceUnavailableError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 504:
            raise GatewayTimeoutError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def create_message(
        self, *, request: CreateNotificationRequest, request_options: typing.Optional[RequestOptions] = None
    ) -> CreateNotificationResponse:
        """
        Creates a `Notification` object in the token-linked `Integration`.

        Parameters:
            - request: CreateNotificationRequest.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "v1/notifications/create"),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            json=jsonable_encoder(request)
            if request_options is None or request_options.get("additional_body_parameters") is None
            else {
                **jsonable_encoder(request),
                **(jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))),
            },
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else 60,
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(CreateNotificationResponse, _response.json())  # type: ignore
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise ForbiddenError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 415:
            raise UnsupportedMediaTypeError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 429:
            raise TooManyRequestsError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 501:
            raise NotImplementedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 502:
            raise BadGatewayError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 503:
            raise ServiceUnavailableError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 504:
            raise GatewayTimeoutError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def clear_message(
        self, notification_id: NotificationId, *, request_options: typing.Optional[RequestOptions] = None
    ) -> None:
        """
        Resolves a `Notification` object in the token-linked `Integration`.

        Parameters:
            - notification_id: NotificationId.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/", f"v1/notifications/clear/{jsonable_encoder(notification_id)}"
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            json=jsonable_encoder(remove_none_from_dict(request_options.get("additional_body_parameters", {})))
            if request_options is not None
            else None,
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else 60,
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,  # type: ignore
        )
        if 200 <= _response.status_code < 300:
            return
        if _response.status_code == 400:
            raise BadRequestError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise ForbiddenError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 409:
            raise ConflictError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 415:
            raise UnsupportedMediaTypeError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 429:
            raise TooManyRequestsError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 500:
            raise InternalServerError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 501:
            raise NotImplementedError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 502:
            raise BadGatewayError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 503:
            raise ServiceUnavailableError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        if _response.status_code == 504:
            raise GatewayTimeoutError(pydantic.parse_obj_as(ErrorBody, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
