import shutil
import tempfile
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TEST_TMP_ROOT = _PROJECT_ROOT / ".pytest_tmp"


@pytest.fixture
def tmp_workdir():
    """Provide a temporary working directory under the project tree."""
    _TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    dirpath = Path(tempfile.mkdtemp(dir=_TEST_TMP_ROOT))
    yield dirpath
    shutil.rmtree(dirpath, ignore_errors=True)
