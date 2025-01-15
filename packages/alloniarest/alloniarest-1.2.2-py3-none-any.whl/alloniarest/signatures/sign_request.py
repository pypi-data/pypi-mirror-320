from functools import wraps
from urllib.parse import parse_qs, urlsplit

from .signature_builder import SignatureBuilder
from .signature_utils import fill_signature_headers, make_request_info

AWS_AUTH_HEADER_PREFIX = "AWS4-HMAC-SHA256"


def sign_request(function):
    """Signs a request by adding the right headers based on host, user_token
    and user_token_id.
    """

    @wraps(function)
    def decorator(*args, **kwargs):
        client_obj = args[0]
        if client_obj.user_token is None:
            return function(*args, **kwargs)
        user_token = client_obj.user_token.get("token")
        user_token_id = client_obj.user_token.get("id")
        if not user_token or not user_token_id:
            return function(*args, **kwargs)
        host = client_obj.hostname
        prepared_request = function(*args, **kwargs)
        split_result = urlsplit(args[2])
        if "params" not in kwargs:
            kwargs["params"] = parse_qs(split_result.query)
        else:
            kwargs["params"] = {
                **kwargs["params"],
                **parse_qs(split_result.query),
            }
        request_info = make_request_info(
            prepared_request.headers, args[1], split_result.path, **kwargs
        )
        signature = SignatureBuilder(
            request_info,
            client_obj.logger,
            AWS_AUTH_HEADER_PREFIX,
            request_info.data,
        ).build(user_token_id, user_token, host)
        fill_signature_headers(prepared_request.headers, signature)
        return prepared_request

    return decorator
