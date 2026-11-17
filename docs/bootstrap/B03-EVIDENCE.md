# B03 local candidate evidence

Date: 2026-11-17; [issue #3](https://github.com/jaharris87/crucible-astro/issues/3),
[D-012 addition](https://github.com/jaharris87/crucible-astro/issues/3#issuecomment-6959269014),
[workflow](../WORKFLOW.md). Author: explicit `gpt-6.1-sol` High; self-review only.

## Exact base and scope

`bootstrap/b03-ci` was rebased from seed-based preparation onto verified B02 main
`5d81381ddfde28cb6f86980e616d7c5065bae768`, human-merged PR #5. This worktree is
isolated; the root checkout was read-only to this worker. The final local head is
reported at commit handoff; a future PR must record full head/base and tested merge
identities. Initial worker preparation had no PR/CI/settings change. Lead continuation is now [draft PR #6](https://github.com/jaharris87/crucible-astro/pull/6); the live record below supersedes pending items in the historical local preparation.

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
verified in the live Linux draft demonstration below. Software tests must use TMPDIR/pytest
scratch; dependency environments/caches are outside the scratch budget.

D-012 implements all eight accepted points in canonical [Model selection and
escalation](../WORKFLOW.md#model-selection-and-escalation), with AGENTS summary,
brief fields, accepted decision and next-orchestrator handoff. Effective **after
Phase 0B**, without changing current assignments. Future routine Astra defaults
are superseded; historical executed assignments remain accurate. Fresh Sol High
review of the final pushed policy/code candidate is still required.

The single-maintainer protections are [recorded controls](../WORKFLOW.md#bootstrap-protection),
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

## Live draft CI and protection evidence

On 2026-11-17, draft PR #6 head `7c90e2f1d562bd64f6290a800e33b2519d4131a4` against base `5d81381ddfde28cb6f86980e616d7c5065bae768` triggered [run 44166765762](https://github.com/jaharris87/crucible-astro/actions/runs/44166765762), event `pull_request`, while still draft. `fast-checks` tested synthetic merge `25d196841a7e965bd75b7632c4746877101cf670`; logged parents are that exact base and head. Checkout, interpreter/setup, locked noneditable installation and lint/format passed. Pytest failed only for `tests/test_ci_control.py::test_ci_detects_controlled_failure`, with `AssertionError: B03 controlled CI failure`; **1 failed, 2 passed**, exit 1. The final candidate removes this temporary probe; no final-pass claim is made from the intentional failure. Subsequent passing status and exact head/base/merge are retained in the PR discussion/checks before independent review/readiness.

Effective token permissions in the job log were **Contents: read; Metadata: read**. Runner reported **4 logical CPUs**. Full job 20:12:12–20:12:23 UTC = **11 seconds × 4 = 44 CPU-seconds**, replacing the 2,400 reservation. Test command measured 0.76 user + 0.05 system seconds, peak RSS **40,980 KiB** (41,963,520 bytes). The inherited 1 GiB address-space setting succeeded; mounted scratch capacity was **104,857,600 bytes**, `du` reported **84 bytes**. This is engineering evidence only.

Before settings mutation, main protection returned 404 (unprotected). The first PUT supplied both legacy `contexts` and `checks` and was rejected with HTTP 422; no protection was created. Retrying with only app-bound `checks` succeeded, followed by independent GET readback:

- required check `fast-checks`, app ID **15368** (`github-actions`), `strict: true`;
- `enforce_admins: true`; `dismiss_stale_reviews: true`;
- `required_approving_review_count: 0`, `require_last_push_approval: false`, `require_code_owner_reviews: false` for the single human maintainer;
- conversation resolution required, force pushes and deletion disabled.

Repository defaults are read-only workflow permissions, no workflow PR approval permission, and auto-merge disabled. No stronger prior controls were overwritten. Zero GitHub approvals do not replace the explicit human merge checkpoint or independent agent evidence. No unmet check may be bypassed.

The CLI's initial run-log fetch tried its default cache outside the sandbox and failed; rerunning with a task-local `XDG_CACHE_HOME` succeeded without global configuration changes. Raw CI/protection receipts are retained in the original checkout's ignored `.local/b03/`. Full job/run links preserve public evidence. Lead inspected the complete diff and exact policy against the maintainer's eight points; clarified “existing investigation or Sol analysis” and explicitly avoided repeated investigations/unnecessary context before the first live run. Model policy review remains pending a fresh Sol High reviewer.

## Corrected passing candidate and final receipt

[Run 44167409103](https://github.com/jaharris87/crucible-astro/actions/runs/44167409103) passed while PR #6 remained draft. Head `d17825b1223a35d34fd6f04d65d260c4cc661adf`, base `5d81381ddfde28cb6f86980e616d7c5065bae768`, tested synthetic merge `306b8aaf6304be1e08f624d6a87a0eb432ba6a40` with those exact parents. Locked noneditable installation, lint/format and **2 tests passed without skips**, exit 0. Full job 20:15:44–20:16:02 UTC = **18 seconds × 4 CPUs = 72 CPU-seconds**; peak test RSS **41,052 KiB**. This establishes the controlled failure→corrected pass demonstration.

After that pass, only README/progress/report/handoff/evidence/accounting receipts change. Workflow, templates, policy, package, lock and tests remain byte-identical to the passed candidate. Link/anchor, historical-preservation, scope and active-policy consistency checks cover these receipts; no extra local software suite is repeated. The ordinary required PR workflow still runs on the new receipt head. Its exact run/outcome and the final fresh review are recorded in the PR discussion; no human readiness occurs unless that exact check passes.

Lead charges its full 120 CPU-second inspection/settings/receipt allowance conservatively, including measured CLI CPU, bounded unmeasured edit/push overhead and final checkpoint accounting. Total charged now **1,386/7,200**. Reserve 2,400 for the final receipt CI before pushing and 120 for the fresh Sol High reviewer. The initial independent B03 round has not yet been consumed.
