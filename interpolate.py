"""Generate images using pretrained network pickle."""

import os
import re
from os.path import join
from typing import List, Optional

import click
import torch
from PIL import Image

from slideflow.gan.stylegan3.stylegan3 import embedding, utils

#----------------------------------------------------------------------------

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

#----------------------------------------------------------------------------

@click.command()
@click.pass_context
@click.option('--network', 'network_pkl', help='Network pickle filename', required=True)
@click.option('--seeds', type=num_range, help='List of random seeds')
@click.option('--start', type=int, help='Starting category for interpolation.')
@click.option('--end', type=int, help='Ending category for interpolation.')
@click.option('--trunc', 'truncation_psi', type=float, help='Truncation psi', default=1, show_default=True)
@click.option('--noise-mode', help='Noise mode', type=click.Choice(['const', 'random', 'none']), default='const', show_default=True)
@click.option('--outdir', help='Where to save the output images', type=str, required=True, metavar='DIR')
@click.option('--video', help='Save in video (MP4) format.', default=False, show_default=True, type=bool, metavar='BOOL')
@click.option('--steps', help='Number of interpolation steps.', type=int, default=100, show_default=True)
@click.option('--merge', help='Merge images side-by-side.', type=bool, default=False, show_default=True)
def save_interpolation(
    ctx: click.Context,
    network_pkl: str,
    seeds: Optional[List[int]],
    start: Optional[int],
    end: Optional[int],
    truncation_psi: float,
    noise_mode: str,
    outdir: str,
    video: bool,
    steps: int,
    merge: bool,
):
    """Generate images using pretrained network pickle."""

    if steps < 2:
        ctx.fail("Steps must be greater than 1.")

    os.makedirs(outdir, exist_ok=True)

    device = torch.device('cuda')
    gan_kw = dict(truncation_psi=truncation_psi, noise_mode=noise_mode)
    E_G, G = embedding.load_embedding_gan(network_pkl, device=device)
    embeddings = embedding.get_embeddings(G, device=device)

    # Generate images.
    for seed_idx, seed in enumerate(seeds):
        print('Generating image for seed %d (%d/%d) ...' % (seed, seed_idx, len(seeds)))
        z = utils.noise_tensor(seed, G.z_dim).to(device)

        # Set up interpolation generator
        generator = embedding.class_interpolate(E_G, z, embeddings[start], embeddings[end], device=device, steps=steps, **gan_kw)

        # Process interpolated images
        if video:
            video_path = join(outdir, f'seed{seed:04d}.mp4')
            print(f'Saving optimization progress video "{video_path}"')
            utils.save_video(list(generator), path=video_path)
        elif merge:
            out_path = join(outdir, f'seed{seed:04d}.png')
            print(f'Saving merged picture "{out_path}"')
            utils.save_merged(list(generator), path=out_path, steps=steps)
        else:
            for interp_idx, img in enumerate(generator):
                Image.fromarray(img).save(join(outdir, f'seed{seed:04d}-{interp_idx:03d}.png'))

#----------------------------------------------------------------------------

if __name__ == "__main__":
    save_interpolation() # pylint: disable=no-value-for-parameter

#----------------------------------------------------------------------------
