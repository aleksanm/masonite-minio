"""Tests for MinioProvider's driver registration.

The provider must register the "minio" disk driver during the *register* phase
so it exists before any provider's boot() runs — in particular before
RouteProvider.boot() dispatches a request to a controller that uses the disk.
See https://github.com/aleksanm/masonite-minio (provider ordering).
"""

import pytest
from masonite.container import Container
from masonite.filesystem import Storage

from masonite_minio import MinioDriver, MinioProvider

DISK_CONFIG = {
    "minio": {
        "driver": "minio",
        "client": "minioadmin",
        "secret": "minioadmin",
        "bucket": "test-bucket",
        "endpoint": "http://127.0.0.1:9000",
    },
}


@pytest.fixture(autouse=True)
def clean_container():
    # masonite's Container stores bindings in a class-level dict, so instances
    # share state across tests. Reset it around each test for isolation.
    Container.objects = {}
    yield
    Container.objects = {}


def _app_with_storage():
    app = Container()
    app.bind("storage", Storage(app, DISK_CONFIG))
    return app


def test_register_adds_minio_driver():
    app = _app_with_storage()
    MinioProvider(app).register()

    drivers = app.make("storage").drivers
    assert "minio" in drivers
    assert isinstance(drivers["minio"], MinioDriver)


def test_disk_is_usable_after_register_without_boot():
    # The whole point of the fix: the disk resolves after register(), without
    # boot() having run (RouteProvider.boot() may dispatch a request first).
    app = _app_with_storage()
    MinioProvider(app).register()

    assert isinstance(app.make("storage").disk("minio"), MinioDriver)


def test_register_then_boot_is_idempotent():
    app = _app_with_storage()
    provider = MinioProvider(app)
    provider.register()
    first = app.make("storage").drivers["minio"]

    provider.boot()  # safety net; must not duplicate or replace the driver
    assert app.make("storage").drivers["minio"] is first


def test_boot_registers_when_storage_bound_after_register():
    # Simulates MinioProvider being listed *before* StorageProvider: "storage"
    # is not bound during register(), so register() is a no-op and boot() (which
    # runs after every provider has registered) picks it up instead.
    app = Container()
    provider = MinioProvider(app)

    provider.register()  # storage not bound yet -> no-op, must not raise
    assert not app.has("storage")

    app.bind("storage", Storage(app, DISK_CONFIG))
    provider.boot()
    assert isinstance(app.make("storage").drivers["minio"], MinioDriver)


def test_register_is_noop_without_storage():
    app = Container()
    # Must not raise even though "storage" is unavailable.
    MinioProvider(app).register()
    assert not app.has("storage")
