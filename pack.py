#!/usr/bin/env python3

import argparse
import os
import re
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "config.yaml")
STRIP_PREFIX = "/etc/mosdns/"

SOURCE_RE = re.compile(
    r'^[ \t]*-\s+["\']?(?P<path>/\S+\.txt)["\']?[ \t]*\r?\n'
    r'[ \t]*#\s*(?P<url>https?://\S+)[ \t]*$',
    re.MULTILINE,
)

def parse_sources(config_text):
    sources = []
    for m in SOURCE_RE.finditer(config_text):
        path = m.group("path")
        url = m.group("url")
        rel_path = path[len(STRIP_PREFIX):] if path.startswith(STRIP_PREFIX) else path.lstrip("/")
        sources.append((rel_path, url))
    return sources


def download(url, timeout=30):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to config.yaml")
    parser.add_argument("--output-dir", default="dist", help="Directory to write fetched files into")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config_text = f.read()

    sources = parse_sources(config_text)
    if not sources:
        print("No download sources found in config.yaml", file=sys.stderr)
        return 1

    failed = []
    for rel_path, url in sources:
        dest = os.path.join(args.output_dir, rel_path)
        print(f"Fetching {url} -> {dest}")
        try:
            data = download(url)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            failed.append((rel_path, url, str(e)))
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
    return 


if __name__ == "__main__":
    sys.exit(main())
