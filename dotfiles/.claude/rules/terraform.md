---
paths:
  - "**/*.tf"
  - "**/*.tftest.hcl"
---

# Terraform

When an older and a newer idiom both fit the module's `required_version` and provider constraint, pick the newer one: training data holds more old Terraform than new.

- Provider `default_tags` reach only resources Terraform creates. Give what a launcher creates later the tags and a `Name` through that launcher's own setting: a launch template's `tag_specifications` for instances, volumes and network interfaces, a CSI driver's volume tags, a controller's default tags.
- Keep secrets out of state: a provider-managed secret where the resource offers one, otherwise a write-only argument with its version argument, fed by an ephemeral resource or variable.

## Versions

- Write for the lowest `required_version` the module declares and for the CLI version CI pins, not the installed CLI. When a feature needs a newer floor, raise the floor in the same change.
- Pin versions to concrete values committed in code or tfvars: AMI releases, add-on and chart versions. A data source that resolves the current default, recommended or latest value (`aws_eks_addon_version`, an SSM AMI parameter, `aws_ami` with `most_recent`) changes the plan with no code change, and a value passed only at plan time is not pinned either.
- In a child module, constrain Terraform and each provider only by a minimum (`>= 6.63`); roots set `~>` and commit `.terraform.lock.hcl`. A `~>` in a child module caps every root that calls it.

## Tests

- Run `terraform test` only when the tests mock every provider that calls a remote API: an unmocked run plans or applies against the real account.
- In a mocked test, a value the mock generated proves nothing, and neither does an assert that recomputes the resource's own expression, such as comparing a policy with the same `file()` the resource reads. Assert on values the configuration computes from inputs, or pin the mocked value with an override and `override_during = plan`.
- Compare a `map(string)` attribute with `tomap({...})`: an object literal never equals a map.
- Test a validation or precondition with `expect_failures` under `command = plan`. A precondition on a value unknown at plan never fires there, so make the value known first with `override_during = plan`.

## Roots and modules

- A root is one state: its backend, providers, lookups and module calls. Put resources in child modules, one level deep, and pass each module the IDs it needs as input variables rather than looking them up inside it, so the root decides where each value comes from.
- Make a value that is the same in every deployment of a root a local. A variable whose validation accepts exactly one value only adds an input to set.
- Between roots, look resources up by name or tag, and read a value published for consumers (an SSM parameter) only for what has neither. Don't add a `terraform_remote_state` data source: it needs read access to the producer's whole state, secrets included.

## State and apply

- State is keyed by resource address, not module source. When you change a module's source or rename resources under an applied root, keep each address or add a `moved` block, and say which resources the plan replaces.
- A plan cannot show limits the service enforces at apply, such as EKS accepting new cluster subnets only in the AZs the cluster was created in. Before calling a change in-place, check the argument's `ForceNew` or `RequiresReplace` plan modifier in the provider source and the update rules in the service's API docs.
