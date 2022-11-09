"""Train a GAN using a predetermined experiment configuration."""

import shutil
import tarfile
import click
import pandas as pd
import slideflow as sf

from os.path import join, basename, exists
from utils import download_slides, verify_md5, EasyDict

# -----------------------------------------------------------------------------

@click.command()
@click.option('--outdir',   help='Where to set up the project',  metavar='DIR',  required=True)
@click.option('--exp',      help='Experiment configuration',     metavar='PATH', required=True)
@click.option('--download', help='Download slides from TCGA',    metavar=bool,   default=False, is_flag=True)
@click.option('--md5',      help='Verify slide integrity via MD5 hash.',  metavar=bool, default=False, is_flag=True)
def main(outdir, exp, download, md5):
    """Train a GAN using a predetermined experiment configuration."""

    # --- Project initialization ----------------------------------------------

    # Load experiment configuration.
    cfg = EasyDict(sf.util.load_json(exp))

    # Initialize project in out directory.
    if sf.util.is_project(outdir):
        print(f"Project already configured at {outdir}")
        P = sf.Project(outdir)
    else:
        print(f"Setting up project at {outdir}")
        shutil.copy(cfg.annotations, outdir)
        P = sf.Project(outdir,
                       annotations=join(outdir, basename(cfg.annotations)))
        P.add_source(
            cfg.name,
            slides=join(outdir, 'slides'),
            roi=join(outdir, 'roi'),
            tiles=join(outdir, 'tiles'),
            tfrecords=join(outdir, 'tfrecords')
        )
        if 'rois' in cfg and cfg.rois:
            print(f"Extracting ROIs to {join(outdir, 'roi')}")
            roi_file = tarfile.open(cfg.rois)
            roi_file.extractall(join(outdir, 'roi'))

    # Read the TCGA manifest.
    try:
        df = pd.read_csv('experiments/gdc_manifest.tsv', delimiter='\t')
        slide_manifest = dict(zip(df.filename.values, df.id.values))
        md5_manifest = dict(zip(df.filename.values, df.md5.values))
    except Exception:
        slide_manifest, md5_manifest = None, None

    # Download slides from TCGA.
    dataset = P.dataset()
    slide_dest = dataset.sources[cfg.name]['slides']
    if download and slide_manifest is None:
        print("Unable to download slides; could not find valid TCGA manifest "
              "at experiments/gdc_manifest.tsv")
    elif download:
        print(f"Downloading slides to {slide_dest}...")
        download_slides(slides=dataset.slides(),
                        dest=slide_dest,
                        manifest=slide_manifest)

    # Verification.
    n_downloaded = len(dataset.slide_paths())
    n_total = len(dataset.slides())
    if n_downloaded != n_total:
        print(f"Warning: only {n_downloaded} of {n_total} slides found. "
              "Download slides from TCGA with the --download flag")

    # MD5 hash verification.
    if md5 and md5_manifest is None:
        print("Unable to download slides; could not find valid TCGA manifest "
              "at experiments/gdc_manifest.tsv")
    elif md5 and exists(slide_dest):
        failed = verify_md5(slide_dest, md5_manifest)
        if failed:
            raise ValueError("MD5 verification failed.")

    # --- Tile extraction -----------------------------------------------------
    print("Extracting tiles...")
    dataset = P.dataset(tile_px=cfg.tile_px, tile_um=cfg.tile_um)
    dataset.extract_tiles(**cfg.extract_kwargs)

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