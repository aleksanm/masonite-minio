import os

import pytest

from masonite_minio import MinioDriver
from masonite_minio.MinioDriver import _MinioSession

ENDPOINT = "http://127.0.0.1:9000"


@pytest.fixture
def driver():
    # The driver's connection/URL logic does not use the application container,
    # so None is fine for unit tests.
    return MinioDriver(None).set_options(
        {
            "client": "minioadmin",
            "secret": "minioadmin",
            "bucket": "test-bucket",
            "endpoint": ENDPOINT,
        }
    )


def test_connection_is_endpoint_scoped(driver):
    conn = driver.get_connection()
    assert isinstance(conn, _MinioSession)
    assert conn._endpoint == ENDPOINT


def test_get_secure_url_is_presigned_and_path_style(driver):
    # generate_presigned_url is computed client-side, so this needs no server.
    url = driver.get_secure_url("photos/cat.png", expires=120)
    assert url.startswith(ENDPOINT)
    # path-style addressing puts the bucket in the path, not a subdomain
    assert "test-bucket/photos/cat.png" in url
    assert "X-Amz-Signature=" in url


@pytest.mark.skipif(
    not os.environ.get("MINIO_TEST_ENDPOINT"),
    reason="set MINIO_TEST_ENDPOINT (and a running MinIO) to run integration tests",
)
def test_put_and_get_roundtrip():
    driver = MinioDriver(None).set_options(
        {
            "client": os.environ["MINIO_TEST_CLIENT"],
            "secret": os.environ["MINIO_TEST_SECRET"],
            "bucket": os.environ["MINIO_TEST_BUCKET"],
            "endpoint": os.environ["MINIO_TEST_ENDPOINT"],
        }
    )
    driver.put("hello.txt", "world")
    assert driver.exists("hello.txt")
    assert driver.get("hello.txt") == "world"
    driver.delete("hello.txt")
    assert driver.missing("hello.txt")
