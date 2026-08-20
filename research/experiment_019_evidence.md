# Experiment 019 — Completed Evidence

**Status:** completed frozen evaluation; central adaptive-confirmation-efficiency claim supported.

## Provenance

- Prospective scientific freeze: `81cc36c19e82e8ddd4f89bcfa6b6eabcf63c0f83`
- Successful hardened evaluation head: `f0ad1d55326076a2ee50c581cf6d3d6ce70dcb3f`
- GitHub Actions run: `32343025180`
- Artifact: `experiment-019-evidence`
- Artifact size: `390510066` bytes
- Artifact SHA-256: `85ab04a209d60e55680b05e7dab62c590ee00a0caff9dee87e93971ed3d8d383`
- Evaluation seeds: `19000..19199`
- Targeted calibration seeds: `4000..4999`

## Frozen criteria

All preregistered H1–H6 criteria pass. H7 remains the explicitly unsolved coherent-all-auxiliary truth-identifiability boundary.

### H1 / C1 — moderate-gain efficiency: PASS

At all three `g_probe=0.50` A/B-fault magnitudes:

- targeted coverage: `0.995`
- Experiment-018 full-confirmation coverage: `0.920`
- coverage gap targeted minus full: `+0.075`
- accepted precision: `1.000`
- wrong acceptance: `0.000`
- targeted-minus-full early-loss difference: `0.000`, paired-bootstrap CI `[0.000, 0.000]`
- adaptation gap versus `triad_persistence`: `0.000`
- mean targeted energy: `0.923875`
- targeted-minus-full mean energy: `-0.068000`

Thus the central efficiency claim passes both required components: coverage is not degraded and diagnostic energy is reduced by more than the frozen minimum.

### H2 / C2 — standard-gain preservation: PASS

At all three `g_probe=1.00` A/B-fault magnitudes:

- coverage `1.000`
- precision `1.000`
- wrong acceptance `0.000`
- mean energy `0.362625`
- adaptation gap versus triad `0.000`

### H3 / C3 — selector validity: PASS

At `g_probe=0.50`, targeted round 5 executes in `0.340` of seeds and the selected edge is physically correct in `1.000` of entered seeds, exceeding the frozen `0.80` requirement.

### H4 / C4 — attenuation safety: PASS

At `g_probe=0.375`, targeted coverage is `0.880`, precision `1.000`, wrong acceptance `0.000`, and targeted-minus-triad early-loss CI is `[0.000,0.000]`.

At `g_probe=0.25`, targeted coverage is `0.300`, precision `1.000`, wrong acceptance `0.000`, and targeted-minus-triad early-loss CI is `[0.000,0.000]`.

At `g_probe=0.125`, targeted coverage is `0.010`, abstention `0.990`, precision among accepted decisions `1.000`, wrong acceptance `0.000`, and targeted-minus-triad early-loss CI is `[0.000,0.000]`.

### H5 / C5 — legitimate-drift non-destruction: PASS

For all genuine-drift magnitudes, targeted relative excess early loss versus triad is exactly `0.000` with CI `[0.000,0.000]`, and adaptation gap is `0.000`.

### H6 / C6 — fault regression protection: PASS

For all common-mode and primary-only fault magnitudes, targeted-minus-full final coefficient-error difference is `0.000` with CI `[0.000,0.000]`.

### H7 / C7 — coherent-all-auxiliary boundary: UNSOLVED BY DESIGN

The targeted strategy still accepts the provenance partition in coherent-all-auxiliary cells, but this does not establish truth identifiability. Relative to triad, mean early-loss increases are approximately `2.618`, `18.135`, and `76.528` for magnitudes `0.25`, `0.50`, and `1.00`, respectively, with strictly positive bootstrap intervals. This boundary remains explicit and must not be interpreted as solved by provenance confidence.

## Scientific conclusion

Experiment 019 supports the preregistered central claim: after four rounds fail to qualify, the round-4 reciprocal scores contain sufficient directional information to focus confirmation on two targets. Adaptive edge-targeted confirmation improves moderate-gain coverage relative to full three-target confirmation while reducing diagnostic energy, without degrading precision, legitimate drift behavior, attenuation safety, or inherited common-mode/primary-fault protections.

The result motivates a new prospective question: whether the edge can be selected one round earlier, allowing a two-target round-4 challenge to qualify easy cases while retaining an exact path back to the fully observed round-4 state and inherited Experiment-019 behavior when early targeting is insufficient.
