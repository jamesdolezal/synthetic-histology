"""Train a GAN using a predetermined experiment configuration."""

import click
import slideflow as sf

from os.path import abspath, dirname
from utils import prepare_project, resolve_relative_paths, EasyDict

# -----------------------------------------------------------------------------

@click.command()
@click.option('--outdir',   help='Where to set up the project',  metavar='DIR',  required=False)
@click.option('--exp',      help='Experiment configuration',     metavar='PATH', required=True)
@click.option('--download', help='Download slides from TCGA',    metavar=bool,   default=False, is_flag=True)
@click.option('--md5',      help='Verify slide integrity via MD5 hash.',  metavar=bool, default=False, is_flag=True)
def main(outdir, exp, download, md5):
    """Train a GAN using a predetermined experiment configuration."""

    # --- Project initialization ----------------------------------------------

    # Load experiment configuration.
    cfg = EasyDict(sf.util.load_json(exp))
    cfg = resolve_relative_paths(cfg, dirname(exp))
    if outdir is None:
        outdir = abspath(cfg.name)
    P = prepare_project(outdir, cfg=cfg, md5=md5, download=download)


    # --- Tile extraction -----------------------------------------------------
    print("Extracting tiles...")
    dataset = P.dataset(tile_px=cfg.tile_px, tile_um=cfg.tile_um)
    dataset.extract_tiles(**cfg.tile_kwargs)

    # --- GAN training --------------------------------------------------------
    print("Initializing GAN training...")
    P.gan_train(
        dataset=dataset,
        outcomes=cfg.outcome,
        **cfg.gan_kwargs
    )

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()