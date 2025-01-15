from datetime import datetime, timezone

from .signature_base import SignatureBase

SIGV4_TIMESTAMP = "%Y%m%dT%H%M%SZ"


class SignatureBuilder(SignatureBase):
    @property
    def region(self):
        return "eu-west-1"

    def build(self, key_id, key_secret, host):
        self._log.debug(
            f"Building signature for {key_id}, {key_secret}, {host}"
        )

        now = datetime.now(tz=timezone.utc)  # noqa: UP017
        timestamp = now.strftime(SIGV4_TIMESTAMP)

        self._signed_headers = {
            "host": host,
            "x-amz-content-sha256": self.hashed_payload,
            "x-amz-date": timestamp,
        }
        # Mandatory as per the s3 api spec
        if "content-type" in self._req.headers:
            self._signed_headers["content-type"] = self._req.headers[
                "content-type"
            ]

        computed_signature = self.compute_signature_for(key_secret)
        credential = f"{key_id}/{self.credential_scope}"
        signed_headers = self.signed_headers
        authorization = (
            self._header_prefix
            + " "
            + ",".join(
                [
                    f"Credential={credential}",
                    f"SignedHeaders={signed_headers}",
                    f"Signature={computed_signature}",
                ]
            )
        )

        result = self._signed_headers.copy()
        result.update({"Authorization": authorization})

        self._log.debug(f"---Signature infos---\n{result}\n---")
        return result
