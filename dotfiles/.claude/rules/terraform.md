---
paths:
  - "**/*.tf"
  - "**/*.tftest.hcl"
---

# Terraform

When an older and a newer idiom both fit the module's `required_version` and provider constraint, pick the newer one: training data holds more old Terraform than new.

- Write for the lowest `required_version` the module declares and for the CLI version CI pins, not the installed CLI. When a feature needs a newer floor, raise the floor in the same change.
- Run `terraform test` only when the tests mock every provider: an unmocked run plans or applies against the real account.
- Keep secrets out of state: a provider-managed secret where the resource offers one, otherwise a write-only argument with its version argument, fed by an ephemeral resource or variable.
- In a mocked test, a value the mock generated proves nothing. Assert on values the configuration computes from inputs, or pin the mocked value with an override and `override_during = plan`. Test a validation or precondition with `expect_failures` under `command = plan`.
- Say what a mocked test cannot show (whether AWS accepts the configuration, permissions, quotas) when reporting that tests pass.
