# Experiment 014 audited evidence

Status: completed frozen evaluation. This record does not alter the prospective specification.

- Workflow run: `32282064364`
- Evaluated head: `6dd00278f69c10a03b6ca352bf5db180bfa0ce4b`
- Artifact: `experiment-014-evidence`, id `9377973659`
- Artifact SHA-256: `b4ad8446ce9d560d307f8d671be377910f75be2b1e4b4055d768c18257c13ed5`
- Gate: unit tests and `scripts/smoke_experiment_014.py` passed before the matrix.
- Execution: all 22 frozen cell shards and deterministic merge/evaluate job passed.
- Coverage independently audited from the artifact: 44,000 seed summaries = 22 cells x 10 strategies x 200 seeds; exactly 200 evaluation seeds `14000..14199`.
- Dependence calibration: seeds `1400..1599`, disjoint from evaluation; frozen `lambda_dep = 0.20140041216204912`; bootstrap seed `14014`.

## Result boundary

The simple pre-event residual-correlation partition learner is not a reliable replacement for trusted provenance. Under the intended A/B dependence signature, exact partition recovery was only 0.21. When that signature was absent it fell to 0.005, under a misleading B/C signature it was 0.01, and in the all-auxiliary common-cause cell it was 0.0.

Despite poor partition recovery, the learned gate sometimes improved on naive sensor-count quorum in the intended A/B-fault family: paired early operational-loss differences (learned minus naive) were -0.381, -3.247, and -13.115 for magnitudes 0.25, 0.5, and 1.0, with all three frozen bootstrap intervals below zero. This is a mechanism-specific benefit, not evidence that the learned partition is generally correct.

The negative boundaries are strong. With the A/B dependence signature removed, learned-minus-oracle early loss was +2.048, +16.827, and +72.339. Under the misleading B/C signature it was +2.060, +16.138, and +69.333 versus oracle (and identically versus triad persistence in these cells). With all auxiliary channels coherently corrupted, learned-minus-triad loss was +2.237, +18.461, and +82.935. All corresponding frozen bootstrap intervals were strictly positive.

Common-mode primary-input protection remained favorable versus triad persistence in final slope error at all three magnitudes: mean paired differences -0.0400, -0.0260, and -0.0637, with the 95% intervals below zero (the 0.5 interval narrowly excludes zero).

## Bounded claim

Observable pre-event dependence can carry useful gating information, but this frozen three-anchor correlation-threshold learner does not identify failure-domain provenance robustly enough to replace trusted structural metadata. The result strengthens the distinction between *evidence redundancy* and *identifiable independence*: a dependence signature can help when it is present and correctly aligned, but provenance is not generally recoverable from one short observational regime by thresholded pairwise correlation alone.
