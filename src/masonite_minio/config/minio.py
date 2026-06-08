"""Example MinIO disk configuration.

This is NOT loaded automatically. Masonite reads disk options from the ``DISKS``
dict in your application's ``config/filesystem.py``. Copy the block below into
that dict (and set the ``MINIO_*`` env vars) to enable the "minio" disk.
"""

from masonite.environment import env

MINIO_DISK = {
    "driver": "minio",
    "client": env("MINIO_CLIENT"),
    "secret": env("MINIO_SECRET"),
    "bucket": env("MINIO_BUCKET"),
    "endpoint": env("MINIO_ENDPOINT", "http://127.0.0.1:9000"),
    "region": env("MINIO_REGION", "us-east-1"),
}
