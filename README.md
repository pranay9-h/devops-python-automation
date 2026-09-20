# DevOps Python Automation

Production-style Python automation portfolio for common AWS, Kubernetes, and operational troubleshooting tasks.

The project emphasizes **safe defaults, clear CLI behavior, testability, and interview-friendly code** rather than one-off scripts.

## What this demonstrates

- AWS automation with boto3
- Kubernetes API automation with the official Python client
- dry-run-first resource cleanup
- EC2 inventory and reporting
- unattached EBS detection
- S3 security posture checks
- Kubernetes pod-health diagnostics
- application log analysis
- unit testing with pytest
- linting with Ruff
- CI validation with GitHub Actions

## Repository structure

```text
.
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── config/
│   └── config.example.yaml
├── src/
│   ├── aws/
│   │   ├── ec2_inventory.py
│   │   ├── s3_audit.py
│   │   └── unused_ebs.py
│   ├── kubernetes/
│   │   ├── failed_pods.py
│   │   └── pod_health.py
│   └── logs/
│       └── error_parser.py
├── tests/
│   ├── test_error_parser.py
│   └── test_pod_health.py
├── .gitignore
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── SECURITY.md
```

## Setup

Create a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## AWS authentication

Do not hard-code credentials.

Prefer short-lived credentials through IAM Identity Center or an assumed role.

Verify identity:

```bash
aws sts get-caller-identity
```

## EC2 inventory

List instances:

```bash
PYTHONPATH=src python src/aws/ec2_inventory.py --region ap-south-1
```

JSON output:

```bash
PYTHONPATH=src python src/aws/ec2_inventory.py --format json
```

CSV output:

```bash
PYTHONPATH=src python src/aws/ec2_inventory.py --format csv
```

The utility reports:

- instance ID
- Name tag
- state
- instance type
- Availability Zone
- launch time

## Unattached EBS detection

Read-only discovery:

```bash
PYTHONPATH=src python src/aws/unused_ebs.py --region ap-south-1
```

By default the script never deletes anything.

Deletion requires both explicit flags:

```bash
PYTHONPATH=src python src/aws/unused_ebs.py --delete --confirm
```

This double opt-in is intentional to reduce accidental destructive actions.

## S3 audit

Run:

```bash
PYTHONPATH=src python src/aws/s3_audit.py
```

The script reports whether each visible bucket has:

- server-side encryption configuration
- S3 Public Access Block fully enabled

This is a lightweight audit, not a complete cloud-security assessment.

## Kubernetes pod health

Use your current kubeconfig:

```bash
PYTHONPATH=src python src/kubernetes/pod_health.py
```

Limit to a namespace:

```bash
PYTHONPATH=src python src/kubernetes/pod_health.py --namespace default
```

The utility flags:

- Pending pods
- Failed pods
- Unknown pods
- CrashLoopBackOff
- restart counts over a configurable threshold

Example:

```bash
PYTHONPATH=src python src/kubernetes/pod_health.py --restart-threshold 3
```

## Failed pod report

```bash
PYTHONPATH=src python src/kubernetes/failed_pods.py
```

This gives a minimal report for pods whose phase is `Failed`.

## Log analysis

Analyze a local application log:

```bash
PYTHONPATH=src python src/logs/error_parser.py application.log
```

JSON output:

```bash
PYTHONPATH=src python src/logs/error_parser.py application.log --format json
```

Signals counted:

- ERROR
- WARN / WARNING
- timeout
- HTTP 500

## Tests

Run:

```bash
pytest -q
```

## Linting

Run:

```bash
ruff check src tests
```

## CI

Pull requests and pushes to `master` run:

1. dependency installation
2. Ruff linting
3. pytest

The CI workflow does not use AWS or Kubernetes credentials.

## Safety principles

This repository intentionally follows several operational safety rules:

- read-only behavior by default
- destructive actions require explicit confirmation
- credentials are external to source control
- scripts return clear output
- automation logic is unit-testable
- cloud and cluster access is never required for CI tests

See [SECURITY.md](SECURITY.md).

## Suggested production improvements

For a real internal automation toolkit, I would additionally consider:

- structured logging
- shared CLI framework such as Typer
- retry/backoff for cloud API throttling
- centralized configuration loading
- role-based authorization checks
- Prometheus metrics or OpenTelemetry instrumentation
- packaging and internal artifact publishing
- broader mocking of AWS/Kubernetes API calls
- approval workflow for destructive operations

## Interview discussion points

Be prepared to explain:

- why destructive automation should be dry-run-first
- how boto3 obtains credentials
- paginator use for AWS APIs
- difference between Kubernetes pod phase and container waiting reason
- why CrashLoopBackOff may not appear as the pod phase
- how you would test AWS automation without touching real AWS
- why CI here avoids cloud credentials
- when JSON/CSV output is more useful than console text
- how you would harden this toolkit for production use

## Author

Pranay Saiteja Soppadandi  
GitHub: https://github.com/pranay9-h
