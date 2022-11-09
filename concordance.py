"""Determine classifier concordance for some seeds."""

import os
import re
import click
import torch
import slideflow as sf

from typing import List
from slideflow.gan.interpolate import StyleGAN2Interpolator

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
@click.option('--out',         help='Where to save results (csv)', metavar='PATH', default='concordance.csv')
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
    trunc,
    noise_mode
):
    """Determine classifier concordance for some seeds."""

    # Initial preparation.
    device = torch.device('cuda')
    classifier_cfg = sf.util.get_model_config(classifier)
    interpolator = StyleGAN2Interpolator(
        network,
        target_px=classifier_cfg['tile_px'],
        target_um=classifier_cfg['tile_um'],
        start=start,
        end=end,
        truncation_psi=trunc,
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

    # Save results to csv.
    df[['seed', 'pred_start', 'pred_end', 'concordance']].to_csv(out)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()