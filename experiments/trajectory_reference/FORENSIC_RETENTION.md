# Native failure snapshot retention

This repair changes diagnostic retention only. It adds no source evaluation and
changes no equation, forcing, Newton update, Jacobian, threshold or retry rule.
The actual native fixture has not been rebuilt or executed for this repair;
producer authority for new execution remains separate.

## Historical records and unchanged wire layout

The campaign prepared from `a771930` used the adapter from `c21cc7b`. On ten-attempt
BE exhaustion, native retry cleanup reset `yt`, `tt`, `t9t`, `rhot` and `yet`
before the driver called `fail`. Those old failure snapshots can mix reset input
fields with the last evaluated F/coefficient/assembly workspaces. Preserve them;
do not reinterpret them as a consistent evaluation or rewrite their bytes.

The repaired writer retains the latest physical input Y/time/T9/rho before
`cross_sect`, and its EOS and weak outputs after that call returns. It marks that
workspace available only once those retained fields are initialized. Later retry
cleanup does not overwrite the retained fields. A coefficient or RHS failure
therefore keeps the actual corresponding evaluated input, including nonfinite
computed outputs where present.

Binary layouts stay at version 1:

- `failure-state.bin`: 163 binary64 values, `[time,T9,rho,Y160]`. An explicitly
  rejected argument, such as an invalid post-update iterate, takes precedence.
  Otherwise its fallback is the latest evaluated physical input. It can differ
  from the evaluated workspace when the rejected argument was never evaluated.
- `failure-workspace.bin`: the existing fifteen-int32 header and binary64 blocks.
  Its prefix is `[time,T9,rho,Ye,cv,etae,detaedt9,Y160,F160]`, followed by the
  coefficient, assembly and Jacobian arrays in their existing order. The prefix
  now uses the retained evaluated fields. Header phase 1 still means that
  `cross_sect` returned but the current `yderiv` was not called; current F and
  assembly positions contain the declared unavailable-value NaNs. Phase 2 means
  that the current F/assembly evaluation returned, even if nonfinite.

The Jacobian block remains the current matrix workspace, potentially factored.
It belongs to the baseline last passed to `jacobian_scale`, **not necessarily
the same Y as the latest post-update F**. `jacobian-bases.bin` records that
baseline; the new `FAILURE_WORKSPACE_JACOBIAN_BASE` log entry identifies its
Jacobian ordinal. The association is updated only when that matrix is formed,
so an incomplete later finite-difference build cannot relabel an older matrix.
Ordinal zero means no such matrix has been formed and the block is initialized
workspace, not an evaluated Jacobian.
`FAILURE_WORKSPACE_LAST_EVALUATION` logs the evaluated prefix's phase/time/T9/rho.
If no physical workspace is initialized, the existing unavailable reason is
logged and no array is dereferenced. Forensic persistence failures retain their
existing best-effort handling and do not supply a new physics result.

## Verification boundary

Public Python checks follow the Fortran capture assignments into the serialized
prefix and reject regressions to mutable reset fields or premature EOS capture.
The `retry-snapshot` native synthetic scenario performs ten synthetic evaluations,
mutates all five retry-cleanup fields after each, then checks exact snapshot
prefix bits against the tenth evaluated state/EOS/F. It preserves version and
phase checks. This fixture requires future explicitly authorized native
compilation/execution; static checks are not native runtime evidence.
