from importlib.metadata import version

import masonite_minio


def test_version_is_exposed_and_matches_metadata():
    assert masonite_minio.__version__ == version("masonite-minio")
    assert "__version__" in masonite_minio.__all__
