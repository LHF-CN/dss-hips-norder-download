#!/usr/bin/env python3

import argparse
import os
import urllib.error
import urllib.request

BASE_URL = "http://alasky.u-strasbg.fr/DSS/DSSColor"
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = _SCRIPT_DIR
BASE_PROPERTIES = None


def get_base_properties():
    """Fetch and cache the remote HiPS properties file."""
    global BASE_PROPERTIES
    if BASE_PROPERTIES is not None:
        return BASE_PROPERTIES
    url = f"{BASE_URL}/properties"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            BASE_PROPERTIES = resp.read().decode("utf-8")
            return BASE_PROPERTIES
    except Exception as e:
        print(f"Failed to fetch base properties: {e}")
    return ""


def num_pixels_for_order(order):
    """HEALPix nested: 12 * 4^order pixels for full sky."""
    return 12 * (4 ** order)


def download_file(url, filepath):
    """Download a single tile; skip if exists. Returns 'ok'|'exists'|'404'|'fail'."""
    if os.path.exists(filepath):
        return "exists"
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
            return "ok"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "404"
        print(f"  Failed {url}: {e.code}")
        return "fail"
    except Exception as e:
        print(f"  Error {url}: {e}")
        return "fail"


def write_properties(output_dir, max_order, base_props):
    base_map = {
        "hips_tile_format": "jpg",
        "hips_frame": "equatorial",
        "hips_order": str(max_order),
        "hips_order_min": "0",
    }
    if base_props:
        for line in base_props.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                if key not in ("hips_initial_ra", "hips_initial_dec", "hips_initial_fov"):
                    base_map[key] = val.strip()
    base_map["obs_title"] = "DSS2 Color (full sky)"
    base_map["hips_order"] = str(max_order)

    content = "".join(f"{k} = {v}\n" for k, v in base_map.items())
    for name in ("properties", "properties.txt"):
        with open(os.path.join(output_dir, name), "w") as f:
            f.write(content)
    print(f"Wrote {output_dir}/properties (hips_order={max_order})")


def main():
    parser = argparse.ArgumentParser(description="Download full-sky HiPS tiles (see README.md)")
    parser.add_argument(
        "--max-order",
        type=int,
        default=3,
        help="Max HEALPix order (default 3). 3=3072 tiles, 4=12288, 5=49152.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: script dir).",
    )
    parser.add_argument(
        "--min-order",
        type=int,
        default=0,
        help="Start from this order (default 0).",
    )
    args = parser.parse_args()

    if args.max_order < 0 or args.max_order > 10:
        print("--max-order should be 0..10 (e.g. 3 or 4 for reasonable size)")
        return
    if args.min_order < 0 or args.min_order > args.max_order:
        print("--min-order must be 0..max-order")
        return

    base_props = get_base_properties()
    if not base_props:
        print("Could not fetch remote properties; using defaults.")
    os.makedirs(args.output, exist_ok=True)
    write_properties(args.output, args.max_order, base_props)

    total_ok = 0
    total_404 = 0
    total_exists = 0
    total_fail = 0

    for order in range(args.min_order, args.max_order + 1):
        npix = num_pixels_for_order(order)
        print(f"\nOrder {order}: {npix} tiles")
        ok, exist, n404, fail = 0, 0, 0, 0
        for pix in range(npix):
            dir_idx = (pix // 10000) * 10000
            rel = f"Norder{order}/Dir{dir_idx}/Npix{pix}.jpg"
            url = f"{BASE_URL}/{rel}"
            local = os.path.join(args.output, rel)
            status = download_file(url, local)
            if status == "ok":
                ok += 1
            elif status == "exists":
                exist += 1
            elif status == "404":
                n404 += 1
            else:
                fail += 1
            if (pix + 1) % 500 == 0 or pix == npix - 1:
                print(f"  {pix + 1}/{npix} (ok={ok} exist={exist} 404={n404} fail={fail})")
        total_ok += ok
        total_exists += exist
        total_404 += n404
        total_fail += fail

    print("\n" + "=" * 50)
    print("Done")
    print("=" * 50)
    print(f"Output: {args.output}")
    print(f"Orders: {args.min_order}..{args.max_order}")
    print(f"Downloaded: {total_ok} | Existed: {total_exists} | 404: {total_404} | Failed: {total_fail}")
    print("=" * 50)
    if total_404 > 0:
        print("Note: 404 is normal for DSS in regions with no coverage.")


if __name__ == "__main__":
    main()
