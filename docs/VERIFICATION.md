# Phase 0B verification accounting

Shared D-011 cap: 7,200 CPU-seconds (2 CPU-hours), local plus CI. Maximum 10 minutes per CI job, 1 GiB per test process, 100 MiB generated test scratch excluding environments/caches. Prefer measured CPU; otherwise charge elapsed time × allocated cores, including workers. No GPU/training/bulk-data/HPC or paid service. Human waiting and agent reasoning are not compute runs.

| Run | Check / estimate before launch | Actual result / accounting |
| --- | --- | --- |
| Startup | Read-only inventory, file preservation, documentation preparation and destination/auth inspection; no software tests | 10 CPU-seconds reserved conservatively for sub-second local commands; network waits excluded. No CI. |
| B01 seed check (planned) | Preservation hashes, archive members, portable links/anchors and public-file screening; <= 10 CPU-seconds, one process; < 1 MiB output | PASS: 21 preserved files, archive digest/14 members, 22 allowlisted files, 114 local links/28 anchors, no screening errors. Measured 0.0155 CPU-s; conservatively charged 10 CPU-s including final post-confirmation check |
| Read-only tooling investigation | <= 60 CPU-seconds allocated to investigator; no test runs or installation | Complete; five inspection commands ~0.79 s shell wall on 16 logical CPUs, rounded up to **20 CPU-seconds**; no tests/installations |

Current conservative charge/reservation: **40 / 7,200 CPU-seconds**. No independent review round has been consumed. Next software/CI run requires a new estimate and ledger row. CI accounting must include runner core count and full job elapsed time when CPU measurements are unavailable. Stop before caps are exceeded; budget exhaustion never establishes acceptance.
