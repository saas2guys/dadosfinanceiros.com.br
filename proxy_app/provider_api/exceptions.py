from __future__ import annotations

from rest_framework.exceptions import APIException


class UpstreamAPIException(APIException):
    """Exception representing an upstream provider failure.

    This exception maps upstream transport or service errors to a consistent
    HTTP 502 (Bad Gateway) response. Use this when the proxy cannot fulfill a
    request due to an error returned by, or while contacting, the upstream
    service.

    Attributes:
        status_code: HTTP status code returned to clients (502).
        default_detail: Default JSON body describing the upstream error.
        default_code: DRF error code string.
    """

    status_code = 502
    default_detail = {"detail": "upstream error"}
    default_code = "bad_gateway"
