# Experiment 016 evidence record

Experiment 016 is scientifically complete. The original requested Actions run `32297896865` completed its unit/smoke gate, all twenty-two frozen shards, deterministic merge, and upload of `experiment-016-evidence`; its final bookkeeping step failed only because the workflow attempted to embed the full report in a GitHub Issue body exceeding GitHub's 65,536-character limit. Registration was recovered without a scientific rerun in issue #19.

## Provenance

- Frozen request head: `cf80d0c3caf92b7c2eedab39139327f29c4185f5`
- Evidence artifact ID: `9383941011`
- Artifact size: `230600081` bytes
- Artifact SHA-256: `d67a32d062efcae2979d0828d7029d8b59632cdf6406a54696d7633a6000601b`
- Coverage: 22 cells x 11 strategies x 200 evaluation seeds = 48,400 seed summaries
- Audit trace: 22 x 11 x 5 audit seeds x 900 evaluated steps = 1,089,000 rows
- Evaluation seeds: `16000..16199`
- Bootstrap seed: `16016`

## Bounded result

Sequential intervention retained oracle-equivalent behavior in the fully responsive A/B-fault regime while reducing mean probe energy from 0.6000 for the fixed maximum probe to approximately 0.23869 (about 60.2%). Early operational-loss differences versus naive three-anchor voting were approximately -2.21, -17.42, and -70.13 as fault magnitude increased, with the preregistered intervals below zero.

The result is not universal. At diagnostic gain 0.50, provenance recovery fell to about 86% and sequential probing often escalated, increasing mean energy to approximately 0.70688. At gain 0.25, recovery fell to about 13%; the sequential method exhausted the available ladder and became effectively the maximum-probe strategy, with excess early loss versus the oracle reaching approximately +61.67 at magnitude 1.0. Coherent corruption of all auxiliary evidence remained unresolved, with approximately +78.14 excess early loss at magnitude 1.0.

The supported claim is therefore narrow: bounded sequential intervention can reduce diagnostic cost when provenance is sufficiently observable, but a finite probe budget cannot create identifiability under severe response attenuation and does not resolve coherent compromise of all auxiliary evidence.

## Execution lesson

Evidence registration is not part of the scientific estimand. Future requested workflows must use bounded issue bodies that point to the full artifact/report rather than embedding the full report. A registration failure after successful merge/upload must be recoverable without rerunning scientific evaluation.
