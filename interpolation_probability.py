"""Plot a probability map of classifier predictions during interpolation."""

import os
import re
import click
import torch
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import slideflow as sf

from os.path import join
from typing import List
from slideflow.gan.interpolate import StyleGAN2Interpolator

# Allow GPU memory growth, so Tensorflow & PyTorch can play nice
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

# -----------------------------------------------------------------------------

def num_range(s: str) -> List[int]:
    '''Accept either a comma separated list of numbers 'a,b,c' or a range 'a-c' and return as a list of ints.'''

    if os.path.exists(s):
        with open(s, 'r') as f:
            return [int(i) for i in f.read().split('\n')]
    else:
        range_re = re.compile(r'^(\d+)-(\d+)$')
        m = range_re.match(s)
        if m:
            return list(range(int(m.group(1)), int(m.group(2))+1))
        vals = s.split(',')
        return [int(x) for x in vals]

# -----------------------------------------------------------------------------

@click.command()

# Networks and outcome.
@click.option('--out',         help='Where to save results (image path)', metavar='PATH', default='interp_prob.png')
@click.option('--network',     help='Network pickle filename',     metavar='PATH', required=True)
@click.option('--classifier',  help='Path to trained classifier',  metavar='PATH', required=True)
@click.option('--outcome_idx', help='Index of the target outcome', metavar=int,    default=1)

# Concordance thresholds.
@click.option('--thresh_low',  help='Lower end of concordance threshold', metavar=float, default=0.25, show_default=True)
@click.option('--thresh_mid',  help='Concordance threshold midpoint',     metavar=float, default=0.5,  show_default=True)
@click.option('--thresh_high', help='Upper end of concordance threshold', metavar=float, default=0.75, show_default=True)

# Additional options.
@click.option('--seeds', help='List of random seeds', type=num_range, default=range(1000))
@click.option('--start', help='Starting category for interpolation.', type=int, default=0)
@click.option('--end',   help='Ending category for interpolation.', type=int, default=1)
@click.option('--trunc', 'truncation_psi', type=float, help='Truncation psi', default=1, show_default=True)
@click.option('--noise-mode', help='Noise mode', type=click.Choice(['const', 'random', 'none']), default='const', show_default=True)
def main(
    out,
    network,
    classifier,
    outcome_idx,
    thresh_low,
    thresh_mid,
    thresh_high,
    seeds,
    start,
    end,
    truncation_psi,
    noise_mode
):
    """Plot a probability map of classifier predictions during interpolation."""

    # Initial preparation.
    device = torch.device('cuda')
    classifier_cfg = sf.util.get_model_config(classifier)
    interpolator = StyleGAN2Interpolator(
        network,
        target_px=classifier_cfg['tile_px'],
        target_um=classifier_cfg['tile_um'],
        start=start,
        end=end,
        truncation_psi=truncation_psi,
        noise_mode=noise_mode,
        device=device
    )

    # Perform classifier concordance search.
    interpolator.set_feature_model(classifier)
    df = interpolator.seed_search(
        seeds,
        outcome_idx=outcome_idx,
        concordance_thresholds=[thresh_low, thresh_mid, thresh_high]
    )
    print("Percent none:   ", len(df.loc[df.concordance == 'none']) / 10)
    print("Percent weak:   ", len(df.loc[df.concordance == 'weak']) / 10)
    print("Percent strong: ", len(df.loc[df.concordance == 'strong']) / 10)

    # Interpolate for classifier-concordant seeds.
    preds_by_seed = dict()
    for seed in df.loc[df.concordance.isin(['strong', 'weak'])].seed.unique():
        raw, processed, preds = interpolator.interpolate_and_predict(
            int(seed),
            outcome_idx=outcome_idx
        )
        preds = np.array(preds)
        preds_range = preds.max() - preds.min()
        preds_norm = (preds - preds.min()) / preds_range
        preds_by_seed[seed] = preds_norm
    seeds = np.array(list(preds_by_seed.keys()))
    preds = np.stack(list(preds_by_seed.values()))

    # Prepare results for plotting.
    all_seeds = list(seeds) * preds.shape[1]
    all_preds = []
    iteration = []
    for s in range(preds.shape[1]):
        all_preds += list(preds[:, s])
        iteration += [s] * preds.shape[0]
    prob_df = pd.DataFrame({
        'seed':all_seeds,
        'pred':all_preds,
        'iteration': iteration
    })

    # Plot.
    plt.clf()
    plt.grid(visible=True, which='both', axis='both', color='white')
    plt.gca().set_facecolor('#EAEAF2')
    sns.lineplot(x='iteration', y='pred', ci="sd", data=prob_df)
    sns.lineplot(x='iteration', y='pred', err_style='bars', data=prob_df)
    plt.savefig(out)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()