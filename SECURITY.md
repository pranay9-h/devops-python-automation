# Security

## Never commit

- AWS access keys
- AWS secret access keys
- session tokens
- kubeconfig files
- private keys
- passwords
- API tokens
- production configuration containing secrets

## Authentication

Prefer:

- AWS IAM Identity Center
- assumed IAM roles
- temporary AWS credentials
- workload identity in CI/CD

For Kubernetes, use the least-privileged context required for the task.

## Destructive actions

Automation that can delete resources must be dry-run or read-only by default.

The EBS utility requires both:

```text
--delete --confirm
```

before it issues delete calls.

Always review discovered resources before enabling destructive behavior.
