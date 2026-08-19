# Experiment 011 — Completed Evidence Record

**Status:** completed frozen evaluation; bounded interpretation preserved.

## Provenance

- Completed GitHub Actions run: `32217582009`
- Evaluated head SHA: `0429e1268621152ca7d419945c7baec9679f81a7`
- Final artifact: `experiment-011-evidence`
- Artifact size: `74,414,754` bytes
- Artifact digest: `sha256:b545909e6cea664d5bc4519690e3c11ba2f936080155e6c8db80760e4c579807`
- Unit-test job: passed
- Thirteen frozen cell-shard jobs: passed
- Deterministic merge/evaluate job: passed

## Structural audit

Independent artifact inspection confirmed:

- `18,200` seed-strategy summaries = `13 cells × 7 strategies × 200 seeds`;
- evaluation seeds exactly `11000..11199`, contiguous and complete;
- each frozen cell contains exactly `1,400` summaries;
- all seven frozen strategies are present;
- audit trace contains exactly `409,500` rows = `13 cells × 7 strategies × 5 audit seeds × 900 evaluated time steps`;
- audit seeds exactly `11000..11004`;
- report records anchor calibration seeds `600..799`, disjoint from evaluation seeds;
- thresholds preserved as `tau=0.4749575582753968`, `kappa=0.004715841027139986`, `kappa3=0.008353014684419843`, and `lambda_anchor=0.019710908213588067`;
- downloaded artifact SHA-256 independently reproduced the registered GitHub digest exactly.

## Main scientific result

The structurally independent anchor breaks the specific Experiment 010 common-mode agreement ambiguity under the frozen healthy-anchor law. Relative to `triad_persistence`, `independent_persistence` reduced final absolute slope error in all three common-mode cells:

- magnitude `0.25`: mean paired difference `-0.0372508525`, 95% bootstrap CI `[-0.0528952190, -0.0217223162]`;
- magnitude `0.50`: mean paired difference `-0.0364048583`, 95% bootstrap CI `[-0.0636160404, -0.0096471676]`;
- magnitude `1.00`: mean paired difference `-0.0454356745`, 95% bootstrap CI `[-0.0813777020, -0.0126467473]`.

The independent path also satisfied the preregistered genuine-drift non-destruction criterion at all three drift magnitudes. The 95% bootstrap upper endpoints for mean relative excess early loss were approximately `0.00185`, `0.00157`, and `0.00137`, all far below the frozen `0.10` boundary.

Primary-only fault regression protection was preserved exactly relative to `triad_persistence`: the paired final-slope-error difference was `0.0` with CI `[0.0, 0.0]` at all three magnitudes.

The healthy control showed low false anchor activity: mean post-event anchor-mismatch fraction `0.009475`, common-mode-suspect fraction `0.0091375`, and only `0.015` mean independent vetoes per seed.

## Preserved negative finding

Experiment 011 also exposes a strong new trust boundary. When genuine physical drift occurs while the independent anchor is corrupted, the independent gate over-vetoes legitimate adaptation and materially worsens early operational loss relative to `triad_persistence`:

- magnitude `0.25`: `+2.3099207085`, 95% CI `[1.7650028939, 2.8927744513]`;
- magnitude `0.50`: `+17.7458148379`, 95% CI `[16.1794443549, 19.3520429385]`;
- magnitude `1.00`: `+81.6683573235`, 95% CI `[75.6525119441, 87.8485295998]`.

At magnitude `1.00`, adaptation by `t=420` fell from `0.85` under `triad_persistence` to `0.06` under `independent_persistence`.

## Bounded conclusion

Experiment 011 supports a narrow but meaningful claim: a structurally independent, trustworthy process-side observable can break the specified three-input common-mode identifiability limit without materially harming legitimate adaptation when the auxiliary source remains healthy.

It does **not** establish general sensor-fault robustness or trustworthy arbitration when the independent auxiliary source itself may fail. The experiment instead moves the limiting question from common-mode observability to **source-trust arbitration under conflicting evidence**.

The highest-value next falsification boundary is therefore whether multiple structurally diverse evidence sources, or an explicit source-reliability inference mechanism, can distinguish `common input-family corruption` from `auxiliary-source corruption` without latent truth and without recreating the over-veto failure demonstrated here.
