# B03 local candidate evidence

Date: 2026-11-17; [issue #3](https://github.com/jaharris87/crucible-astro/issues/3),
[D-012 addition](https://github.com/jaharris87/crucible-astro/issues/3#issuecomment-6959269014),
[workflow](../WORKFLOW.md). Author: explicit `gpt-6.1-sol` High; self-review only.

## Exact base and scope

`bootstrap/b03-ci` was rebased from seed-based preparation onto verified B02 main
`5d81381ddfde28cb6f86980e616d7c5065bae768`, human-merged PR #5. This worktree is
isolated; the root checkout was read-only to this worker. The final local head is
reported at commit handoff; a future PR must record full head/base and tested merge
identities. B03 PR: **None**; no push/CI/settings/merge in this pass.

Files: workflow, one issue form, PR template; AGENTS, WORKFLOW, AGENT_BRIEFS,
DECISIONS, HANDOFF, PROGRESS, README, CONTRIBUTING, initial status report,
VERIFICATION, this evidence and annotated historical preparation record. Executed
PHASE_0B_LAUNCH, REVIEW, TRANSITION and archive are preserved exactly. No package,
lock, software test, data, scientific contract, global settings or agent tooling
changes. B01/B02 complete; B03 active local candidate; B04 not implemented.

## Configuration and policy

[Initial preparation](B03-PREPARATION.md) retains verified full action pins and
manifest sources. CI now uses `uv sync --locked --no-editable`, exercising both
installed-distribution tests without the editable license-inventory skip. One
`fast-checks` job, PRs to main including drafts, main pushes, read-only contents,
no persisted checkout credentials, timeout ten minutes, serial tests and disabled
pytest plugin autoload remain. It logs actual CPU allocation, PR head/base,
event source/checkout/merge parents, GNU time peak RSS/CPU and scratch use/capacity.
A 1 GiB address-space limit and 100 MiB designated scratch tmpfs are configured,
not yet executed or verified on Linux. Software tests must use TMPDIR/pytest
scratch; dependency environments/caches are outside the scratch budget.

D-012 implements all eight accepted points in canonical [Model selection and
escalation](../WORKFLOW.md#model-selection-and-escalation), with AGENTS summary,
brief fields, accepted decision and next-orchestrator handoff. Effective **after
Phase 0B**, without changing current assignments. Future routine Astra defaults
are superseded; historical executed assignments remain accurate. Fresh Sol High
review of the final pushed policy/code candidate is still required.

The planned single-maintainer protections are [explicit proposals](../WORKFLOW.md#planned-bootstrap-protection),
including actual observed named check, strict freshness, PR requirement,
stale-review dismissal, conversations resolved, force/deletion blocks and no
auto-merge. Zero separate required approvals may address the sole-human limit;
an explicit human merge decision remains mandatory. Lead settings facts are
attributed in HANDOFF; this worker did not configure or independently verify them.

## Actual verification and budget

Reserve <=120 CPU-seconds for this pass; prior charge is 1,110/7,200, including
the earlier 30-second B03 preparation, 10-second lead control readback and final
60-second B02 integration reconciliation (provisional 40 is historical). Lead
settings/identity/source checks reserve 120 separately; future CI reserves
2,400 per job before reconciliation to full elapsed × reported logical CPUs. No package installation,
software tests, resource-control execution or CI was authorized in this pass.
Actual checks: YAML/structural assertions (event/job/permissions/full pins/tool
versions/noneditable command/form), four `bash -n` blocks: PASS, 0.04 user +
0.02 system = **0.06 CPU-s**. Python scope/base/local-link/heading/policy/history/
whitespace checks: PASS, 0.05 user + 0.05 system = **0.10 CPU-s**; **15 scoped
files, 102 local links, 28 anchors, eight policy points**, three explicitly
protected historical documents plus unchanged scope outside the allowlist.
Manual active-guidance scan and complete diff self-review found no contradictory
routine Astra default; supersession and historical descriptions remain explicit.
A planned-protection wording correction applies the accepted sole-maintainer
provision without introducing a new per-choice approval gate or weakening
stronger controls. No independent review was performed.

**40 CPU-seconds charged**, releasing 80 of this worker’s 120 reservation. This
includes measured checks/edits and conservative source/network/commit overhead;
unmeasured initial inspection/network elapsed uses the 16-logical-CPU fallback
(overall <=2.4 s envelope plus measured commands, rounded to 40). Phase total is
**1,150 charged + 120 separately reserved for lead = 1,270/7,200**. No network-wait
exclusion is used. Final record-only accounting edits receive whitespace/scope
inspection; software reruns are unnecessary because executable inputs did not
change after the successful configuration syntax checks.

## Remaining acceptance

Lead owns the pushed draft, intentional failing then corrected passing CI,
actual run/resource/permissions evidence and settings decision/effective checks.
Fresh read-only exact pushed-candidate Sol High review must cover policy and
workflow; preserve findings/dispositions and focused verification if needed.
Then readiness, explicit human merge and merged-result checks remain. Do not
claim B03/Phase 0B completion before these exits. Scientific results remain
**not yet evaluated**. No model substitution or Astra invocation in this pass.
