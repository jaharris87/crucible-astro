# Phase 0B launch prompt

Prepared during the maintainer-directed transition, 2026-11-17. **Invoked by the maintainer on 2026-11-17; execution active and incomplete.** The original uninvoked version is preserved locally. It authorizes the bounded Phase 0B work described, with publication-readiness and human merge checkpoints; saving this file alone grants no authority.

```text
Execute CRUCIBLE Phase 0B: repository and development-workflow bootstrap only.

Read root AGENTS.md, README.md, docs/HANDOFF.md, DECISIONS.md, WORKFLOW.md,
BACKLOG.md B01–B04 and the Phase 0B exit in ROADMAP.md. Use the selected
CRUCIBLE workspace; inspect its current state before modifying it. Preserve
unrelated work and the historical Phase 0A review/archive/inventories.

At the start, create and confirm an active native Codex persistent goal:
“Complete CRUCIBLE Phase 0B B01–B04: establish the authorized public
jaharris87/crucible-astro repository and minimal reproducible development
workflow; take the synthetic species-order manifest validator through a
governing issue, implementation/checks, self-review, exact-candidate
independent PR review, findings disposition, human merge decision, merged
integration checks and documented closeout.”
If native Goals are unavailable, say so and maintain the same scope/status in
docs/HANDOFF.md. Do not mark complete merely because a budget is exhausted or
a human decision is pending. This goal excludes Phase 1 and scientific models.

Accepted decisions; do not ask again:
- GitHub owner jaharris87; repository crucible-astro; public; BSD-3-Clause.
- D-010 adopts the prepared workflow and B01–B04, with draft PR candidates,
  explicit fresh-context independent review, simple main, and human merge.
- D-011 adopts the verification/review limits below.
- D-002 chooses CCSN particle trajectories first. D-003 explores both target
  kinds, starting with qualified instantaneous RHS. Neither these nor later
  scientific decisions are prerequisites for B04's synthetic fixtures.

Publication prerequisite:
UT-Battelle, LLC is the proposed copyright holder, not yet confirmed wording.
Prepare the public seed and record the proposed LICENSE/notice content.
Before publishing project content, confirm with the maintainer any still-
missing institutional copyright/year/notices and applicable release readiness
under D-001. Use existing recorded confirmation if already supplied. Explain
exactly what remains missing and cite docs/TRANSITION.md; do not re-ask the
settled public/owner/license choices. Continue independent local preparation
while waiting; do not silently create a private repo or publish unconfirmed
material. No institutional submissions or messages to third parties are
included in this authority.

Git/GitHub and local implementation authority for THIS task:
You may initialize Git in this project, create the public
jaharris87/crucible-astro repository if it does not exist, configure its remote,
create bounded B01–B04 issues, feature branches/isolated worktrees, commits,
pushes, draft PRs, PR evidence/review/disposition comments, and mark candidates
ready for human review after their gates pass. You may install the minimal
project-local development dependencies, create packaging/test/CI files,
implement the synthetic validator, and run checks within the budget.
Inspect any existing repository before reuse; do not overwrite unrelated
content, replace existing history, delete repositories or force-push shared
branches. No global agent infrastructure/configuration changes.

B01 one-time initialization exception: after publication readiness is recorded,
you may make and push the minimum seed commit on main needed to establish a
base before PRs exist. Record this explicitly in the bootstrap issue/handoff;
this prompt authorizes that bounded seed action, not bypass of later PRs.
Use an explicit public-content allowlist: portable docs, appropriate license
and minimal repository metadata. Keep machine-local reference-path inventories,
historical local archives, reference code/data/PDFs, credentials and unrelated
files out of the public seed; retain local provenance in an ignored local-only
area and record any relocations. Produce portable citation notes and working
links. Do not claim the old Phase 0A review covers later adoption or code.

Execute B01–B04 as recorded in BACKLOG.md:
B01: verify destination and publication readiness, establish repository/base,
     carry adopted guidance forward and record bootstrap provenance.
B02: minimal Python package and one repeatable environment/check path;
     imports have no data access, training or output side effects.
B03: compact issue/PR templates; fast CI that actually runs on draft PRs;
     minimal workflow permissions; available agreed branch protections and
     exact named required checks. Establish the lightweight progress view with
     phases, issue/milestone links, dependencies, status and linked PRs. Adopt
     the prepared meeting-report template and initial bootstrap status report,
     update them to actual bootstrap state and link both from README and handoff.
     Scientific results stay explicitly "not yet evaluated" until supported by
     linked experiment records; synthetic checks do not establish science.
     Do not import a large review bot/router or
     Fortran/MPI/GPU matrix. Document unavailable controls without pretending
     a check or human approval exists; ask before consequential weakening.
B04: synthetic fixture-manifest validator, test-first. Accept a valid control;
     reject a same-shape/same-set species permutation for the correct reason,
     duplicates/missing identities, checksum mismatch and unsupported schema.
     Temporarily changing ordered comparison to set comparison must make the
     ordering test fail; retain the observed evidence and restore the code.
     No nuclear-data loader or scientific model belongs in this issue.

Use one orchestrator and isolated workspaces for concurrent implementation.
You may delegate bounded investigations, implementation and fresh read-only
reviews, initially no more than three useful specialists concurrently. Select
Sol High for substantive code/workflow work, Astra High for difficult
scientific/design critique, Luna High for narrow mechanical work if useful;
record substitutions if required. Lead owns integration and evidence checks.

For merge-intended work follow the entire adopted cycle: governing issue,
investigation, implementation/checks, self-review, pushed draft PR candidate,
fresh independent adversarial review tied to exact head/base SHAs, preserved
findings and dispositions, fixes plus appropriate re-review, ready-for-human
handoff, human merge decision, merged-result checks and issue closeout.
One reviewer may cover multiple risk viewpoints. Review comments or passing CI
are not human approval. Stop at each merge checkpoint with the concrete PR,
exact candidate, checks, dispositions and limitations. The maintainer merges,
or explicitly delegates merging that candidate. Do not auto-merge or treat
silence or the general launch authority as a merge decision. Continue other
independent authorized work while a checkpoint is pending.

Budget and stop rules:
- Aggregate B01–B04 verification: 2 CPU-hours, local plus CI.
- Maximum 10 minutes per CI job; 1 GiB per test process; 100 MiB generated
  test scratch, excluding dependency environments/caches.
- No GPU, training, bulk dataset downloads, HPC, paid compute/service purchase,
  reference-project edits, data regeneration or Phase 1 work.
- Track measured CPU time when reliable, otherwise charge elapsed time times
  allocated CPU count; include CI and parallel workers conservatively.
  Estimate the next run and stop/report before exceeding a cap. Do not repeat
  successful checks without a new change or unresolved concern.
- Per governing issue: one initial independent review plus focused repair
  verification. Seek maintainer direction before another broad review round
  or budget increase. Unresolved blockers remain blockers.

Actual phase exit criteria (all required):
1. Correct public owner/repository and BSD-3-Clause publication record, with
   confirmed copyright/release wording, portable intended seed and preserved
   local review/provenance history.
2. Minimal package/environment and fast checks reproduce from a fresh isolated
   checkout; imports are side-effect-free. No model or bulk data is included.
3. Draft-PR CI demonstrably runs; a controlled failure is detected and the
   corrected final candidate passes; actual protection/permissions are recorded.
   The progress view covers phases and B01–B04 with dependencies/status and
   actual PR links or None. The reusable meeting template and initial bootstrap
   report are linked from README and handoff, reflect recorded work and retain
   "not yet evaluated" for unsupported scientific results.
4. B04 has the valid/invalid controls and ordered-to-set mutation evidence,
   with required acceptance/checks satisfied for the final candidate.
5. At least B04 has completed the whole governing-issue-to-human-merge cycle,
   including an exact-SHA fresh independent review, preserved dispositions,
   human merge decision and passing checks on the merged result. Apply the
   adopted review process to B02/B03 PRs as well; only B01's minimum seed has
   the explicitly recorded initialization exception.
6. Issues, remaining limitations/follow-ups, budget use, merged SHAs and a
   concise durable handoff are current. Scientific choices/data qualification
   remain properly scoped; a synthetic test does not complete NS1–NS3.

If a required input, publication prerequisite or human merge decision is
missing, preserve a resumable handoff and report the exact pending step; do
not claim Phase 0B complete. Once all exits actually hold, mark the native goal
complete, summarize evidence and remaining limitations, then stop. Do not
continue into Phase 1 or model implementation.
```
