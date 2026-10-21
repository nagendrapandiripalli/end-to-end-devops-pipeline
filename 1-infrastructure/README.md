# Offline network preflight

Copy network.tfvars.json.example to a local network.tfvars.json and edit it.
From the repository root run:

    python scripts/check_network.py 1-infrastructure/network.tfvars.json

Use the same file with Terraform -var-file when planning. The committed example
can also be checked directly. All network inputs must be explicit; the checker
does not parse HCL defaults. It rejects overlaps, subnets outside the VPC,
invalid IPv4 prefixes and subnet counts exceeding the available zone entries.

No cloud connection or deployment is performed. Zone existence and region
membership are not checked. Terraform validation and an authenticated plan are
still needed. This example provides public routing but no NAT gateway or
explicit private route table; it does not provide private subnet internet egress.

Run tests with: python -m unittest discover -s tests -v
The existing GitHub Actions job discovers these tests automatically.
