# OpenClaw RLS Onboarding Wizard

Generate a reusable read-access onboarding package for an OpenClaw deployment.

The package maps verified Discord/OpenClaw sender IDs to people, departments, roles, and three data layers. It also creates positive and negative test checklists for launch, transfer, and offboarding.

## Important scope

This repository does **not** apply database row-level security and does not change Discord, Notion, Google Drive, or Google Sheets permissions.

It is a defense-in-depth decision layer for OpenClaw. Source databases and platform permissions remain authoritative; OpenClaw rules may restrict access further but must never expand it.

## Decision flow

```text
verified sender ID
  -> person
  -> department and role
  -> data layer
  -> source permission check
  -> allow the minimum necessary data, or deny
```

Display names, nicknames, email addresses, and plain-text mentions are not authorization evidence. Unknown, conflicting, revoked, and `pending_id` identities are denied governed internal data by default.

## Data layers

- `company_shared`: verified internal members and AI consultants
- `department_general`: members of that department; AI consultants only while assigned to that department
- `department_sensitive`: executive owner, that department's lead, or an active, precisely scoped, time-bounded grant approved by one of those roles

## Install

```bash
git clone https://github.com/JasperYang0609/rls-onboarding-wizard.git \
  ~/.openclaw/workspace/skills/rls-onboarding-wizard
openclaw skills check
```

## Generate a starter package

```bash
python3 ~/.openclaw/workspace/skills/rls-onboarding-wizard/scripts/generate_package.py \
  --client-name "Example Company" \
  --client-slug "example-company" \
  --industry "professional-services"
```

The default output is `records/<client-slug>/` and contains:

- `rls_matrix.yaml`
- `AGENTS_rls_addendum.md`
- `onsite_rls_checklist.md`
- `rls_test_cases.md`
- `manual_platform_permissions.md`

The generator rejects unsafe slugs, Unicode line/control injection, symlinked output paths, and every existing output directory. It writes through a verified directory handle. To update a package, generate into a new directory, review the diff, and preserve the previous version.

## Onboarding gate

Do not mark an installation ready until:

- every person has verified numeric IDs or remains `pending_id`
- every data source is assigned to one of the three layers
- department and role mappings are complete
- wrong-role, cross-department, revoked-ID, pending-ID, revoked/future/expired/wrong-approver/broad-grant, and source-denial tests pass
- source-system permissions have been checked separately

See [SKILL.md](SKILL.md), [the baseline](references/baseline.md), and [the wizard questions](references/wizard-questions.md) for the complete workflow.

## Test

```bash
python3 -m unittest discover -s tests -v
```

All tests use synthetic identities and temporary directories. Do not commit customer names, IDs, permission matrices, or generated client packages to this public repository.
