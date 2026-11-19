# Portable evidence and citation notes

Inspected 2026-11-17. Absolute machine locators are omitted from this public version. Source code establishes inspected behavior, not provenance of an existing run. PDF pages below are **one-based PDF positions**, not necessarily printed labels. Recommendations elsewhere are CRUCIBLE design judgments, not quotations from these sources.

## Source aliases and access limits

This is a portable adaptation of the Phase 0A evidence notes, not a new source audit or independent review. Original absolute locators and fingerprints are preserved in the ignored local startup archive described in [BOOTSTRAP](../BOOTSTRAP.md#local-provenance-preservation). No reference code, data or PDFs are distributed with this repository.

| Alias | Source identity | Access and limits |
| --- | --- | --- |
| Q | Maintainer-supplied chemical research checkout `qiosk_sic_part1` | No root Git identity in the historical inspection; consult the optional local locator first, then report any specific access gap. |
| N | Q-relative `nuclear_kinetics/source_postp` | Inspected HEAD `200b024cd06abdf4edaee489d6229edaa9ae30b3`, with local changes; HEAD alone is insufficient. |
| RUN | Q-relative `nuclear_kinetics/Run_slab_033` | Private/local reference outputs; not redistributed or qualified. |
| EN | Maintainer-supplied ENACT-AI proposal/reference collection | P1/P2 are non-distributed project documents; consult the optional local locator and proposal guide first, then request only a missing named version/page. |
| X | XNet workflow checkout | Inspected HEAD `b885318c1b2f9645bba0506df6627ee0a1d12dd8`; local inspection only. |
| F | fTimer workflow checkout | Inspected HEAD `865f108c297fc5dff072c97182d2072c8cb17727`; local inspection only. |

Alias-relative filenames and line/page locators below identify historical observations. A public citation does not establish provenance of the inspected run. Omitted local inputs are not a reproducible public dataset.

## Optional local reference discovery

A maintainer may supply an ignored `.local/REFERENCES.md` in a particular checkout.
It lists verified read-only local locations and entry points without copying the
existing indexes. Consult it before asking for background already accessible.
The Genesis workspace README provides the related-code map; its nucleosynthesis
guide and annotated paper index route scientific reading; its proposal guide and
meeting artifacts concern project commitments/discussions. Chemical implementations
and the XNet development/upstream trees are reference implementations. Development
workflow documents are engineering examples, not scientific evidence or adopted
CRUCIBLE policy. Read selectively and verify consequential claims against original
papers or the relevant producer; guide descriptions and path existence are not
new scientific validation. Report specific unavailable material rather than assume
access. CRUCIBLE's accepted decisions and workflow remain authoritative.

Keep absolute machine paths only in that ignored locator. Do not publish it,
PDFs, proposal material, reference source trees or local inventories. Portable
bibliographic identities, historical observations and public source links in this
file remain usable without local access. References are optional for development
and are never runtime, installation or CI dependencies.

Ignored files do **not** accompany a Git checkout or new worktree. One simple setup
is to copy only the locator from a known primary CRUCIBLE checkout, with explicit
paths chosen for the actual host (no assumed parent layout):

```sh
reference_primary='/absolute/path/to/primary/crucible-astro'
reference_worktree='/absolute/path/to/target/crucible-astro'
if [ -f "$reference_primary/.local/REFERENCES.md" ] &&
   [ -d "$reference_worktree" ] &&
   [ ! -e "$reference_worktree/.local/REFERENCES.md" ]; then
    mkdir -p "$reference_worktree/.local" &&
    cp "$reference_primary/.local/REFERENCES.md" "$reference_worktree/.local/REFERENCES.md" &&
    git -C "$reference_worktree" check-ignore -v .local/REFERENCES.md
else
    printf '%s\n' 'Check source/target paths or preserve the existing target locator.'
fi
```

Check the reported ignore rule and recheck the locator's paths on the target host;
do not force-add it. An existing locator is preserved by this recipe. If no usable
locator exists, use the portable citations here and state the precise missing
local-access information. Copying the locator grants no permission to change or
execute the reference projects. The Phase 0B addition verified path availability
and entry points only; historical review/source records are unchanged.

## Papers and funding scope

| ID | Source and exact location | Consequential finding / boundary |
| --- | --- | --- |
| P1 | Final narrative (`narrative_ENACT_final.pdf`, non-distributed reference), §3 p. 4, §4 p. 5, §§5–6 p. 6 | Small comparison spanning latent, grouped and nonintrusive methods, common abundance/energy/cost metrics; NS1 representative CCSN+NSM reference data, NS2 general prototype interface, NS3 stand-alone reduced r-process comparison. Production coupling explicitly Phase II in nuclear-specific §3. Metric 3 proposes hundred-fold r-process energy-inference improvement at suitable NSM accuracy; not a measured result or universal threshold. Historical month/day labels are not this roadmap's deadlines. |
| P2 | Final summary (`projectsummary_ENACT_final_v2.pdf`, non-distributed reference), p. 1 | Broad embedding/latent-dynamics language; does not remove P1's multi-method scope. Broad simulation language in P1 p. 5 and this summary versus P1 p. 4 is preserved as D-008, not silently expanded into production coupling. |
| P3 | [Hix & Meyer (2006)](https://arxiv.org/abs/astro-ph/0509698), §2.2–2.3 pp. 6–7, Eqs. 10–11; §4 pp. 13–15; §5 pp. 16–18 | Defines conventional Y/X, baryon/charge relations and mass-weighted nuclear energy release; discusses neutrino/thermal losses and equilibrium timescales. These motivate questions/checks, not proof of the supplied data's semantics. Strong equilibrium need not imply weak equilibrium. |
| P4 | Hix et al. QSE network (2007) (`HiPaFr07.pdf`, non-distributed reference), pp. 1–2 | Physics-based grouped reduction has a demonstrated silicon-burning use; neutronization/freeze-out matter. Its grouping/performance is not automatically valid for r-process. |
| P5 | [Harris et al. tracer study (2017)](https://arxiv.org/abs/1701.08876), p. 1, p. 6, §4.4 pp. 15–17, §4.5 p. 18 | Sampling, initialization, thermodynamic extrapolation and NSE transitions affect post-processing yields independently of surrogate error. Study-specific settings are not universal CRUCIBLE thresholds. |
| P6 | [Zhang, Ramanuj & Sankaran, ZhRaSa25](https://doi.org/10.1111/jace.70267), §2.2 p. 5 Eqs. 4–5; §3.2.1 p. 7 Eq. 6; §3.2.2 pp. 9–12 | Fixed PCA representation, nonlinear reconstruction/surface readouts and separate vector latent RHS; integrated comparisons exist in paper. `1−RMSE` is not a per-species percentage guarantee. Boundary/long-horizon failures support separate rollout checks. Chemical architectures, T/P inputs and five coordinates are study choices. |

P6 bibliographic identity is [DOI 10.1111/jace.70267](https://ceramics.onlinelibrary.wiley.com/doi/10.1111/jace.70267). The local PDF records acceptance in 2025 and a 2026 journal volume. No chemical speed factor is adopted as nuclear performance evidence.

Used the final narrative directly for commitments, not earlier drafts. The umbrella proposal guide (`PROPOSAL_GUIDE.md`, non-distributed reference) records matching body text for compact `ENACT_AI.pdf` pp. 1–10 and the final narrative; this task did not repeat that full equivalence check. `NP_ML_2025.pdf` is earlier background, not a current commitment source and not reread here. Administrative/personnel appendices were not ingested.

Lead verified the key proposal text and rendered p. 5, chemistry Eq. 5 on p. 5, and Hix–Meyer equations on p. 6. Specialist also visually checked selected science pages. Existing bundled `pypdf`/`pypdfium2` enabled extraction/rendering; no environment installed. Poppler rendering encountered font-cache errors, so working bundled rendering was used. Temporary extractions/renders are not required deliverables.

## Chemical implementation: what to transfer and avoid

Required starting documents read: README (`README.md`, non-distributed reference), AGENTS (`AGENTS.md`, non-distributed reference), handoff (`NUCLEAR_KINETICS_HANDOFF.md`, non-distributed reference), walkthrough (`CODE_WALKTHROUGH.md`, non-distributed reference), paper map (`PAPER_MAP.md`, non-distributed reference), data/artifacts (`DATA_AND_ARTIFACTS.md`, non-distributed reference), known issues (`KNOWN_ISSUES.md`, non-distributed reference). They orient inspection; source supplies the consequential checks below.

| ID | Q-relative source location | Verified observation and design consequence |
| --- | --- | --- |
| C1 | `run_reduction.py:69–79,115–154`; `reduction_models/autoencoder.py:100–179`; `chemsource_model.py:109–143`; `reduction_models/src_model_class.py:43–75` | Fixed training-fit PCA plus nonlinear reconstruction and two chemical surface heads; separate signed-vector source regression. Carry separation forward, omit chemical heads and hard-coded schedules. No basis for a mandatory NN family. |
| C2 | `chemsource_data_prepare.py:111–120,141–150`; `data_utils.py:221,385–395` | Affine scaled/subset source projection is derivative scaling then PCA matrix, with no centering offset. Chemical mass-fraction conversion is `M*gas_w/rho`; not automatic nuclear conversion. |
| C3 | `data_utils.py:185–188,281–289,324–356`; `chemsource_model.py:93–103`; `chemsource_data_prepare.py:48–62`; `docs/KNOWN_ISSUES.md`, “Data alignment and evaluation” | Unsorted file identities, full-data normalization, shuffled loaders, and transform reloading hazards. Require saved IDs, train-only fitting, prediction-metadata alignment and saved transforms. Existing truth/prediction pairs are not thereby all invalid. |
| C4 | `run_reduction.py:24–34,44–79,98`; `chemsource_data_prepare.py:32–38`; `chemsource_model.py:120–143`; `docs/KNOWN_ISSUES.md`, “Missing inputs…” | Active chemical XML/config/checkpoints/source data absent; stage paths/dimensions differ; top-level experiment scripts and 500,000-epoch source training are unsuitable inspection entry points. Missing chemical artifacts do not block a clean nuclear design. The paper's integration evidence is distinct from absent integration code in this copy. |

## Nuclear producer findings, not accepted training semantics

The historical observations below retain their original source aliases. For
the separately authorized Phase 1 audit of the collection at its maintainer-moved
location, consult the [current S01 evidence](../phase1/S01_AUDIT.md) and ignored local
locator. Current findings do not establish the generating build or retroactively
turn this historical inspection into data qualification. [Genesis guidance](../phase1/GENESIS_GUIDANCE.md)
pins the actual released data-card template and remaining access gaps.

| ID | N/RUN-relative source location | Observation / limit |
| --- | --- | --- |
| N1 | N `xnet_abundances.f90:8–18`; `xnet_integrate_be.f90:123–138,237–275,329–338`; `xnet_evolve.f90:97–98,118–157`; `xnet_integrate.f90:55–62` | `ydot` is evaluated at a trial/Newton iterate; a correction/floor can change `yt` before convergence and copy to accepted `y`, with no final reevaluation on this path. Both iterates are at the **new implicit time**, not old-time explicit Euler. This is normal implicit-solver bookkeeping, not evidence of a solver bug. A fresh accepted-state RHS comparison is needed only to establish training-label fidelity against the chosen error budget. Initial output precedes initial timestep RHS evaluation and needs its own validity audit. Actual run/source correspondence remains unknown. |
| N2 | N `xnet_output.f90:71–73`; `xnet_output_hdf.f90:85–118,238,331–375`; `postp.f90:313–332` | Binary ts output contains full `y` and appended derivatives, optional fluxes; header includes network/flux metadata. HDF mass fractions are selected `A*y`, sometimes interpolated. NSE writer assigns composition and zero derivative placeholders; ASCII carries `NSE` tag. HDF writer's ordinary binary write uses `edot` without scalar indexing unlike the other writer, so actual record widths must be verified against build/batching. Do not infer layout from filename or a single writer. |
| N3 | N `add_ydot_to_ts.py:25–36,136–164`; `xnet_evolve.f90:39,154–158` | Patcher's alternative is `(y−yo)/tdel` for an internal step, with first/invalid-step zero fallback; routine output every 20 integration steps. Saved-record differences have different intervals. Patcher mutates sources at top level; it was not imported/run. |
| N4 | N nested Git status/HEAD; `make_ydot.log:1–34`; N/RUN `postp` SHA-256 | Log records widths/build using HDF writer. Executable copies share `661d1057756e864519b96601f777a93f61651914033baea699037d8d863653b0`. Equal binaries do not prove generating source, patch set or which executable produced outputs. Full provenance unresolved. |
| N5 | RUN `control:8,12,16,28`; N `xnet_evolve.f90:141–145`; `xnet_output_hdf.f90:344–368` | Supplied control enables weak and neutrino reactions, selects BE, disables self-heating. Current `edot = -(enm-enold)/tdel` is a signed internal-step average nuclear mass-energy rate, not an energy increment; NSE sets it to zero. Its units and energy-loss convention still require audit. These settings do not establish every condition/input or deposited-heating semantics. They specifically disfavor an unexamined constant-Ye constraint. |

The run ASCII subset includes NSE records; it is not authoritative full-network species metadata. No binary/HDF read/qualification, reference rerun, timing measurement, training or dataset regeneration was performed. The stronger N1 call-sequence observation refines the handoff's original trial-time question; it does not declare supplied data unusable or quantify error.

## Machine-learning evaluation guidance

Primary developer guidance consulted on 2026-11-17; methodological evidence,
not selection of an ML library or permission to start model development.

| ID | Source | Application and limit |
| --- | --- | --- |
| M1 | [scikit-learn: grouped-data cross-validation](https://scikit-learn.org/stable/modules/cross_validation#cross-validation-iterators-for-grouped-data) | Dependent samples need domain-specific grouping; holdout groups are absent from paired training data. A/B/C are CRUCIBLE audit aliases, not this guidance. Actual physical groups and sufficient training coverage require data evidence. |
| M2 | [scikit-learn: data leakage](https://scikit-learn.org/stable/common_pitfalls#data-leakage) | Keep test data out of model/preprocessing fitting and selection. This supports train-only rules, not a particular split fraction, number of trajectories or astrophysical domain claim. |

## Workflow reference evidence and adaptations

| ID | Source-relative location | Transfer / adaptation |
| --- | --- | --- |
| W1 | X `AGENTS.md:167–194`; `docs/development/maintainer-workflow.md:49–75,156–283`; `docs/development/review-playbook.md:15–145`; `docs/development/scientific-validation.md:12–52,91–155`; `.github/pull_request_template.md:19–34,116–140` | Governing issue, self-review, pushed draft candidate, fresh exact-SHA read-only review, preserved findings and disposition, human merge and distinct evidence categories. Adopt proportionate roles and stopping rule; omit upstream mirror/development branch scheme. |
| W2 | F `AGENTS.md:178–203,241–258`; `CONTRIBUTING.md:46–62`; `docs/maintainer.md:15–48,90–99`; `docs/workflows/pr-open.md:7–34`; `findings-disposition.md:5–35,61–101`; `review-monitoring.md:7–17,54–92` | Targeted reading and durable findings, explicit current-SHA rerouting and anti-churn ideas. Native coverage does not prove reviewer independence. Its timing rules are router-specific, not CRUCIBLE compute budgets. |
| W3 | F `.github/workflows/codex-review.yml:149–150`; `codex-review-coverage.yml:64–68`; `.github/prompts/detailed/{software-review,test-quality-review,pragmatic-design-review}.md`; `.github/codex-review-roles.json` | Ready-only trigger/coverage explains PR-state difference. CRUCIBLE uses draft + explicit dispatch; no imported PAT, label queue or twelve-role catalog. Prompt themes inform briefs; roles remain viewpoints. |
| W4 | X `.github/workflows/xnet-pr-pilot.yml:1–24,38–45,49–114`, `xnet-gnu.yml:1–24`; `.github/ISSUE_TEMPLATE/{investigation,change}.yml`; F `.github/workflows/ci.yml:1–19,109–183`; `.github/ISSUE_TEMPLATE/{strategic-question,feature-request}.yml` | Templates separate decision/investigation from bounded implementation and demand observable evidence. CI uses read-only permissions, distinct test/configuration jobs and configuration probes; XNet retains failure evidence and pins checkout. Adopt minimal permissions, clean checks and useful failure logs; do not copy Fortran/MPI/compiler matrices, branch filters or platform claims into CRUCIBLE. |

Local repository evidence is sufficient for the historical workflow comparison; no GitHub writes or upstream synchronization occurred. Current GitHub [branch-protection documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) was consulted for stale-approval controls on 2026-11-17; availability/settings must still be checked in Phase 0B.
