# Phase 2D source and original-paper grounding

Targeted read-only checks on 2026-11-20 continue the
[original Qiosk-to-nuclear trace](../integration/GROUNDING.md). They do not relabel
2B/2C evidence or their original reviews. Local guides routed discovery; original
papers and actual retained producer files supplied the checks below. Private PDF
hashes/extractions and selected equation/result renders remain in the local record.

| Original source | Checked evidence and 2D consequence |
| --- | --- |
| Pei Zhang, Sankaran & Hawkes (2021), [a priori reactor/DNS study](https://doi.org/10.2514/6.2021-1784), PDF pp.7–10 | Reconstruction on different source distributions does not establish free evolution. Two within-parent forced IVPs cannot establish physical or simulation-level generalization. |
| Pei Zhang & Sankaran (2022), [autoencoder reacting systems](https://doi.org/10.1615/JMachLearnModelComput.2022045133), PDF pp.6–7 Eq.4–6, p.10, pp.19–20 | Encoder derivatives, chemical source and PSR inlet closure are distinct; integration/decoding and spurious fixed points require separate assessment. CRUCIBLE uses physical identity coordinates and one vector kinetics source, with no PSR inlet term or decoder. |
| Pei Zhang, Liu, Lu, Sankaran & Guannan Zhang (2022), [OOD-aware autoencoder](https://doi.org/10.3934/dcdss.2021138), PDF pp.12–16 | PSR/DNS distribution and uncertainty/error assessment are separate from finite-input checks. Positive T/rho and table coverage are not learned-domain detection. Preserve train-only preprocessing; no detector is added. |
| Pei Zhang, Ramanuj & Sankaran (2025 online; 2026 issue), [MTS/SiC kinetics](https://doi.org/10.1111/jace.70267), PDF p.5 Eqs.4–5, pp.9–12 | One vector source evolves fixed linear coordinates while three heads reconstruct/read out chemistry. Carry source/integration/evaluation separation; do not import chemical heads, T/P conditioning, conversion factors or normalized error scores. |
| Xiaoyu Zhang et al. (2025), [astrophysical reacting flows](https://doi.org/10.3847/1538-4357/adf331), PDF p.3 and p.10 | A different author group and fixed-step abundance-increment target. Its fallback/cost results do not change CRUCIBLE's instantaneous-RHS target or authorize model rollout. |
| Harris et al. (2017), [CCSN tracer post-processing](https://arxiv.org/abs/1701.08876), PDF pp.15–18 | Initialization, NSE transition and thermodynamic sampling/extrapolation affect the physical comparison. The selected saved-state/linearly forced problem is a declared new IVP, not hydro reproduction. |
| Timmes (1999), [network integration survey](https://doi.org/10.1086/313160), numerical-method discussion | Bare first-order Euler has no automatic step-error estimate; nonlinear convergence and step refinement are different. The proposal measures mesh differences and makes no formal-order or physical-accuracy claim. |

The actual Qiosk part-1 affine derivative mapping and part-2 source callback were
read, without import/execution. Constant offsets disappear from derivatives;
optimization target scaling does not define an ODE coordinate change. Chemical
normalization and the float32/VODE choices described in the earlier trace are
not copied into native nuclear integration.

Retained producer evidence, relative to its hash-bound `source_postp`:

- `xnet_integrate_be.f90:228–276,306–330`: rates refreshed only on the first
  heating-off iteration, abundance monomials refreshed thereafter; negative/below
  `ymin` trial values set to zero; update/mass stopping tests. The proposal names
  its fresh-F/residual adaptation explicitly.
- `xnet_jacobian_dense.f90:133–186,388–410,450–459`: fixed-coefficient monomial
  partials and native dense LU calls. Full EOS/weak/screening composition
  dependence requires the proposed numerical derivative; LU status must be checked.
- `xnet_conditions.f90:89–129`: linear interpolation, first-knot hold and possible
  late extrapolation/hold. The proposal adds exact-knot and fail-closed coverage
  behavior to an isolated staged numerical copy.
- `xnet_abundances.f90:41–48`, `xnet_eos_starkiller.f90:48–65`,
  `xnet_integrate.f90:532–597`: composition supplies Q/B; fresh rate evaluation
  refreshes EOS/weak/screening; zero active neutrino count removes that forcing path.
- `model_input_pdata.f90:620–621,712–713,924–925`: production initialization
  renormalizes. The small driver bypasses it and preserves the exact saved Y/B0.
- `xnet_ffn.f90:86–118`: interpolation domain and native log-rate cutoff;
  temperature/rho endpoints alone cannot establish evolving-composition coverage.

These observations support the **proposed** protocol. No new numerical convergence,
Jacobian qualification, reference acceptance or producer execution is implied.
