# Experiment 001 Evidence Record

## Provenance

- Workflow: `Experiment 001`
- GitHub Actions run: `32100558557`
- Producing commit: `d988221879790fe8e896179f1364c021da6067ab`
- Artifact: `experiment-001-evidence`
- Artifact ID: `9311469065`
- GitHub-recorded artifact SHA-256: `3e35abdf79b3476ca1ce63a28f31b4a2b2e6e1d572810b8391ac44ef8cf8c349`
- Downloaded artifact SHA-256 independently verified equal to the GitHub digest.

Contained files and SHA-256 values:

- `report.json` — `7374dcd3be857b6552329f4aec86b692dc383ece457ca28e2cc07c0055f6fb78`
- `seed_summary.csv` — `293071f8e95cd30eae19086682a0e36c5f8d3452e460577367d896a05abf2abb`
- `trace.csv` — `c3d264c51764bc983802cbe0e7e99ad6896beca47ff106a81ba5adc69b36d2b3`

The full trace is large and remains in the Actions evidence artifact. The compact report is committed in this directory. The experiment is deterministically regenerable from the producing revision and frozen seeds.

## Frozen calibration result

- Rolling-MSE threshold `tau`: `0.4749575582753968`
- Evaluation seeds: `1000..1199`
- Independent streams per condition: `200`

## Primary evidence

Persistent-condition mean cumulative squared loss over `t=401..600`:

- Frozen: `84.92151614740324`
- Continuous: `56.67675177174851`
- Threshold: `62.61675131928025`
- Persistence-aware: `63.91505222821736`

Transient-condition probability of at least one adaptation during the 20-step matched event:

- Frozen: `0.000`
- Continuous: `1.000`
- Threshold: `0.395`
- Persistence-aware: `0.285`

## Paired seed-level audit

Using 10,000 whole-seed bootstrap resamples of the preserved seed summary:

- Persistence minus threshold transient-adaptation-rate difference: `-0.110`
- 95% paired seed-bootstrap CI: `[-0.155, -0.070]`

- Persistence minus threshold persistent-loss difference: `+1.2983`
- 95% paired seed-bootstrap CI: approximately `[+1.03, +1.59]`

Additional persistent-loss contrasts:

- Persistence minus frozen: `-21.0065`, 95% paired bootstrap CI approximately `[-22.40, -19.62]`
- Persistence minus continuous: `+7.2383`, 95% paired bootstrap CI approximately `[+6.70, +7.81]`

Persistent-condition first-adaptation delay:

- Continuous: mean `0` steps
- Threshold: mean `40.145` steps; median `25`
- Persistence-aware: mean `46.71` steps; median `32`

For the transient-event primary indicator, all 22 discordant threshold-versus-persistence seeds were cases in which threshold adapted and persistence did not; there were no seeds in which persistence adapted during the event while threshold did not.

## Current evidence status

Experiment 001 demonstrates a real tradeoff in this controlled system rather than an unqualified winner.

Relative to the simple threshold gate, persistence confirmation reduced adaptation during a temporary matched-onset change by 11 percentage points, but increased cumulative loss after persistent drift by about 1.30 squared-error units over the frozen 200-step horizon. Both paired intervals exclude zero under the prespecified seed-level resampling unit.

Continuous adaptation produced the lowest persistent-drift loss among the four tested strategies, but by construction adapted throughout every transient stream. The frozen model avoided all adaptations but incurred substantially greater persistent-drift loss.

The result therefore supports continued study of the responsiveness-versus-unnecessary-adaptation tradeoff. It does not establish general superiority of persistence gating.

## Important limitation exposed by Experiment 001

Across the long post-event period, repeated opportunities to cross a 99th-percentile rolling-loss threshold produced substantial adaptation occurrence even in stable streams. In the preserved seed summary, at least one post-event adaptation occurred in approximately 78% of stable threshold-gate streams and 58.5% of stable persistence-gate streams. This is not a violation of the preregistered primary endpoint, but it is important evidence that long-horizon false-alarm accumulation must be made explicit in follow-on studies.
