# Agent instructions and reusable briefs

Maintainer adopted the workflow and concise root guidance on 2026-11-17. These are reusable brief templates, not separate policy. [WORKFLOW](WORKFLOW.md) owns process rules and [DECISIONS](DECISIONS.md) owns accepted choices. Phase 0B was separately authorized on 2026-11-17; publication and human merge gates remain. Sol workers/reviewers must explicitly use `gpt-6.1-sol` with high reasoning; report alternatives before any unavailable-model substitution.

## Active root guidance

The reviewed draft was adopted and condensed into [root AGENTS.md](../AGENTS.md) during the maintainer-directed transition (D-010). It is the active entry point; the original draft is retained in the [historical archive](TRANSITION.md#historical-review-preservation), rather than duplicated as competing policy here. Bootstrap will add verified environment/check commands when they exist.

For work after Phase 0B use the canonical [model selection and escalation policy](WORKFLOW.md#model-selection-and-escalation), accepted D-012. Current Phase 0B assignments remain unchanged.

## Bounded worker brief

```text
Task / governing issue / dependency state:
Model / reasoning effort / availability or substitution:
Model-policy reference: WORKFLOW.md#model-selection-and-escalation (D-012)
Escalation justification or N/A: question, existing-analysis insufficiency, benefit
Expected escalation deliverable / scope / effort / stop or N/A:
Lead verification/integration / actual outcome / remaining uncertainty:
Objective and observable acceptance:
Scope / non-goals / relevant decision IDs:
Inputs and exact revision/artifact identities:
Workspace and writable files (or read-only):
Required evidence and checks:
Budget: tool/CPU/GPU/wall time, disk/memory, search breadth as applicable
Stop when: acceptance met / scope ambiguity / invalid input / budget exhausted
Report: facts with source locations; actual actions/checks; artifacts;
        limitations, decisions needed and next bounded action
Do not: modify other workers' areas, change authority, launch unbudgeted work,
        or convert assumptions into scientific facts.
```

## Fresh independent reviewer brief

```text
Read-only review of governing issue [ID] and PR [URL].
Model [explicit ID], reasoning effort [level], availability/substitution [record].
Model policy: WORKFLOW.md#model-selection-and-escalation (D-012, after Phase 0B).
Escalation [N/A or question, insufficiency, expected benefit/deliverable/scope/effort/stop].
Outcome [lead verification/integration, resolution and remaining uncertainty].
Candidate head [full SHA], base [full SHA]; playbook [revision].
Acceptance/non-goals: [verbatim issue criteria or link].
Risk viewpoints assigned: [minimum credible selection].
Evidence packet: [diff, source, relevant contracts, test/run records].
Unavailable context/checks: [explicit]. Budget/stop: [bounded].

Verify actual candidate identity. Independently inspect requirements and source;
seek counterexamples and false passes. Do not repair the candidate. Do not assume
implementation claims are true. Challenge unnecessary abstractions/dependencies
and recommend the smallest simplification preserving required safeguards.

Return PASS or stable proposed finding IDs with severity/confidence, exact SHA,
path/line, evidence, consequence, smallest fix and verification needed. List
checks actually performed and limitations. No finding quota or style-only churn.
```

For Phase 0A only, a local documentation checksum inventory replaces PR/SHA because GitHub changes are prohibited. This bounded exception does not weaken the future pushed-PR rule. The reviewer gets original requirements and sources without the author's self-assessment or other reviewers' conclusions.

## Composable role questions

| Viewpoint | Reusable challenges |
| --- | --- |
| Requirements/scope | Does the result meet each acceptance criterion? Are temporary restrictions presented as permanent policy? Are milestones or authority overclaimed? What unsupported scope/abstraction can be removed? |
| Software/test effectiveness | Trace parsing, mapping, failure paths and serialization. Would the test reject a same-shape wrong species order or wrong units? Did the negative control fail for its intended reason? Can the test and implementation share the same mistaken oracle? |
| Scientific/numerical | Verify state/target/conditioning and chain rule. Is the reference independent and appropriate? Are constraints regime-correct, tolerances justified, energy defined, and reconstruction/RHS/rollout distinct? Can low pointwise error conceal instability or closure failure? |
| Provenance/data | Bind producer patches/build/run/raw/derived/transform/model. Are trial/accepted/NSE/interval semantics explicit? Is leakage possible across related cases? Can missing or failed records appear successful? |
| Performance/operations | Match accuracy, inputs and horizon. Include failed runs and solver/transformation overhead. Was the requested hardware/configuration actually used? Are budgets, portability limits and reproducible timing stated? |

## Focused repair review brief

```text
Prior [SHA] → replacement [SHA]; originating findings [IDs].
Model / reasoning effort / availability: [explicit]. Model policy: D-012 link above.
Escalation justification / bounded deliverable / effort / stop: [N/A or explicit].
Lead verification/integration / actual outcome / remaining uncertainty: [record].
Independently verify the stated fixes, their tests and material repair risks.
Inspect the delta and relevant unchanged context. Confirm final-candidate
coverage, or identify an additional risk requiring broader review. Preserve
original findings and report their verification separately from new findings.
```

## External audit brief

Use the portable packet and upload rules in [WORKFLOW](WORKFLOW.md#independent-external-audits). Ask Claude/Gemini (when available and authorized) to evaluate the same claims without implementation advocacy. Return evidence-backed findings and limitations, not a numerical confidence score substituting for validation. Record availability honestly; an audit can remain deferred without pretending it occurred.
