# Experiment 045 — Sample-Split Symmetry E-Process Confirmation

Prospectively frozen before any Experiment-045 outcomes.

The operative scientific contract is GitHub issue #115. Experiment 045 separates discovery from confirmation and tests one frozen topology candidate with a nonnegative sign-symmetry betting process on disjoint later probe responses.

Discovery uses round 1 only with baseline slice B1=181..184. Confirmation rounds 2..5 use B2=185..188, B3=189..192, B4=193..196, B5=197..200 respectively. For each round r, D_r(i,j) is the target-j probe mean observed by i minus the matching baseline-slice mean. Discovery selects exactly one edge by maximum S_ij=D_1(i,j)+D_1(j,i), lexical tie-break ab<ac<bc, and never accepts or reselects.

For the two directed responses of the frozen edge in rounds 2..5, each factor is m(x)=1+sgn(x)*tanh(|x|/0.05), with inherited SIGMA_PROBE=0.05 and sgn(0)=0. Starting from E=1, multiply factors sequentially. Confirm at the first round with cumulative E>=100; otherwise abstain after round 5 and use exact triad fallback. Threshold 100 is frozen from the 1% single-hypothesis risk budget via Ville's inequality.

Deployment: Experiment-031 causal context composition through Experiment-032 after confirmation; inherited primary-fault veto; exact fallback; unchanged operational adaptation and probe amplitudes. No Gaussian-posterior acceptance threshold is used for Experiment-045 confirmation.

Evaluation: Gaussian, Laplace, Student-t3, contaminated-Gaussian; gain 0.50/0.425 x noise scale 1.00/1.50; H_ab drift/fault magnitude 0.50; 16 cells; seeds 45000..45999; audit 45000..45004; bootstrap seed 45045.

Frozen H1-H13 and interpretation rule are exactly those in issue #115. No tuning of the split, discovery score, betting function, or E>=100 threshold from Experiment-045 outcomes is permitted.