# Proposed native diagnostic streams, version 1

These are D-038 implementation formats, not execution authority. All files are
new per process, little endian, without Fortran sequential-record markers.
Unless specified otherwise, numbers are binary64. Matrix arrays use Fortran
column-major order. Existing native logs, failure snapshots, counter streams and
terminal `status.txt` are retained. `SUCCESS` means the fixed diagnostic process
completed; failed derivative/linear criteria remain scientific outcomes.

Commands `repeat-3`, `repeat-1` and `diagnose` require ordinary version-1
`input.bin` with mode zero. The driver's setup fresh F is the first repeat, or
one extra setup F for each diagnose process. No-argument behavior and the old
mode-2 mixed-sign direction remain unchanged. `diagnose` uses odd one-based
species support for its second direction, separately from the old protocol.

All diagnostic commands write:

- `diagnostic-evaluations.bin`: 324-value rows `[rhs_call_id,time,T9,rho,Y160,F160]`
  for every successful physical evaluation, including subsequently branch-refused
  probes. A domain-refused probe executes no kernel and writes no such row.
  Supplied Y/time/T9/rho must remain bitwise unchanged. A mutation writes
  `diagnostic-input-mutation.bin`: 326 values
  `[before_time,T9,rho,Y160,after_time,T9,rho,Y160]` before the fatal identity gate.
  Nonfinite computed values
  remain fatal and use failure snapshots.
- `diagnostic-ieee.bin`: eleven int64 values per successful call:
  `[call,nearest_before,nearest_after,underflow_control_supported,gradual_before,
  gradual_after,invalid,divide_by_zero,overflow,underflow,inexact]`.
  Boolean values are zero/one; gradual is -1 when its control is unavailable.
  Rounding must be nearest and modes must remain unchanged. Exception flags are
  observed without clearing them; they are not isolated per-call increments.
  Standard Fortran does not identify DAZ; no DAZ-identification claim is made.
- `species.bin`: `[Z160,A160]`.
- `used-maps.bin`: the unchanged original RHS harness mapping stream:
  int32 la/le followed, for each order, by order/nreac/nan, participant indices,
  mu, n0 and binary64 assembly factors. Use existing Phase 1 `parse_maps`.
- Baseline payloads described below, plus legacy counter/status/runtime artifacts.

A baseline payload has twelve int32 header values:
`[0x43524442,1,160,nc1,nc2,nc3,nc4,nb1,nb2,nb3,nb4,branch_size]`, then
`[call,time,T9,rho,B,Q,Ye,cv,etae,detaedt9,Y160,F160,csect1..4,b1..4]`, then
`branch_size` int32 branch selectors. The physical closure has
`nc=[683,1345,16,4]`, `nb=[1862,4860,53,19]`, `branch_size=10240`.
`repeat-3` writes `baseline-001.bin` through `baseline-003.bin`; `repeat-1` writes
only `baseline-001.bin`. `diagnose` writes `baseline-001.bin` after the fourth
Jacobian baseline restore, immediately before forming the fixed-b derivative,
so that the exported coefficient workspace binds that matrix without a new F.
`candidate.bin`, when produced, has the same layout.

## Derivative records

`diagnose` writes all four `jacobian-factor-N.bin` 160-by-160 matrices in ordinal
factor order `[0.1,1,10,100]`. An unavailable column is explicit NaN and makes its
matrix incomplete; a nonfinite computed quotient remains fatal.

- `matrix-status.bin`: four five-value rows
  `[factor,Jacobian_id,complete,rhs_count_before,rhs_count_after]`.
  Its baseline F call is `before+1`, restored F call is `after`.
- `fd-columns.bin`: legacy six-value selected-column records.
- `fd-probe-attempts.bin`: twelve-value records
  `[Jacobian_id,column,stencil,nominal_delta,actual_offset1,actual_offset2,
  probe_component1,probe_component2,ok1,ok2,rhs_id1_or_zero,rhs_id2_or_zero]`.
  A branch-refused physical call has a nonzero ID and false ok flag. A domain or
  unrepresentable-increment refusal has zero ID. Existing refusal reasons and
  branch events are retained; complete selected columns bind their F values
  through these IDs, baseline records and `diagnostic-evaluations.bin`.
- `fixed-b-jacobian.bin`: the original native monomial matrix, 160-by-160,
  formed using the exported baseline b workspace; not the full-F derivative.
- `direction-attempts.bin`: 327-value rows
  `[direction,multiplier_index,stencil,h1,h2,ok1,ok2,Yprobe1_160,Yprobe2_160]`.
- `directional.bin`: legacy 27-by-1286 layout:
  `[direction,multiplier_index,stencil,admissible,h1,h2,v160,Jv_factor_one_160,
  Dv160,dYprobe1_160,dYprobe2_160,Fbaseline160,Fprobe1_160,Fprobe2_160]`.
  Unavailable directional estimates/probes and incomplete factor-one Jv use NaN.
- `diagnostic-jv.bin`: 160-by-3-by-4 array; incomplete matrices give NaN Jv.

The fixed-b build has a separate native log count of one. `counters.json`
`jacobian` counts only the four full-F finite-difference builds. For diagnostic
failure snapshots, matrix-baseline ordinal -1 identifies the fixed-b baseline;
positive ordinals identify `jacobian-bases.bin` as before, zero means unformed.

## Frozen linear algebra and candidate

Only state three has both `old-state.bin` (160 values) and `frozen-h.bin` (one
value). Presence must be paired; lengths, domains and `time=h=1.953125e-7` are
checked before setup F. The orchestrator binds both files to the private annex.
Other states provide neither file and execute no linear stage.

For each complete matrix, `linear-factor-N.bin` contains five int32 values
`[0x4352444c,1,160,LU_info,solve_info]`, then
`[h,Y160,Yold160,F160,M160x160,RHS160,LU160x160,correction160]`, then 160 int32
pivots. `solve_info=-999` means not called. Any nonzero solve status leaves
the correction unavailable NaN; returned values from an unsuccessful solve are
not tested or published as a correction. A successful status with nonfinite
computed correction remains fatal.
Native `jacobian_scale`, decomposition and back-substitution form the actual
system/solution. Optional diagnostic status outputs preserve each LAPACK result;
legacy calls without that option still abort on nonzero info. Finite LU failures
are retained scientific outcomes and do not choose another factor.

`candidate-status.txt` is one of `SKIPPED <reason>`, `REFUSED <domain reason>` or
`EVALUATED`. Only the factor-one correction can produce a candidate. It is never
projected, iterated, time advanced or accepted. A refused candidate's full
`[time,T9,rho,Y160]` is retained in `candidate-refused.bin`; an evaluated candidate
produces one fresh F and `candidate.bin`.

Including setup, conservative physical-call bounds are 12 repeats + 3 diagnose
setup calls + 103704 full-J work + 486 directional probes + 3 restores + 1
candidate = **104209**. No source evaluation is added for maps, baseline exports,
fixed-b matrix construction, matrix scaling, LU or persistence.
