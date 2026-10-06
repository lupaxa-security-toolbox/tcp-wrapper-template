"""Package version metadata."""

from __future__ import annotations

import template
from template import get_version


def test_version_is_semver_like() -> None:
    assert isinstance(template.__version__, str)
    parts = template.__version__.split(".")
    assert len(parts) >= 2
    assert all(part.isdigit() for part in parts[:2])


def test_get_version_matches_dunder() -> None:
    assert get_version() == template.__version__
