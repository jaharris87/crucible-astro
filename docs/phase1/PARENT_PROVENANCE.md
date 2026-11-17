# Parent simulation and production attribution

Updated 2026-11-17 under [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10).
**Evidence classes matter:** the maintainer supplied the collection's lineage
and roles; original publications corroborate the named model, not its exact
post-processing build or every supplied file.

## Maintainer report

The maintainer identifies the parent as **Chimera D9.6-SN160-3D**, used as the
basis of the two publications below. This supplies **one identified hydrodynamic
parent**, not two independent simulations. Relationships among additional
post-processing reruns/variants and any physical trajectory-family grouping
still need explicit treatment before scientific partition acceptance.

| Production stage | Maintainer-attributed contributor |
| --- | --- |
| Chimera simulation data | Eric Lentz |
| XNet post-processing source | Raph Hix and J. Austin Harris |
| Post-processing workflow scripts/tooling | Andre Sieverding |
| Execution for this collection | James Ternullo |

These roles are recorded as maintainer attribution, not independently reconstructed
from paper authorship. The maintainer reports research-group participation in
Genesis ENACT-AI and little formal dataset licensing/reuse documentation. A formal
custodian/retention arrangement and dataset redistribution determination remain
undocumented. Project access for this authorized work is distinct from public
release; keep real records local. Neither paper availability nor the repository
software license supplies a dataset license.

## Original publication checks

- **Sandoval et al. (2021)**, *Three Dimensional Core-Collapse Supernova Simulations
  with 160 Isotopic Species Evolved to Shock Breakout*, ApJ 921, 113,
  [DOI 10.3847/1538-4357/ac1d49](https://doi.org/10.3847/1538-4357/ac1d49).
  The [primary author manuscript v2](https://arxiv.org/html/2106.01389v2), revised
  2021-11-12, names D9.6-sn160-3D in §II.5: a 9.6-solar-mass, zero-metallicity
  progenitor evolved with CHIMERA before FLASH continuation. Table 1/§III.1 give
  466.6 ms post-bounce as the mapping time. §II.4 describes sn160 and a network-edge
  limitation; Table 2 lists species. These facts do not identify this collection's
  tracer files, processed rates or derivative alignment.
- **Neopane et al. (2026)**, *Simulation to a Newborn Supernova Remnant from a
  Low-mass Iron Core Star*, ApJ 1008, 36,
  [DOI 10.3847/1538-4357/ae8a44](https://doi.org/10.3847/1538-4357/ae8a44).
  The [primary author manuscript v2](https://arxiv.org/html/2606.19490v2), revised
  2026-07-08, explicitly uses the same D9.6 model in §II.7. §II.5 distinguishes
  full sn160 from a decay-only network and describes decay-energy escape/deposition
  assumptions. Those continuation-specific heating definitions must **not** be
  assigned to the inspected XNet `edot` diagnostic. Its network/rate description
  also cannot establish the exact supplied post-processing inputs.

The DOI/journal endpoints were inaccessible to the browsing tools; exact DOI
associations and versions were verified through the primary arXiv records and
HTML manuscripts. No PDF page numbers are invented. Paper uses of a nuclear
“tracer species” are not evidence of Lagrangian trajectory IDs in this collection.

## What is and is not bound

The selected raw files have local hashes and independently verified layouts.
Recovered original inputs corroborate all three pairs' initial time/T/rho. A/B
have zero native initial abundances and take the inspected NSE initialization
fallback; their composition Ye matches the appended initial Ye. C follows
name mapping/normalization, reproduced to floating-point summation precision.
These checks strengthen association; no original NSE solver was rerun.

The raw audit artifact's immutable metadata still says its physical parent was
unknown when extracted. The current card and a separate local provenance overlay
record the subsequent maintainer identification; original HDF/manifest bytes and
all-false scientific masks are not rewritten. The new three-state reference
diagnostic is separately bound to a selected source/EOS/build, not proof of the
historical generating build. No simulation-independent holdout, qualified stored
RHS, deposited heating, or dataset release follows from the new attribution.
