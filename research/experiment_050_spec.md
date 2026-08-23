# Experiment 050 — Doubled Confirmation Replicate with Exact 40-Sign 1% Binomial E-Variable

Prospectively frozen before any Experiment-050 outcomes.

The operative scientific contract is GitHub issue #145. Experiment 050 tests whether doubling the held-out confirmation information budget can recover useful coverage after Experiment 049 established that the inherited 20-sign budget is safe but information-limited.

Discovery is inherited unchanged from Experiment 047 and uses only the primary stream: five rounds, amplitudes `(0.025, 0.050, 0.100, 0.200, 0.200)`, frozen discovery indices, six-direction covariance-matched profile selection, lexical tie-break, and immutable candidate.

For primary evaluation seed `s`, the confirmation-only replicate is generated under the identical frozen cell with seed `s + 5,000,000`. Replicate values are forbidden from discovery, context, adaptation, comparator policies, and fallback. Each round contributes four Experiment-049 pairwise signs from the primary stream and four from the independent replicate, for exactly 40 confirmation signs.

The terminal rule is frozen exactly: `S >= 28`, where `S` is the positive-sign count. Under `Binomial(40, 1/2)`, `p28 = 9119901052 / 1099511627776 = 0.008294501687487355`; `p27 = 21153123932 / 1099511627776 = 0.01923865414210013`. The terminal e-variable is `1/p28 = 120.56179354433637` on `S >= 28`, otherwise zero, with the inherited `E >= 100` decision boundary.

Resource accounting is explicit: the confirmation replicate adds a second five-round diagnostic measurement/probe exposure. This is not an equal-budget comparison to Experiment 049.

Deployment on the primary stream remains frozen: wrong-action cost 100, fallback cost 1, Experiment-031 current-time causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged adaptation logic and calibration constants.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain `{0.50, 0.425}` x noise scale `{1.00, 1.50}`; H_ab drift/fault magnitude 0.50; 16 cells; primary seeds `50000..50999`; replicate seeds `5050000..5050999`; audit primary seeds `50000..50004` plus mapped replicates; bootstrap seed `50050`.

Frozen H1-H16 and the interpretation rule are exactly those in issue #145. No seed-map, sample-count, pairing, sign-cutoff, score, or threshold tuning from Experiment-050 outcomes is permitted.
