# D-027 documentation migration

Governing [issue #39](https://github.com/jaharris87/crucible-astro/issues/39).
The maintainer separately authorized execution of the accepted
[12-guide plan](../BACKLOG.md#documentation-migration-plan) on 2026-11-19 after
Phase 1 completion. This transition changes navigation, not scientific contracts,
accepted dataset/scorer identities, process rules or Phase 2 acceptance/authority.
The [Phase 2 launch draft](../PHASE_2_LAUNCH.md) remains **not invoked**.

## Source and destinations

Pre-move source: `d7e60485b81f6afdc1817c86189acc40f97df7ae`, the verified merged
Phase 1 status closeout. Each maintained guide retains its complete source body
and heading text/order, with only relative/current-main links and the workflow
path in reusable brief examples updated. Retained preparation-time statements
remain historical where the guide already labels them so. The old path is a
compatibility page: each of its original heading/explicit anchors links directly
to the same fragment in the new guide. This includes the original title anchors.

| Original path (relative to repository root) | Maintained guide | Pre-move SHA256 | Anchors |
| --- | --- | --- | --- |
| `docs/DESIGN.md` | [docs/science/DESIGN.md](../science/DESIGN.md) | `adb3b0e0231b9ecf7e666bc41df480848e13533fbe5b6b5ab83b8ec67a881d9c` | 8 |
| `docs/VALIDATION.md` | [docs/science/VALIDATION.md](../science/VALIDATION.md) | `13631510c13924e634b1a57450ab50c86dce592ed83d0c3364b3f9e9fff24289` | 11 |
| `docs/EVIDENCE.md` | [docs/science/EVIDENCE.md](../science/EVIDENCE.md) | `9d308c16c5a809b9cb44904967940f7eaf435de4ab67f82fbd4e4643433456fa` | 8 |
| `docs/phase1/NATIVE_BENCHMARK.md` | [docs/science/benchmark/NATIVE_RHS.md](../science/benchmark/NATIVE_RHS.md) | `5ece846ae9847bbb297f04b858ffd1b7b937bb10b41448a3ad7260e6ba67df2e` | 7 |
| `docs/phase1/PARTITIONS.md` | [docs/science/benchmark/PARTITIONS.md](../science/benchmark/PARTITIONS.md) | `5cf268ece6e5566a8a5618b8743abd3715fb0b0a0694a2617d403281a395ba9e` | 5 |
| `docs/phase1/S02_READER.md` | [docs/science/data/XNET_READER.md](../science/data/XNET_READER.md) | `1718041113ea3b0c9313cf78933cda66456eaa501322bb2eca0539529aaba70a` | 4 |
| `docs/phase1/PRIMARY_RHS_DATASET.md` | [docs/science/data/PRIMARY_RHS_DATASET.md](../science/data/PRIMARY_RHS_DATASET.md) | `e8f82590bbd4f5604223aa2773a0135183db86ec8ac381caf1e1860cb15570e6` | 5 |
| `docs/phase1/RHS_DATASET.md` | [docs/science/data/PILOT_RHS_DATASET.md](../science/data/PILOT_RHS_DATASET.md) | `cf65005acec893402cbaf4b4b4f8170fb6bbd04c8e1614e6735facf74942c386` | 6 |
| `docs/phase1/ERROR_BUDGETS.md` | [docs/science/validation/PHYSICAL_ERROR_BUDGETS.md](../science/validation/PHYSICAL_ERROR_BUDGETS.md) | `f240715b5780411e1e9f9ea9d65a3ef67c5a873b6468b114c8cf991a9d419f14` | 6 |
| `docs/WORKFLOW.md` | [docs/process/WORKFLOW.md](WORKFLOW.md) | `20ac7adcb01416e6e508dce3bb84c5a1440f66040204823e7110549fea35a10c` | 13 |
| `docs/AGENT_BRIEFS.md` | [docs/process/AGENT_BRIEFS.md](AGENT_BRIEFS.md) | `3c65ca0fecaaa803c41cf1a46396416153a1089beca3a7cf7abd65e9e2448b60` | 7 |
| `docs/MEETING_REPORT_TEMPLATE.md` | [docs/process/MEETING_REPORT_TEMPLATE.md](MEETING_REPORT_TEMPLATE.md) | `0e72284374077dc7cc7f60cdebdf099ee87a1a05bf1a5b76094223ff1ae0fd2e` | 1 |

The pre-move inventory found 99 tracked Markdown inbound links to these guides
and 81 heading anchors. Literal paths in module docstrings continue to work through
the compatibility pages; source modules remain byte-identical. Maintained README,
contributor/agent guidance, status/planning routes and GitHub templates use the
new destinations. Immutable GitHub revision links are preserved.

Historical Phase 0 records, Phase 1 audits/proposals/executions/provenance/guidance,
the Phase 1 closeout index, bootstrap/audit/dated reports, all five distinct data
cards and experiment recipes stay at their original paths and bytes. They may
continue linking through compatibility pages. Current status, review and merge
receipts belong in the governing issue/PR and [handoff](../HANDOFF.md), rather than
altering those historical records.

## Accepted source bindings

An accepted source path is a locator, not permission to substitute a compatibility
page for its pinned bytes. Before moving guides, the local accepted overlay's
benchmark binding was verified against its retained original checkout:

| Binding | Recover exact Git version | SHA256 |
| --- | --- | --- |
| D-025 overlay benchmark (13,923 bytes) | `c36d1d3d6698dd216c234f3158b20750487ca6a5:docs/phase1/NATIVE_BENCHMARK.md` | `839a0ad408406f2547586be4bd23921f29ee13edaa4dd8ebe42ceb2ff65d45c3` |
| Qualification recipe's union guide (9,350 bytes) | `52e3895e3d1a6d991a0f91b66a18a90ddf10c502:docs/phase1/PRIMARY_RHS_DATASET.md` | `cbb4f8fcfaab9caa211c15c15fec15c5f3acd9c855515e7750c96b4267f465c0` |

The recipe's original guide locator already contained a later guide revision at
migration start; the pinned bytes were recovered and rehashed from the Git object
above. The accepted overlay, recipe, all private artifacts and original retained
checkouts were left untouched. The current guide or old-path stub is not that
frozen source. The migration does not claim to requalify or rerun the dataset.

For recovery into a separate local file, use `git show '<commit>:<original-path>'`,
then verify SHA256 and byte size against the accepted binding. A fresh retained
checkout of that commit preserves original relative layout; do not overwrite a
current compatibility page or edit an accepted manifest to point at changed bytes.
Full relevant Git history is required; a shallow checkout may need the named
commits fetched. No producer call or artifact regeneration is needed for recovery.

## Verification and completion

From the repository root, run:

```sh
python -B scripts/check_documentation.py
```

This bounded migration check compares exact guide bodies after the allowed link
substitutions, headings/order, all compatibility targets, all public local Markdown
links/fragments, frozen source-tree document bytes and the two accepted Git-bound
versions above. It requires the pre-move source/history and does not fetch or check
external websites. This is migration-specific evidence, not a permanent freeze
of maintained guides; later authorized content changes can update or retire this
check. The synthetic scoring example and normal checks are documented
in [README](../../README.md#read-this-package) and [CONTRIBUTING](../../CONTRIBUTING.md).
Scientific performance remains **not evaluated**.

Fresh independent review, explicit human merge and merged-result verification
remain required. The [issue](https://github.com/jaharris87/crucible-astro/issues/39)
and linked PR record exact candidates, actual commands/results, negative controls,
review dispositions, human decisions and integration. The migration goal remains
incomplete until those exits hold. No new Phase 1 or Phase 2 scientific gate follows.
