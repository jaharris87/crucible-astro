# Qiosk-to-nuclear design lineage for 2C

This is a **2026-11-20 targeted continuation** of the original Qiosk adaptation,
not a replacement design or a retrospective extension of Phase 0A review.
[D-003](../../docs/DECISIONS.md#decision-d-003-first-baseline-target-strategy)
records the maintainer's original choice to start with instantaneous RHS because
that is the chemical workflow. The preserved
[source findings C1–C4](../../docs/science/EVIDENCE.md#chemical-implementation-what-to-transfer-and-avoid)
and [design chain rule](../../docs/science/DESIGN.md#representation-and-derivative-consistency)
already carry the separation of data, representation, one vector source and
evaluation. The maintainer reaffirmed this lineage during 2C.

## Original papers checked

Page numbers here are one-based PDF positions; printed pages coincide except
for the OOD paper, whose first PDF page is journal p.913. These are selective
original-paper checks; local bibliographic annotations are discovery aids.

| Original source | Specific evidence | Application and boundary in 2C |
| --- | --- | --- |
| Pei Zhang, Sankaran & Hawkes (2021), *A priori examination of reduced chemistry models derived from canonical stirred reactors using three-dimensional direct numerical simulation datasets*, [DOI](https://doi.org/10.2514/6.2021-1784) | PDF p.7, Eq.4/Fig.6 compares reconstruction on DNS states from different reactor training distributions; p.10 leaves coupled 3D deployment for future work. | Coverage and pointwise reconstruction are separate from free-running trajectory validity. Finite within-parent nuclear qualification does not establish generalization or rollout accuracy. |
| Pei Zhang & Sankaran (2022), *Autoencoder Neural Network for Chemically Reacting Systems*, [DOI](https://doi.org/10.1615/JMachLearnModelComput.2022045133) | PDF p.6 Eq.4 differentiates the encoder; p.7 Eqs.5–6 distinguish source and inlet closures. P.10 separates regression checks from integration/decoding. P.14 identifies source-closure ambiguity that a nonlinear decoder does not cure; pp.19–20 show spurious fixed points. | Differentiate the represented dynamics consistently. A decoder is not another physical kinetics source. Identity/full-state coordinates currently remove the encoder transformation; saved target optimization scaling must still be inverted before returning native rates. Callable equivalence alone cannot establish learned dynamics accuracy. |
| Pei Zhang, Liu, Lu, Sankaran & Guannan Zhang (2022), *An Out-of-Distribution-Aware Autoencoder Model for Reduced Chemical Kinetics*, [DOI](https://doi.org/10.3934/dcdss.2021138) | PDF pp.12–16 / journal pp.924–928 distinguish PSR and DNS reconstruction distributions and assess uncertainty/error discrimination. PDF p.14 says the entire PSR dataset is scaled before splitting. | Finiteness and positive conditions are callable checks, not OOD detection or physical safety. No detector/gating is added in 2C. Preserve CRUCIBLE's accepted train-only preprocessing instead of copying the paper's full-dataset scaling. |
| Pei Zhang, Ramanuj & Sankaran (accepted 2025; 2026 issue), *Modeling MTS pyrolysis and SiC deposition kinetics using principal component analysis and neural networks*, [DOI](https://doi.org/10.1111/jace.70267) | PDF p.5 Eqs.4–5 separate fixed PCA coordinates, three reconstruction/surface readouts and one vector source. P.7's `1−RMSE` is a normalized aggregate; pp.10–12 show boundary/interior errors and long-horizon accumulation. | Carry the source/integration separation into the nuclear identity-state baseline. Preserve physical-unit errors and separate analytic solver verification, model fidelity, real rollouts and cost. Chemical surface heads, `W*omega/rho`, T/P features and numerical scores do not define nuclear semantics. |

Xiaoyu Zhang et al. (2025), *Deep Neural Networks for Modeling Astrophysical
Nuclear Reacting Flows*, [DOI](https://doi.org/10.3847/1538-4357/adf331), is a
**different Zhang author group**. Its PDF p.3 learns fixed-step abundance
increments; p.10's fallback and cost results belong to its own small-network
deployments. They do not replace the accepted instantaneous-RHS contract.

## Actual Qiosk source and deliberate adaptation

Read the supplied reference projects without importing or executing their
experiment scripts. Part 1 `chemsource_data_prepare.py:111–154` constructs the
affine normalized PCA state and transforms derivatives with its linear matrix,
without a centering term. `chemsource_model.py:109–151` trains and persists the
separate vector source. Part 2 `src/kinetics/utils.py:52–125` wraps that source as
an ODE callback, keeps external T/P fixed for state partials, and integrates the
latent state; `cvd_pfr_examples_reduced.py:132–155` encodes, integrates and decodes.

The original nuclear handoff explicitly permits an identity/full-state baseline
and requires actual nuclear state, target, units, conditions and constraints.
CRUCIBLE's accepted stage therefore uses all 160 ordered physical Y components
and native signed dY/dt, recorded T9/rho and composition-derived Ye. There are no
chemical surface readouts, molar-to-mass chemistry conversion, PSR inlet term,
PCA or decoder in 2C. Later representation choices remain separately gated.

The inspected Qiosk wrapper casts neural callbacks to float32 while requesting
`1e-10` local controls; it uses VODE without selecting BDF (Adams default), and
its dormant model-switch path does not update the supplied primary-model
Jacobian. These are historical implementation observations, not settings to
copy. The accepted 2C protocol deliberately uses one binary64 Radau path with
its own numerical Jacobian of the actual callback at fixed conditions. It makes
no supplied-Jacobian or formal-order claim. This preserves the mathematical
responsibility without reproducing incidental choices or known limitations.

The fixed 2C campaign checks independent analytic equations first; frozen MLP
checks remain pointwise. No paper establishes that the negative-fidelity 2B MLP
is suitable for astrophysical integration. Real forcing/reference/rollout work
remains 2D/2E. The targeted source/paper check found no concrete contradiction
requiring a change to the accepted protocol; its numerical choices remain exact.

The read-only `gpt-6.1-sol` High literature assignment and lead source inspection
retain original-PDF/source SHA256 identities, extracted pages and selected
equation/result renders privately. This later check does not relabel those
documents or the original implementation as newly independently reviewed code.
The ordinary exact-candidate PR review covers this new traceability note.
