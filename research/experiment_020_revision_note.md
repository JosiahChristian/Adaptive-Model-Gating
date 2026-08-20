# Experiment 020 — Pre-outcome Specification Correction

The first prospective Experiment-020 specification was committed at `2ac9ce07e35fd4d77a5029ccf80b0a5aa9c77916` before any Experiment-020 outcomes were generated.

During implementation review, before any calibration/evaluation execution, an internal design inconsistency was identified: the draft required an early two-target round-4 intervention followed, on failure, by execution of the omitted third target while also requiring the reconstructed round-4 response matrix to be numerically identical to an independently executed Experiment-019 comparator. Because diagnostic noise is time-indexed and the omitted intervention would necessarily occur at a different time, exact numerical equality to the inherited Experiment-019 round-4 matrix cannot be guaranteed.

No Experiment-020 calibration values, evaluation seeds, cell results, coverage values, losses, or scientific outcomes were observed before discovering this issue.

Therefore the `2ac9ce...` specification is superseded pre-outcome. The corrected prospective specification removes the impossible exact-reconstruction claim and instead preregisters an explicit continuation rule using the actually observed late third block, with Experiment 019 retained as a separate comparator. The correction does not use outcome information.
