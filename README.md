<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Security Toolbox" />
  </a>
</p>

<h1 align="center">Tcp Wrapper Template</h1>

Starting point for a TCP Wrapper filter that the [Tcp Wrapper Multiplexer](https://github.com/lupaxa-security-toolbox/tcp-wrapper-multiplexer) can run.

Copy `src/template.sh` or `src/template.py`, name the copy for the check you want, and fill in the allow or deny logic. Use the Python file when the filter has to look something up, such as an ASN or a country.

Exit `0` to allow the connection. Any other exit code denies it, and the multiplexer stops on that result.

> **Note:**
> TCP Wrappers do not replace a firewall. Use a filter as one layer of a larger control.

## Install

Copy your filter to `/usr/local/sbin` and make it executable. The name you install is the name you add to the multiplexer.

```bash
sudo install -m 755 src/template.sh /usr/local/sbin/your-filter
```

`src/template.sh --version` and `src/template.py --version` print the template version. A deny log includes that same version, so an installed copy can be told apart from an older one.

Install the Python template the same way:

```bash
sudo install -m 755 src/template.py /usr/local/sbin/your-filter
```

`main` calls `handle_blocks`. That function is the lookup to replace. The sample value `item1` is not on an empty `BAN_LIST`, so the filter allows the connection until you fill the list in.

## Configure the Check

`ACTION` is `DENY` or `ALLOW`.

- `DENY` blocks a value that matches the list.
- `ALLOW` blocks a value that does not match the list.

`check_results` exits `1` on deny. Allow falls through, and `main` exits `0`.

```bash
BAN_LIST='match-me'
ACTION=$DENY_ACTION
```

Set those at the top of the script. `handle_blocks` looks up one value for this connection and passes it to `check_results`:

```bash
check_results "${value}" "${BAN_LIST}"
```

In `src/template.py`, set the same two names. Replace the `lookup` return value with the ASN, country code, or other value to check:

```python
BAN_LIST = "match-me"
ACTION = DENY_ACTION
```

Set those at the top of the file. `lookup` returns the value for this connection:

```python
def lookup(ip: str) -> str:
    return "item1"
```

## Multiplexer

The multiplexer does not decide allow or deny itself. It runs each named filter and returns the first deny.

Set `FILTERS` in the multiplexer to the installed filter name. Filters run from `FILTER_PATH` (default `/usr/local/sbin`).

```bash
FILTERS="your-filter"
FILTER_PATH="/usr/local/sbin"
```

Each filter is called as:

```bash
/usr/local/sbin/your-filter <client-ip> MUX
```

The second argument sets `MUX`, so `in_multiplexer` is true and `debug` prints as well as logging. A filter that is missing or not executable is skipped.

## TCP Wrapper Order

TCP Wrappers read `/etc/hosts.allow` first, then `/etc/hosts.deny`. Anything not handled in `hosts.allow` falls through to `hosts.deny`.

When the multiplexer is in front, `hosts.allow` calls the multiplexer, not this filter. Use the rules below only when this filter runs on its own.

### Hosts Allow

Pass every SSH client address to the filter. `aclexec` runs the script, and `%a` is the client address. Exit `0` allows the connection. Exit `1` denies it.

```text
sshd: ALL: aclexec /usr/local/sbin/your-filter %a
```

### Hosts Deny

Deny SSH when `hosts.allow` does not allow it:

```text
sshd: ALL
```

> **Note:**
> The deny rule should not be reached when the filter handles every address. Keep it as a fallback.

## Development

```bash
make init
make bash-check
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
