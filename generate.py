"""Generate images using pretrained network pickle."""

import re
import click
from typing import List

from slideflow.gan.stylegan3.stylegan3.generate import generate_images

#----------------------------------------------------------------------------

def num_range(s: str) -> List[int]:
    '''Accept either a comma separated list of numbers 'a,b,c' or a range 'a-c' and return as a list of ints.'''

    range_re = re.compile(r'^(\d+)-(\d+)$')
    m = range_re.match(s)
    if m:
        return list(range(int(m.group(1)), int(m.group(2))+1))
    vals = s.split(',')
    return [int(x) for x in vals]


class InvalidArgumentError(Exception):
    pass


@click.command()
@click.pass_context
@click.option('--network', 'network_pkl', help='Network pickle filename', required=True)
@click.option('--seeds', type=num_range, help='List of random seeds')
@click.option('--trunc', 'truncation_psi', type=float, help='Truncation psi', default=1, show_default=True)
@click.option('--class', 'class_idx', type=int, help='Class label (unconditional if not specified)')
@click.option('--noise-mode', help='Noise mode', type=click.Choice(['const', 'random', 'none']), default='const', show_default=True)
@click.option('--projected-w', help='Projection result file', type=str, metavar='FILE')
@click.option('--outdir', help='Where to save the output images', type=str, required=True, metavar='DIR')
@click.option('--format', help='Image format (png or jpg)', type=str, required=True)
@click.option('--save-projection', help='Save numpy projection with images', type=bool, default=False)
@click.option('--resize', help='Resize to target micron/pixel size.', type=bool, default=False)
@click.option('--gan-um', help='GAN image micron size (um)', type=int)
@click.option('--gan-px', help='GAN image pixel size', type=int)
@click.option('--target-um', help='Target image micron size (um)', type=int)
@click.option('--target-px', help='Target image pixel size', type=int)
def main(ctx, **kwargs):
    """Generate images using pretrained network pickle."""
    try:
        generate_images(**kwargs)
    except InvalidArgumentError as e:
        ctx.fail(e)

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter

#----------------------------------------------------------------------------
