"""Allow and deny behaviour of the filter template."""

from __future__ import annotations

import pytest

import template


@pytest.fixture(autouse=True)
def _quiet_syslog(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(template.syslog, "syslog", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(template, "BAN_LIST", "")
    monkeypatch.setattr(template, "ACTION", template.DENY_ACTION)
    monkeypatch.setattr(template, "IP", "")
    monkeypatch.setattr(template, "MUX", False)


def _run(argv: list[str]) -> int | str | None:
    with pytest.raises(SystemExit) as exc:
        template.main(argv)
    return exc.value.code


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(["--version"]) == 0
    assert _run(["-V"]) == 0
    captured = capsys.readouterr()
    assert captured.out == f"tcp-wrapper-template {template.__version__}\n" * 2


def test_missing_address_allows() -> None:
    assert _run([]) == 0


def test_sample_lookup_allows() -> None:
    assert _run(["203.0.113.5"]) == 0


def test_deny_listed_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(template, "BAN_LIST", "item1, other")
    assert _run(["203.0.113.5", "MUX"]) == 1
    assert template.MUX is True
    assert template.IP == "203.0.113.5"


def test_deny_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(template, "BAN_LIST", "Item1")
    assert _run(["203.0.113.5"]) == 1


def test_allow_action_blocks_unknown_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(template, "ACTION", template.ALLOW_ACTION)
    assert _run(["203.0.113.5"]) == 1


def test_allow_action_permits_listed_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(template, "ACTION", template.ALLOW_ACTION)
    monkeypatch.setattr(template, "BAN_LIST", "item1")
    assert _run(["203.0.113.5"]) == 0


def test_lookup_returns_the_sample_value() -> None:
    assert template.lookup("203.0.113.5") == "item1"
