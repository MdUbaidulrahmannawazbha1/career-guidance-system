"""Root conftest – ensure the ``backend`` directory is on ``sys.path``."""

import pathlib
import sys

# Add the backend directory to the Python path so that ``import app`` works
# in both local pytest runs and CI environments.
_BACKEND_DIR = str(pathlib.Path(__file__).resolve().parent)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
