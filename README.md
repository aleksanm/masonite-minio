# masonite-minio

A [MinIO](https://min.io/) (S3-compatible) filesystem driver for the
**Masonite 5** framework. It extends Masonite's built-in S3 driver to target a
custom MinIO endpoint with path-style addressing, and adds presigned URLs.

## Install

```bash
pip install masonite-minio
```

## Setup

**1. Register the provider** in `config/providers.py`:

```python
from masonite_minio import MinioProvider

PROVIDERS = [
    # ... framework providers ...
    MinioProvider,
]
```

The driver is registered in the provider's `register()` phase, so placement is
flexible — just keep `MinioProvider` after the framework's `StorageProvider`
(appending it at the end of the list, as above, satisfies this).

**2. Add a `minio` disk** to the `DISKS` dict in `config/filesystem.py`:

```python
from masonite.environment import env

DISKS = {
    # ... existing disks ...
    "minio": {
        "driver": "minio",
        "client": env("MINIO_CLIENT"),
        "secret": env("MINIO_SECRET"),
        "bucket": env("MINIO_BUCKET"),
        "endpoint": env("MINIO_ENDPOINT", "http://127.0.0.1:9000"),
        "region": env("MINIO_REGION", "us-east-1"),
    },
}
```

> A copy of this block ships at `masonite_minio/config/minio.py` for reference.
> The driver reads options from `DISKS`, so the disk must be defined there — a
> standalone config file is not picked up automatically.

**3. Set environment variables** in `.env`:

```ini
MINIO_CLIENT=minioadmin
MINIO_SECRET=minioadmin
MINIO_BUCKET=my-bucket
MINIO_ENDPOINT=http://127.0.0.1:9000

# optional: make minio the default disk
FILESYSTEM_DISK=minio
```

## Usage

```python
from masonite.facades import Storage

Storage.disk("minio").put_file("avatars", uploaded_file)
contents = Storage.disk("minio").get("avatars/photo.png")
exists = Storage.disk("minio").exists("avatars/photo.png")

# presigned, time-limited URL (generated client-side)
url = Storage.disk("minio").get_secure_url("avatars/photo.png", expires=3600)
```

All standard Masonite filesystem operations are supported (`put`, `put_file`,
`get`, `exists`, `missing`, `stream`, `copy`, `move`, `delete`, `get_files`,
`store`), inherited from the framework's S3 driver.

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
pytest
```

Unit tests run offline. Integration tests against a live MinIO are skipped
unless `MINIO_TEST_ENDPOINT` (+ `MINIO_TEST_CLIENT/SECRET/BUCKET`) are set:

```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

This publishes two ports: the **S3 API** on `9000` (use this for
`MINIO_ENDPOINT`) and the **web console** on `9001`
(http://127.0.0.1:9001, log in with `minioadmin` / `minioadmin`). Without
`--console-address`, MinIO binds the console to a random internal port that
isn't reachable from the host. A fresh server has no buckets — create
`MINIO_TEST_BUCKET` from the console before running the integration tests.

## Releasing

Releases are published to PyPI automatically by `.github/workflows/publish.yml`
using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) —
no API tokens are stored in the repo.

**One-time PyPI setup** (per project): on PyPI go to the project's
*Settings → Publishing → Add a new pending/trusted publisher* and register:

| Field | Value |
|-------|-------|
| Owner | `aleksanm` |
| Repository | `masonite-minio` |
| Workflow name | `publish.yml` |
| Environment | `pypi` |

**To cut a release:**

1. Bump `version` in `pyproject.toml` and commit.
2. Tag it: `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin main vX.Y.Z`.
3. Publish a GitHub Release for that tag (e.g. `gh release create vX.Y.Z --generate-notes`).

Publishing the Release triggers the workflow, which builds the sdist + wheel,
verifies the built version matches the tag, and uploads to PyPI. (Adding the
GitHub `pypi` environment under *Settings → Environments* lets you gate the
publish step with required reviewers.)

## License

MIT
