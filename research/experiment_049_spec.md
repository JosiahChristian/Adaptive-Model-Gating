# Experiment 049 — Doubled Disjoint Sign Confirmation

Prospectively frozen before any Experiment-049 outcomes.

The operative scientific contract is GitHub issue #136. Experiment 049 tests whether confirmation power can be recovered by extracting two disjoint target-minus-baseline sign contrasts per selected direction per round from the already held-out confirmation samples, while preserving Experiment-047 covariance-matched discovery and an exact nonrandomized 1% symmetry-valid terminal decision.

Frozen discovery is unchanged from Experiment 047/048. Confirmation uses the first two held-out target samples paired chronologically with the two held-out baseline samples for each selected direction; the third held-out target sample is unused. This yields exactly 20 signs across five rounds. Let S be the number positive. Freeze p16=P(Bin(20,1/2)>=16)=6196/1048576=0.005908966064453125 and terminal E=1{S>=16}/p16. Retain E_THRESHOLD=100, so acceptance is exactly S>=16. No magnitude, randomization, fitted parameter, pairing change, threshold tuning, or observation reuse is permitted.

Deployment remains frozen: wrong-action cost 100, fallback cost 1, Experiment-031 causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged probe schedule/amplitudes and calibration constants, and full five-round latency.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain {0.50,0.425} x noise scale {1.00,1.50}; H_ab drift/fault magnitude 0.50; 16 cells; seeds 49000..49999; audit 49000..49004; bootstrap seed 49049.

Frozen H1-H15 and interpretation rule are exactly those in issue #136. Any failure is preserved. No Experiment-049 outcome may be inspected before implementation and preflight are frozen.

Preflight trigger marker: implementation/specification only; no Experiment-049 evaluation has been requested.