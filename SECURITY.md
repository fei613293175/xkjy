# Security Boundary

## Prohibited repository content

The following must never be committed, copied into artifacts, or logged:

- Payment, storage, identity, email, or database credentials.
- PEM private keys, client certificates, or provider certificate bundles.
- Private integration exports or the original private mother-template ZIP.
- Production user data, identity captures, payment screenshots, or R2 object URLs.

## Runtime configuration

Production and test credentials belong only on the connected server in a restricted secret directory or Secret manager. The repository may contain field names, contracts, and empty examples only.

When a server preflight detects a missing or invalid secret, record the exact capability as blocked without exposing its value. Do not replace a real integration with a fake success path.

## Incident response

The source development package contained non-empty integration configuration and PEM material. Treat any value distributed with that package as potentially exposed: restrict access, determine scope, and rotate every still-valid credential before production use.
