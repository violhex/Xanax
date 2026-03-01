# Security

## Reporting a vulnerability

Do not open a public GitHub issue for security vulnerabilities. Instead, use [GitHub Security Advisories](https://github.com/violhex/xanax/security/advisories/new) to report privately.

Include as much of the following as you can:

- A description of the vulnerability and its potential impact
- Steps to reproduce, or a minimal code example that demonstrates the issue
- The xanax version and Python version you were running
- Any relevant output or tracebacks

You'll receive a response within 7 days. If the issue is confirmed, a fix will be released as soon as possible and a public advisory will be published once it's out.

## Scope

xanax is a client library. The attack surface is narrow:

**In scope:**
- API key leakage through logging, repr output, or error messages
- Request forgery or parameter injection via user-supplied input
- Unsafe deserialization of API responses
- Dependency vulnerabilities that affect xanax users directly

**Out of scope:**
- Vulnerabilities in the Wallhaven API itself — report those to Wallhaven
- Issues that require a compromised Python environment or elevated system access
- Rate limit bypass or API abuse — the client enforces nothing the API doesn't

## API key handling

The client is designed so your API key stays private:

- Transmitted via the `X-API-Key` HTTP header, never in query parameters
- Not included in `repr()`, `str()`, or any log output
- Not stored anywhere beyond the client instance

```python
client = Xanax(api_key="my-secret-key")
print(client)  # Xanax(authenticated)  — key not visible
```

If you find a way to extract or expose a key through normal library usage, that is a vulnerability worth reporting.

## Supported versions

Security fixes are applied to the latest release only. If you're on an older version, upgrade to the latest before reporting.
