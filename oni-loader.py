#!/usr/bin/env python

import argparse
from rocrate.rocrate import ROCrate
import requests
from pathlib import Path
import sys


def load_collection(cratedir, baseURL, collectionId):
    url = f"{baseURL}/api/object/meta?resolve-parts&id={collectionId}"
    r = requests.get(url)
    if r.status_code == 200:
        rcj = r.json()
        if "error" in rcj:
            print(f"Error fetching collection metadata for {url}")
            return None
        ro_metadata = cratedir / "ro-crate-metadata.json"
        with open(ro_metadata, "w") as rmf:
            rmf.write(r.text)
        return ROCrate(cratedir)


def download_part(cratedir, part):
    """Download one bytestream"""
    print(f"Downloading {part.id}")
    r = requests.get(part.id)
    if r.status_code == 200:
        print(r.txt)
    else:
        print(f"download failed: {r.status_code}")


def get_root(crate):
    metadata_descriptor = crate.dereference("ro-crate-metadata.json")
    root_id = metadata_descriptor["about"]
    root_entity = crate.dereference(root_id["@id"])
    return root_entity


def main():
    ap = argparse.ArgumentParser("Oni load test")
    ap.add_argument(
        "--repo",
        default="https://data.atap.edu.au",
        type=str,
        help="base URL of repo",
    )
    ap.add_argument("--collection", type=str, help="ID of collection")
    ap.add_argument("--dir", type=Path, help="directory")
    args = ap.parse_args()
    if not args.collection or not args.dir:
        print("You need to provide a collection id and a directory")
        sys.exit(-1)

    crate = load_collection(args.dir, args.repo, args.collection)
    if crate:
        root = get_root(crate)
        for part in root["hasPart"]:
            if "File" in part.type:
                download_part(args.dir, part)
                sys.exit(-1)


if __name__ == "__main__":
    main()
