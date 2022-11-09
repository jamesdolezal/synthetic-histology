"""Utility functions"""

import os
import hashlib

from os.path import join, exists
from typing import List, Any, Dict, Optional
from tqdm import tqdm
from slideflow.test.utils import download_from_tcga
from slideflow.util import path_to_name

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
                           message=f"Downloading {i} of {len(to_download)}...")


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
