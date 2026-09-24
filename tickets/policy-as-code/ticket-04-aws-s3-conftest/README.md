# Daily Ticket 04: AWS S3 Policy as Code with Conftest

## Status

Complete and locally validated.

## Focus

- AWS S3 security requirements
- Terraform plan analysis
- Conftest
- Open Policy Agent Rego
- Policy-as-code deployment guardrails
- CI/CD-compatible exit codes

## Workplace Scenario

A Terraform pull request proposes an Amazon S3 bucket for sensitive portfolio
artifacts. Before approving the change, the platform engineering team needs an
automated policy gate that evaluates the proposed Terraform plan.

The guardrail must reject the plan when:

- Any S3 public-access protection is not enabled.
- S3 server-side encryption does not use AWS KMS.

This ticket evaluates representative Terraform plan JSON locally. It does not
connect to AWS, deploy resources, or require cloud credentials.

## Learning Objective

Translate cloud security requirements into executable Rego policies that can
automatically approve or reject infrastructure changes before deployment.

## Architecture and Approach

The solution uses Conftest to load Terraform plan JSON and evaluate it against
an Open Policy Agent Rego policy.

The validation flow is:

1. Read the proposed Terraform resource changes.
2. Identify S3 public-access-block resources.
3. Confirm all four public-access protections are enabled.
4. Identify S3 encryption-configuration resources.
5. Confirm the encryption algorithm is `aws:kms`.
6. Return a nonzero exit code when violations are found.
7. Return exit code `0` when all evaluated requirements pass.

## Deliverables

| File | Purpose |
|---|---|
| [`policy/s3.rego`](policy/s3.rego) | Defines the executable S3 security requirements |
| [`testdata/noncompliant-plan.json`](testdata/noncompliant-plan.json) | Contains two intentional security violations |
| [`testdata/compliant-plan.json`](testdata/compliant-plan.json) | Contains the remediated configuration |
| [`evidence/conftest-version.txt`](evidence/conftest-version.txt) | Records the pinned Conftest and OPA versions |
| [`evidence/noncompliant-test.txt`](evidence/noncompliant-test.txt) | Proves the insecure plan was rejected |
| [`evidence/compliant-test.txt`](evidence/compliant-test.txt) | Proves the remediated plan passed |


## Requirements Enforced

### S3 Public-Access Protection

The policy requires all these properties to equal `true`:

- `block_public_acls`
- `block_public_policy`
- `ignore_public_acls`
- `restrict_public_buckets`

### S3 Encryption

The policy requires the server-side encryption algorithm to equal:

`aws:kms`

## Validation Results

### Noncompliant Fixture

The policy detected:

- `block_public_acls` set to `false`
- `sse_algorithm` set to `AES256`

Result:

- Tests passed: `0`
- Tests failed: `2`
- Exit code: `1`

### Compliant Fixture

The remediated fixture uses:

- All four public-access protections set to `true`
- `sse_algorithm` set to `aws:kms`

Result:

- Tests passed: `2`
- Tests failed: `0`
- Exit code: `0`

## Security and Governance Relevance

This implementation converts written security requirements into preventive,
repeatable, and reviewable technical controls. The policy produces
machine-readable enforcement results while the stored evidence provides an
audit trail showing both negative and positive testing.

The policy supplements engineering review; it does not replace AWS
organization-level controls, IAM permissions, AWS Config, Security Hub, or
runtime monitoring.

## Architecture Tradeoff

Predeployment policy enforcement prevents known misconfigurations from reaching
AWS, but the policy can evaluate only the conditions explicitly encoded in
Rego. Expanding coverage improves assurance while increasing policy
maintenance, testing, and exception-management requirements.

## Business Value

Automated policy evaluation reduces manual review effort, identifies security
problems earlier in the delivery lifecycle, standardizes infrastructure
requirements, and helps prevent avoidable cloud exposure.

## Career Connection

This ticket demonstrates how Cloud Engineers implement automated deployment
guardrails and how Cloud Architects translate security requirements into
reusable platform controls.

## Cost and Safety

The exercise runs locally through Docker and creates no AWS resources. No AWS
credentials, account identifiers, secrets, or customer data are stored in the
repository.