from __future__ import annotations

from typing import Optional, Literal

import dns.resolver

_resolver = dns.resolver.Resolver()
_resolver.nameservers = ["8.8.8.8", "1.1.1.1"]


def auth_proto_resolver(
        proto: Literal["DMARC1", "DKIM1", "spf1"],
        domain: str,
        selector: Optional[str] = None
) -> Optional[str]:
    if proto == "DKIM1" and selector is None:
        raise ValueError("DKIM1 selector must be specified")

    match proto:
        case "DMARC1":
            qname = f"_dmarc.{domain}"
        case "DKIM1":
            qname = f"{selector}._domainkey.{domain}"
        case "spf1":
            qname = domain
        case _ :
            raise Exception(f"Unknown protocol: {proto}")

    dns_record = _resolver.resolve(qname, 'TXT')

    for record in dns_record:
        if proto in str(record):
            return str(record)

    return None


if __name__ == "__main__":
    print(auth_proto_resolver("DKIM1", "google.com", "20230601"))