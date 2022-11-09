"""Utility functions"""

import os
import tarfile
import shutil
import hashlib
import pandas as pd
import slideflow as sf

from os.path import join, exists, basename
from typing import List, Any, Dict, Optional
from tqdm import tqdm
from slideflow.util import download_from_tcga

# -----------------------------------------------------------------------------

class EasyDict(dict):
    """Convenience class that behaves like a dict but allows access
    with the attribute syntax."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        del self[name]


def md5(path: str) -> str:
    """Calculate and return MD5 checksum for a file."""
    m = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            m.update(chunk)
    return m.hexdigest()


def download_slides(slides: List[str], dest: str, manifest: Dict[str, str]):
    """Download a list of slides to a destination, using
    a given manifest which maps slide names to TCGA UUIDs."""
    if not exists(dest):
        os.makedirs(dest)
    to_download = [s for s in slides if not exists(join(dest, f'{s}.svs'))]
    for i, slide in enumerate(to_download):
        download_from_tcga(manifest[slide+".svs"],
                           dest=dest,
                           message=f"Downloading {i+1} of {len(to_download)}...")


def verify_md5(
    dest: str,
    manifest: Dict[str, str],
    verbose: bool = True
) -> Optional[List[str]]:
    """Verify slides in a target directory with a dictionary of MD5 hashes."""

    if verbose:
        print(f"Verifying slides at {dest}...")

    slides_with_md5 = [s for s in os.listdir(dest) if s in manifest]
    failed_md5 = []
    for slide in tqdm(slides_with_md5):
        if md5(join(dest, slide)) != manifest[slide]:
            if verbose:
                tqdm.write(f"Slide {slide} failed MD5 verification")
            failed_md5 += [slide]

    if verbose:
        if not failed_md5:
            print(f"All {len(slides_with_md5)} slides passed MD5 verification.")
        else:
            print(f"Warning: {len(failed_md5)} slides failed MD5 verification:")

    return failed_md5


def resolve_relative_paths(cfg: EasyDict, path: str) -> EasyDict:
    """Convert relative paths into absolute paths."""

    if exists(join(path, cfg.annotations)):
        cfg.annotations = join(path, cfg.annotations)
    if exists(join(path, cfg.rois)):
        cfg.rois = join(path, cfg.rois)
    return cfg


def create_project(path: str, cfg: EasyDict) -> sf.Project:
    """Setup a project at the given directory using a given configuration."""
    P = sf.Project(path, annotations=join(path, basename(cfg.annotations)))
    shutil.copy(cfg.annotations, path)
    P.add_source(
        cfg.name,
        slides=join(path, 'slides'),
        roi=join(path, 'roi'),
        tiles=join(path, 'tiles'),
        tfrecords=join(path, 'tfrecords')
    )
    if 'rois' in cfg and cfg.rois:
        print(f"Extracting ROIs to {join(path, 'roi')}")
        roi_file = tarfile.open(cfg.rois)
        roi_file.extractall(join(path, 'roi'))
    return P


def prepare_project(
    path: str,
    cfg: EasyDict,
    md5: bool,
    download: bool
) -> sf.Project:
    """Prepare a given project, downloading and verifying missing slides."""

    # Initialize project in out directory.
    if sf.util.is_project(path):
        print(f"Project already configured at {path}")
        P = sf.Project(path)
    else:
        print(f"Setting up project at {path}")
        P = create_project(path, cfg=cfg)

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

    return P