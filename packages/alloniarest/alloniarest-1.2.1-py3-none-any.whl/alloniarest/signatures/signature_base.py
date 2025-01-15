import hmac
from hashlib import sha256
from urllib.parse import quote

# Loosely based on:
# https://github.com/boto/botocore/blob/develop/botocore/auth.py


def sign(key, msg, hexa=False):
    if hexa:
        sig = hmac.new(key, msg.encode("utf-8"), sha256).hexdigest()
    else:
        sig = hmac.new(key, msg.encode("utf-8"), sha256).digest()
    return sig


class SignatureBase:
    def __init__(self, request, logger, header_prefix, data):
        self._req = request
        self._log = logger
        self._header_prefix = header_prefix
        self._req_data = data
        self._signed_headers = {}

    @property
    def canonical_request(self):
        result = (
            f"{self._req.method.upper()}\n{self.canonical_uri}\n"
            f"{self.canonical_query_string}\n{self.canonical_headers}\n"
            f"{self.signed_headers}\n{self.hashed_payload}"
        )

        self._log.debug(f"--- Canonical request ---\n{result}\n")
        return result

    @property
    def canonical_uri(self):
        # We might need to url encode this path
        return quote(self._req.path)

    @property
    def canonical_query_string(self):
        key_val_pairs = [
            (quote(key, safe="-_.~"), quote(str(value), safe="-_.~"))
            for key in self._req.args
            for value in self._req.args.getlist(key)
        ]
        sorted_key_vals = [
            f"{key}={value}" for key, value in sorted(key_val_pairs)
        ]
        return "&".join(sorted_key_vals)

    @property
    def canonical_headers(self):
        _headers = []
        for key in sorted(self._signed_headers.keys()):
            value = self._signed_headers[key]
            _headers.append(f"{key.lower()}:{value}\n")
        return "".join(_headers)

    @property
    def signed_headers(self):
        return ";".join(sorted(self._signed_headers.keys()))

    @property
    def hashed_payload(self):
        return sha256(self._req_data).hexdigest()

    @property
    def timestamp(self):
        return self._signed_headers["x-amz-date"]

    @property
    def timestamp_short(self):
        return self.timestamp[0:8]

    @property
    def service(self):
        return "s3"

    @property
    def region(self):
        return None

    @property
    def credential_scope(self):
        return (
            f"{self.timestamp_short}/{self.region}/{self.service}"
            "/aws4_request"
        )

    @property
    def string_to_sign(self):
        return "\n".join(
            [
                self._header_prefix,
                self.timestamp,
                self.credential_scope,
                sha256(self.canonical_request.encode("utf-8")).hexdigest(),
            ]
        )

    def compute_signature_for(self, private_key):
        k_date = sign(
            ("AWS4" + private_key).encode("utf-8"), self.timestamp_short
        )
        k_region = sign(k_date, self.region)
        k_service = sign(k_region, self.service)
        k_signing = sign(k_service, "aws4_request")
        sts = self.string_to_sign
        self._log.debug(f"--- string_to_sign ---\n{sts}\n---")
        return sign(k_signing, sts, hexa=True)
