import os
from pathlib import Path

import pytest
from hypothesis import settings

from localitylens.data.manifest import SnapshotManifest
from tests.support.synthetic_gnis import synthetic_manifest, write_gnis_zips

settings.register_profile("default", max_examples=100, deadline=None)
settings.register_profile("thorough", max_examples=5000, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))


@pytest.fixture
def gnis_snapshot(tmp_path: Path) -> tuple[Path, SnapshotManifest]:
    directory = tmp_path / "raw"
    write_gnis_zips(directory)
    return directory, synthetic_manifest(directory)
