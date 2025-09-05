#!/usr/bin/env python3
import sys, os, urllib.request, time

CHUNK = 1024 * 512


def download(url, out):
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req) as r, open(out, "wb") as f:
        while True:
            b = r.read(CHUNK)
            if not b:
                break
            f.write(b)

if __name__ == "__main__":
    url = sys.argv[1]
    out = sys.argv[2]
    # Handle SourceForge redirect chain
    try:
        download(url, out)
    except Exception as e:
        print(f"::error::download failed: {e}")
        sys.exit(1)
    print(out)
