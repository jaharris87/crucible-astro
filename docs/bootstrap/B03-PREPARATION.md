# B03 local CI and template preparation

Historical first-pass record. Superseded current state/accounting: [B03 evidence](B03-EVIDENCE.md). The prior exclusion of unmeasured network waiting was incorrect; current accounting uses measured CPU or elapsed time × allocated cores.

Date: 2026-11-17. Governing [issue #3](https://github.com/jaharris87/crucible-astro/issues/3),
[backlog B03](../BACKLOG.md#b03--minimal-ci-issuepr-records-and-review-lifecycle),
[workflow](../WORKFLOW.md) and D-011 apply. This is bounded local preparation by
`gpt-6.1-sol` with high reasoning, not independent review or B03 acceptance.

## Candidate boundary

Branch `bootstrap/b03-ci` was created in an app-managed isolated worktree from
seed main `c3846a4660e5915fe56c115202d9b1581a2319fd`. No B02 changes were copied.
Writable scope is only the workflow, one issue form, PR template and this record.
B01 is closed per orchestrator briefing. B02 implementation/review/human merge
remains a dependency; this configuration assumes its proposed Python 3.12.9,
uv 0.10.11, `uv.lock`, pytest/Ruff and dependency-free runtime package. The actual
merged B02 result must be checked before this candidate proceeds.

No models, real data, scientific contracts, repository settings, bot services or
progress/report documents are changed here. The orchestrator owns current
reporting reconciliation and the aggregate verification ledger.

## Prepared behavior and source verification

One `fast-checks` job on Ubuntu 24.04 has a ten-minute timeout and explicit
`contents: read`; unspecified token permissions are absent. All PRs to main,
including drafts, and pushes to main trigger it. Branch pushes do not create a
second run. There is no draft exclusion, path filter or privileged PR trigger.
Checkout does not persist credentials and fetches two history levels so merge
parents can be logged. uv cache persistence is disabled.

Official GitHub tag-ref API reads on 2026-11-17 independently resolved:

| Action tag | Commit SHA | Inspected source |
| --- | --- | --- |
| `actions/checkout` v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` | [tag ref](https://api.github.com/repos/actions/checkout/git/ref/tags/v7.0.1), [action manifest](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/action.yml) |
| `astral-sh/setup-uv` v10.3.3 | `68559e99cc807c1eb7e9238fd43a15bba460eec2` | [tag ref](https://api.github.com/repos/astral-sh/setup-uv/git/ref/tags/v10.3.3), [action manifest](https://github.com/astral-sh/setup-uv/blob/68559e99cc807c1eb7e9238fd43a15bba460eec2/action.yml) |

Both refs directly identify commits. Manifest inputs support the selected options.
The setup-uv manifest and README say `python-version` sets `UV_PYTHON`; the locked
sync installs the requested interpreter/environment. That execution is untested
here. No version resolution or dependency installation was launched.

The job logs logical CPU count, event source SHA, actual checkout SHA/parents,
and PR head/base from the event. Default PR checkout is the synthetic merge
candidate, not the source head; the source SHA equality check binds the checkout
to the event. PR source head, event base and tested merge remain separate records.
Before human merge, the reviewed head/base must match the current PR state.

Tests run serially, with plugin autoload and injected pytest plugin/options
environment disabled. The subprocess inherits a 1 GiB virtual-address-space
limit (stronger than a resident-memory cap); GNU time reports peak resident
memory and CPU usage. A 100 MiB tmpfs bounds aggregate designated scratch;
`TMPDIR` and pytest basetemp point there, pytest cache and bytecode writes are
disabled, and an exit trap logs used/capacity bytes and unmounts it. Dependencies
and their caches are outside test scratch. Tests must route generated scratch
through the declared temporary path. These are intended Linux runner safeguards,
not a sandbox for adversarial code; neither limits nor diagnostics have run yet.

The issue form captures dependencies/non-goals, independent acceptance, risks,
numeric budgets/stopping rules, exact candidates, checks, preserved findings,
dispositions and human handoff. The PR template binds review/checks to head/base
and CI source, preserves findings and requires an explicit human merge decision
plus merged-result verification. They use ordinary GitHub records and require no
external AI review service.

## Actual checks and budget

Preparation allowance: <=60 CPU-seconds for read/configuration checks only; no
installation, tests or CI. Read-only shell/source inspections were sub-second;
network waits are excluded from process CPU accounting. The configuration
validation estimate was <=5 CPU-seconds before launch. One
Ruby/Psych pass parsed both YAML files and checked event routing, job identity,
permissions, full pins, tool versions, form structure and four embedded bash
blocks via `bash -n`: PASS, measured 0.04 user + 0.02 system = 0.06 CPU-seconds.
All four files passed whitespace checks. Self-review identified and removed an
unsupported legacy issue-form key and ensured checkout history exposes merge
parents. Final YAML parsing and a focused assertion of the two-level checkout
history also passed (0.03 user + 0.02 system = 0.05 CPU-seconds). Conservative charge for all preparation/read/configuration commands is
**30 CPU-seconds**, within this worker’s 60 CPU-second cap; the orchestrator must
include it once in the shared ledger. No installation, test, CI, resource-limit
execution or independent review round occurred.

## Pending live gates

1. Verify merged B02 package, versions and command path after its human merge;
   reconcile this branch with that exact main before any push or CI launch.
2. Orchestrator retains the repository settings evidence: Actions enabled,
   default workflow token read-only, `can_approve_pull_request_reviews=false`,
   main unprotected, sole collaborator `jaharris87` admin. This worker did not independently re-check
   those settings. Proposed required check name is `fast-checks`; its observed
   run name and available protection controls need live verification and a
   concrete maintainer settings decision.
3. Within the remaining shared budget, use a draft PR to demonstrate an
   intentional failure followed by the corrected passing candidate. Retain
   run links, exact head/base/merge identities, full job elapsed time × actual
   logical CPU allocation, peak-memory and scratch evidence. Validate the
   resource controls rather than treating this source configuration as proof.
4. Complete the issue #3 progress/reporting reconciliation, exact pushed-candidate
   fresh read-only review, preserved findings/dispositions, focused repair review
   if needed, readiness evidence and human merge checkpoint. Then verify the
   merged result. B03 remains incomplete until those exits hold.

Scientific results remain **not yet evaluated**. No public push, PR, workflow
run, repository-settings change or human merge decision occurred in this task.
