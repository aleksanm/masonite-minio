"""Masonite 5 service provider that registers the MinIO filesystem driver."""

from masonite.packages import PackageProvider

from .MinioDriver import MinioDriver


class MinioProvider(PackageProvider):
    def configure(self):
        # Package identity. `root` must match the importable package path so the
        # framework can resolve the package directory after installation.
        (self.root("masonite_minio").vendor_name("aleksanm").name("minio"))

    def register(self):
        # PackageProvider.register() runs configure(); keep that behaviour.
        super().register()
        # Register the "minio" disk driver during the *register* phase rather
        # than boot(). The framework runs every provider's register() before any
        # provider's boot(), and RouteProvider.boot() is what dispatches the
        # request to your controller — so registering here guarantees the driver
        # exists before a route can use it, no matter where MinioProvider sits in
        # the PROVIDERS list (as long as it is after the framework's
        # StorageProvider, i.e. the usual "append at the end" placement).
        self._register_driver()

    def boot(self):
        # Safety net for the unusual case where MinioProvider is listed *before*
        # StorageProvider: "storage" was not yet bound during register(), so add
        # the driver now (by boot() every provider has registered). Idempotent.
        self._register_driver()

    def _register_driver(self):
        if not self.application.has("storage"):
            return
        storage = self.application.make("storage")
        if "minio" not in storage.drivers:
            storage.add_driver("minio", MinioDriver(self.application))
