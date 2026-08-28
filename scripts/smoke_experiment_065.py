from __future__ import annotations

import sys
sys.path.insert(0, 'src')

import experiment_065 as e

# Nonreserved smoke only: 6540000..6540005 is outside every #258
# DQ/DP development range (6500000..6513999) and every untouched
# VQ/VP validation range (6514000..6534999).
for i, panel in enumerate(('DQ1', 'DQ2', 'DQ3', 'DQ4', 'DQ5', 'DQ6')):
    seed = 6540000 + i
    row = e.evaluate_robustness_draw(panel, seed, start=6540000)
    assert row['panel'] == panel
    assert row['seed'] == seed
    assert row['q_family'] == f'Q{i + 1}'
    assert set(row['underlying_accept']) == set(e.ARCHITECTURES)
    expected_all = int(all(row['underlying_accept'][a] == 1 for a in e.ARCHITECTURES))
    expected_m0 = int(expected_all and row['topology_agreement'])
    assert row['all_four_accept'] == expected_all
    assert row['m0_accept'] == expected_m0

assert e.provenance_integrity()
print('Experiment 065 nonreserved M0 smoke passed; no DQ/DP/VQ/VP reserved seed executed.')
