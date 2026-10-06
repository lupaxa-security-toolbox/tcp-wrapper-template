#!/usr/bin/env python3
"""TCP Wrapper filter template.

Copy this file, set ``ACTION`` and ``BAN_LIST``, and replace :func:`lookup`.
Exit 0 allows the connection. Exit 1 denies it.

The multiplexer calls this filter as ``<filter> <client-ip> MUX``.
"""

from __future__ import annotations

import contextlib
import sys
import syslog

__version__ = "0.1.0"

ALLOW_ACTION = "ALLOW"
DENY_ACTION = "DENY"

# Space-separated or comma-separated values matched by check_results.
BAN_LIST = ""

# DENY blocks a listed value. ALLOW blocks a value that is not listed.
ACTION = DENY_ACTION

IP = ""
MUX = False


def get_version() -> str:
    """Return the package version string."""
    return __version__


def in_multiplexer() -> bool:
    """Return whether the multiplexer started this filter."""
    return MUX


def in_terminal() -> bool:
    """Return whether stdout is a terminal."""
    return sys.stdout.isatty()


def debug(message: str = "") -> None:
    """Print when a person or the multiplexer can see it, and log the message."""
    if not message:
        return
    if in_terminal() or in_multiplexer():
        print(message)
    with contextlib.suppress(OSError):
        syslog.syslog(message)


def _listed(item: str, ban_list: str) -> bool:
    tokens = {token.casefold() for token in ban_list.replace(",", " ").split() if token}
    return item.casefold() in tokens


def check_results(item: str, ban_list: str) -> None:
    """Deny the connection when ``item`` fails the ``ACTION`` rule.

    Parameters
    ----------
    item :
        Value returned by :func:`lookup`, such as an ASN or a country code.
    ban_list :
        Space-separated or comma-separated values to match.
    """
    matched = _listed(item, ban_list)
    if ACTION == DENY_ACTION:
        response = DENY_ACTION if matched else ALLOW_ACTION
    else:
        response = ALLOW_ACTION if matched else DENY_ACTION
    if response == DENY_ACTION:
        debug(f"{response} sshd connection from {IP} ({item}) version {__version__}")
        raise SystemExit(1)


def lookup(ip: str) -> str:
    """Return the value to check for this client address.

    Replace this body with an ASN or country lookup. The sample value is not
    on an empty ``BAN_LIST``, so the filter allows the connection.

    Parameters
    ----------
    ip :
        Client address from TCP Wrappers.

    Returns
    -------
    str
        Value passed to :func:`check_results`.
    """
    # The sample ignores the address. Replace this return with an ASN or country lookup.
    return "item1"


def handle_blocks() -> None:
    """Look up the client and apply the allow or deny rule."""
    check_results(lookup(IP), BAN_LIST)


def main(argv: list[str] | None = None) -> None:
    """Run the filter for one client address.

    Parameters
    ----------
    argv :
        Arguments after the program name. ``--version`` prints the template
        version. Otherwise the first argument is the client address, and a
        second argument means the multiplexer started this filter.
    """
    global IP, MUX

    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"--version", "-V"}:
        print(f"tcp-wrapper-template {__version__}")
        raise SystemExit(0)

    if not args or not args[0]:
        debug("Ip addressed not supplied - Aborting")
        raise SystemExit(0)

    IP = args[0]
    MUX = len(args) > 1 and bool(args[1])
    handle_blocks()
    raise SystemExit(0)


if __name__ == "__main__":
    main()
