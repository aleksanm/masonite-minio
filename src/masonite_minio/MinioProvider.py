"""Masonite 5 service provider that registers the MinIO filesystem driver."""

from masonite.packages import PackageProvider

from .MinioDriver import MinioDriver


class MinioProvider(PackageProvider):
    def configure(self):
        # Package identity. `root` must match the importable package path so the
        # framework can resolve the package directory after installation.
        (
            self.root("masonite_minio")
            .vendor_name("aleksanm")
            .name("minio")
        )

    def boot(self):
        # Register the "minio" disk driver onto the storage manager. boot() runs
        # after every provider has registered, so the "storage" binding (from the
        # framework's StorageProvider) is guaranteed to exist.
        self.application.make("storage").add_driver(
            "minio", MinioDriver(self.application)
        )
