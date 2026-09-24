import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_template.py <compiled-template.json>")
        return 2

    template_path = Path(sys.argv[1])

    if not template_path.is_file():
        print(f"ERROR: Template not found: {template_path}")
        return 2

    with template_path.open(encoding="utf-8-sig") as template_file:
        template = json.load(template_file)

    storage_account = next(
        (
            resource
            for resource in template.get("resources", [])
            if resource.get("type") == "Microsoft.Storage/storageAccounts"
        ),
        None,
    )

    if storage_account is None:
        print("ERROR: No Microsoft.Storage/storageAccounts resource found")
        return 2

    properties = storage_account.get("properties", {})
    network_acls = properties.get("networkAcls", {})
    sku = storage_account.get("sku", {})

    checks = [
        (
            "Storage API version",
            storage_account.get("apiVersion"),
            "2025-08-01",
        ),
        (
            "Storage account kind",
            storage_account.get("kind"),
            "StorageV2",
        ),
        (
            "Storage redundancy",
            sku.get("name"),
            "Standard_LRS",
        ),
        (
            "Minimum TLS version",
            properties.get("minimumTlsVersion"),
            "TLS1_2",
        ),
        (
            "HTTPS-only traffic",
            properties.get("supportsHttpsTrafficOnly"),
            True,
        ),
        (
            "Anonymous blob access",
            properties.get("allowBlobPublicAccess"),
            False,
        ),
        (
            "Shared-key authorization",
            properties.get("allowSharedKeyAccess"),
            False,
        ),
        (
            "Default OAuth authentication",
            properties.get("defaultToOAuthAuthentication"),
            True,
        ),
        (
            "Public network endpoint",
            properties.get("publicNetworkAccess"),
            "Enabled",
        ),
        (
            "Firewall bypass",
            network_acls.get("bypass"),
            "None",
        ),
        (
            "Default network action",
            network_acls.get("defaultAction"),
            "Deny",
        ),
    ]

    failed_checks = 0

    for name, actual, expected in checks:
        if actual == expected:
            print(f"PASS: {name} = {actual!r}")
        else:
            failed_checks += 1
            print(
                f"FAIL: {name} expected {expected!r}, "
                f"found {actual!r}"
            )

    print()
    print(f"Checks passed: {len(checks) - failed_checks}")
    print(f"Checks failed: {failed_checks}")

    return 1 if failed_checks else 0


if __name__ == "__main__":
    sys.exit(main())