"""MinIO filesystem driver for Masonite 5.

MinIO speaks the S3 API, so this extends Masonite's built-in ``AmazonS3Driver``
and only changes how the boto3 connection is built: it targets a custom MinIO
endpoint and forces path-style addressing (boto3 defaults to virtual-host style,
which does not work against a custom S3 endpoint).
"""

from botocore.client import Config
from masonite.filesystem.drivers import AmazonS3Driver


class _MinioSession:
    """Wrap a boto3 ``Session`` so every ``resource()``/``client()`` call defaults
    to the MinIO endpoint and path-style addressing.

    The parent driver's methods all call ``get_connection().resource("s3")`` with
    no keyword arguments, so injecting the endpoint here lets us reuse every
    inherited file operation unchanged.
    """

    def __init__(self, session, endpoint):
        self._session = session
        self._endpoint = endpoint

    def _defaults(self, kwargs):
        kwargs.setdefault("endpoint_url", self._endpoint)
        # MinIO requires path-style addressing and SigV4 signatures.
        kwargs.setdefault(
            "config",
            Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        return kwargs

    def resource(self, name, **kwargs):
        return self._session.resource(name, **self._defaults(kwargs))

    def client(self, name, **kwargs):
        return self._session.client(name, **self._defaults(kwargs))


class MinioDriver(AmazonS3Driver):
    def get_connection(self):
        try:
            import boto3
        except ImportError:
            raise ModuleNotFoundError(
                "Could not find the 'boto3' library. Run 'pip install boto3' to fix this."
            ) from None

        if not self.connection:
            session = boto3.Session(
                aws_access_key_id=self.options.get("client"),
                aws_secret_access_key=self.options.get("secret"),
                region_name=self.options.get("region", "us-east-1"),
            )
            self.connection = _MinioSession(session, self.options.get("endpoint"))

        return self.connection

    def get_secure_url(self, path, expires=3600):
        """Return a presigned (time-limited) URL for ``path``.

        This is generated client-side — it does not contact the server.
        """
        return (
            self.get_connection()
            .client("s3")
            .generate_presigned_url(
                "get_object",
                Params={"Bucket": self.get_bucket(), "Key": path},
                ExpiresIn=expires,
            )
        )
