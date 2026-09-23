# Daily Ticket 01: AWS Subnet Planning with Terraform

## Objective

Calculate four non-overlapping `/24` subnet CIDR blocks from the AWS VPC
address range `10.42.0.0/16` using Terraform.

## Workplace Scenario

A cloud engineering team needs a network foundation for an application running
across two AWS Availability Zones. Each Availability Zone requires a public
subnet for internet-facing services and a private subnet for application
workloads.

The addressing plan must be repeatable and reviewable before infrastructure is
deployed.

## Acceptance Criteria

- Two public subnet CIDRs
- Two private subnet CIDRs
- `/24` prefix for every subnet
- No overlapping ranges
- Descriptive subnet names
- Successful Terraform formatting and validation
- Expected subnet values displayed in the Terraform plan
- No cloud resources created

## Architecture and Approach

The parent VPC uses a `/16` network. The required subnets use `/24`, so
Terraform must add eight network bits:

```text
24 - 16 = 8

```

The configuration assigns a unique number to each subnet and uses
`cidrsubnet()` inside a Terraform `for` expression.

| Subnet | Number | Calculated CIDR |
|---|---:|---|
| `public_az1` | 0 | `10.42.0.0/24` |
| `public_az2` | 1 | `10.42.1.0/24` |
| `private_az1` | 10 | `10.42.10.0/24` |
| `private_az2` | 11 | `10.42.11.0/24` |

The unused subnet numbers between the public and private ranges reserve space
for future network tiers.

## Implementation

The [`main.tf`](main.tf) configuration contains:

- A validated `vpc_cidr` variable
- A map of logical subnet names and numbers
- A `for` expression that calls `cidrsubnet()`
- An output containing the calculated subnet map

This ticket performs local Terraform calculations. It does not configure an AWS
provider or create cloud resources.

## Prerequisites

- Terraform 1.5 or later
- Git
- Git Bash
- Visual Studio Code or another editor

## Validation

Run these commands from the repository root:

```bash
TICKET_DIR="tickets/terraform/ticket-01-aws-subnet-planning"

terraform -chdir="$TICKET_DIR" fmt -check
terraform -chdir="$TICKET_DIR" init -backend=false
terraform -chdir="$TICKET_DIR" validate
terraform -chdir="$TICKET_DIR" plan -input=false -no-color
```

Terraform validation passed, and the plan returned:

```text
private_az1 = 10.42.10.0/24
private_az2 = 10.42.11.0/24
public_az1  = 10.42.0.0/24
public_az2  = 10.42.1.0/24
```

Validation evidence:

- [`terraform-validation.txt`](evidence/terraform-validation.txt)
- [`terraform-plan.txt`](evidence/terraform-plan.txt)

## Security and Governance Considerations

Generating CIDRs through version-controlled infrastructure code reduces manual
addressing errors and records network-segmentation decisions for review.

Public and private names describe the intended subnet roles, but names do not
enforce security. Route tables, security groups, network ACLs, and workload
placement must enforce the final boundaries.

No credentials, Terraform state, or cloud account information are required for
this ticket.

## Troubleshooting

### Terraform has not been initialized

Run:

```bash
terraform -chdir="$TICKET_DIR" init -backend=false
```

### The calculated prefix is incorrect

Confirm that `newbits` is the difference between `/24` and `/16:

```text
24 - 16 = 8
```

### Formatting validation fails

Run:

```bash
terraform -chdir="$TICKET_DIR" fmt
terraform -chdir="$TICKET_DIR" fmt -check
```

### A subnet has an unexpected address

Confirm that each entry in `subnet_numbers` uses a unique integer.

## Architecture Tradeoff

Reserving address space between public and private subnet ranges supports future
growth and makes the network plan easier to understand. The tradeoff is that
some address space may remain unused.

A `/24` contains 256 addresses. AWS reserves five addresses in each subnet,
leaving 251 usable addresses. Production subnet sizes should therefore reflect
expected workload growth.

## Business Value

Automated subnet calculation reduces configuration mistakes, improves change
review, and creates a reusable network foundation for multi-Availability Zone
architectures.

## Career Connection

This ticket demonstrates the networking and infrastructure-as-code skills
expected from Cloud Engineers and introduces the capacity-planning decisions
expected from Cloud Architects.