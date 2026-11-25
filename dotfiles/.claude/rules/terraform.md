---
paths:
  - "**/*.tf"
  - "**/*.tftest.hcl"
---

# Terraform

When an older and a newer idiom both fit the module's `required_version` and provider constraint, pick the newer one: training data holds more old Terraform than new.

- Write for the lowest `required_version` the module declares and for the CLI version CI pins, not the installed CLI. When a feature needs a newer floor, raise the floor in the same change.
- Pin versions to concrete values committed in code or tfvars: AMI releases, add-on and chart versions. A data source that resolves the current default, recommended or latest value (`aws_eks_addon_version`, an SSM AMI parameter, `aws_ami` with `most_recent`) changes the plan with no code change, and a value passed only at plan time is not pinned either.
- Provider `default_tags` reach only resources Terraform creates. Give what a launcher creates later the tags and a `Name` through that launcher's own setting: a launch template's `tag_specifications` for instances, volumes and network interfaces, a CSI driver's volume tags, a controller's default tags.
- Keep secrets out of state: a provider-managed secret where the resource offers one, otherwise a write-only argument with its version argument, fed by an ephemeral resource or variable.
- Run `terraform test` only when the tests mock every provider: an unmocked run plans or applies against the real account.
- In a mocked test, a value the mock generated proves nothing, and neither does an assert that recomputes the resource's own expression, such as comparing a policy with the same `file()` the resource reads. Assert on values the configuration computes from inputs, or pin the mocked value with an override and `override_during = plan`. Compare a `map(string)` attribute with `tomap({...})`: an object literal never equals a map. Test a validation or precondition with `expect_failures` under `command = plan`.
- Say what a mocked test cannot show (whether AWS accepts the configuration, permissions, quotas) when reporting that tests pass.
