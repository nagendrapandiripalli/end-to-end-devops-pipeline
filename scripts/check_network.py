"""Validate explicit Terraform JSON network inputs without accessing AWS."""
import ipaddress
import json
import sys
from pathlib import Path

def validate(data):
    errors = []
    try:
        vpc = ipaddress.IPv4Network(data["vpc_cidr"], strict=True)
        azs = data["azs"]
        if not isinstance(azs, list) or not azs or any(not isinstance(a, str) or not a.strip() for a in azs):
            return ["azs must contain zone names"]
        if len(set(azs)) != len(azs):
            errors.append("Duplicate zones")
        networks = []
        for key in ["public_subnet_cidrs", "private_subnet_cidrs"]:
            cidrs = data[key]
            if not isinstance(cidrs, list) or not cidrs:
                errors.append("Subnet list must not be empty")
                continue
            if len(cidrs) > len(azs):
                errors.append("Subnet count exceeds zone count")
            for cidr in cidrs:
                net = ipaddress.IPv4Network(cidr, strict=True)
                if not net.subnet_of(vpc):
                    errors.append("Subnet outside VPC")
                if not 16 <= net.prefixlen <= 28:
                    errors.append("Invalid AWS IPv4 subnet prefix")
                if any(net.overlaps(other) for other in networks):
                    errors.append("Overlapping subnets")
                networks.append(net)
        if not 16 <= vpc.prefixlen <= 28:
            errors.append("Invalid AWS IPv4 VPC prefix")
    except (KeyError, ValueError, TypeError) as exc:
        errors.append(str(exc))
    return errors

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variables", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.variables.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print("\n".join(errors) if errors else "Network input checks passed")
    sys.exit(bool(errors))
