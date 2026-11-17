# Genesis card guidance evidence

Retrieved 2026-11-17 for [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10).
Investigation: `gpt-6.1-sol` High, read-only; lead inspected the released template.
These are guidance sources, not data-release permission or scientific acceptance.

The [DOE ModCon page](https://www.energy.gov/undersecretaryforscience/genesis-mission/modcon-transformational-ai-and-data)
(page updated 2026-10-23) recommends early cards for datasets at every publication
and sensitivity stage. It distinguishes dataset, model and agent documentation.
The maintainer-supplied [OSTI presentation 3426874](https://www.osti.gov/biblio/3426874),
dated 2026-08-19, DOI `10.2172/3426874`, was inspected including rendered PDF pages
15–16, 26–27, 32 and 34. Its [PDF](https://www.osti.gov/servlets/purl/3426874)
SHA-256 is `7002d527dedd1bdcc03224bdf60b319155b62a63e4b47adc5e08e0412da991ad`.

## Actual released template

The presentation links [OSTI release 3376151](https://www.osti.gov/biblio/3376151),
DOI `10.18141/3376151`, and the [official NETL EDX release](https://edx.netl.doe.gov/dataset/genesis-data-card-schema-template-and-supporting-tools).
The [v2.0.0 archive](https://edx.netl.doe.gov/storage/f/edx/2026/10/2026-10-01T15:47:52.944911/9fd0a191-70ea-42c6-aeb9-c22c8a969700/data-cards-v2.0.0.zip)
was uploaded 2026-10-01; EDX metadata was modified 2026-10-07. Its MD5 matches
the resource's published checksum, `86e11bc27a6739ebe796dda74732de7a`.

| Retrieved artifact | SHA-256 |
| --- | --- |
| Release ZIP | `3a2aedd1e42bc3b71da01f1b02f846dd6ef1722b3a1a6f43e937677d4a40dd67` |
| `template/latest/template/genesis_datacard_merged_shared.md` | `def450cfeec669bf849d9fe0b03c2f3b2ae60bde8cc1d8c0ab04aed868b1e953` |
| Companion LinkML schema | `ac62025933859944c38185e866e2966ed4f907f5dcc7b8a972cb716fe2b2f6a8` |

The archive includes the actual Markdown/YAML templates, schema, field guide,
CEBAF worked example and capability-specific examples. Both template banner and
schema identify version **2.0.0**. This pins the inspected release; it does not
establish the inaccessible GitLab `main` revision or that this is the newest release.

The template combines YAML metadata with six adaptable narrative sections and a
capability snapshot. Its instructions allow answering relevant narrative questions
selectively. Its capabilities describe intended support, not a scientific grade.
Discoverability is mandatory in a machine-valid card; five further capability
flags activate additional required field groups. Card and dataset sensitivity,
card/template/dataset versions, workflow state and publication status are distinct.
Unknown information must not be replaced with a claim that it does not apply.

The initial CRUCIBLE [raw-collection card](../data-cards/genesis_datacard_ccsn_raw_candidate.md)
uses that narrative structure as a **living draft**, explicitly recording missing
ownership, rights and provenance. It is not submitted to a catalog and does not
claim full YAML/schema conformance or machine validation. Finish the required
metadata and validate against this pinned schema before making such a claim;
do not invent governance determinations to make a validator pass. Derived dataset
cards will link their exact parents, extraction and qualification separately.

One release inconsistency matters when adding machine metadata: narrative tags
use `training_use_allowed`/equivalents, but schema/YAML use `training_use_status`,
`inference_use_status`, `evaluation_use_status`, with `Yes`/`No`/`Conditional`
and conditional-use descriptions. Follow the pinned schema rather than obsolete
prose keys. No metadata framework or registry is introduced here.

## Access gaps and model-card timing

The requested [template tree](https://gitlab.osti.gov/genesis/data-cards/-/tree/main/template),
[examples tree](https://gitlab.osti.gov/genesis/data-cards/-/tree/main/examples)
and [BPSW model-card template](https://gitlab.osti.gov/genesis/modcon-bpsw/-/blob/main/cards/templates/model-card.md)
redirected anonymous direct reads to sign-in. Raw requests did too; anonymous
project API requests returned 404. The older GitLab location in the presentation
also failed (API 404/raw 403). Thus **the requested current GitLab commits and
actual BPSW model-card template remain unverified**. The official released data
template was recovered through EDX; its access gap is resolved for v2.0.0 only.

The separate DOE-linked discovery registry examples are not substituted for the
BPSW model-card template. Phase 2 must retrieve that actual guidance or record
the specific continuing gap, and bind a card to the actual model, training
data/split, evaluation and limitations. No trained model/performance or agent
card is fabricated during Phase 1. External Claude/Gemini advisory audit is
deferred until there is a scientific data-contract qualification candidate;
no external endorsement is claimed.
