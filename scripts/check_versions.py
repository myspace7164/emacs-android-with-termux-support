#!/usr/bin/env python3
import os, json, sys, re, urllib.request
from urllib.error import HTTPError, URLError

GITHUB_TERMUX_API = "https://api.github.com/repos/termux/termux-app/releases/latest"


def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        return r.read(), dict(r.headers)


def latest_termux_asset(regex_pattern):
    data, _ = http_get(GITHUB_TERMUX_API, headers={"Accept": "application/vnd.github+json"})
    rel = json.loads(data.decode("utf-8"))
    assets = rel.get("assets", [])
    pat = re.compile(regex_pattern)
    for a in assets:
        name = a.get("name", "")
        if pat.search(name):
            return {
                "name": name,
                "url": a.get("browser_download_url"),
                "tag": rel.get("tag_name") or rel.get("name") or "latest"
            }
    raise SystemExit(f"No Termux asset matched regex: {regex_pattern}")


def latest_sourceforge_file(project):
    # SourceForge provides a stable 'latest' redirect URL
    url = f"https://sourceforge.net/projects/{project}/files/latest/download"
    try:
        _, headers = http_get(url)
        # Resolve final filename from Content-Disposition if present
        disp = headers.get("Content-Disposition", "")
        m = re.search(r'filename="?([^";]+)"?', disp)
        name = m.group(1) if m else "emacs-latest.apk"
        final_url = headers.get("Location") or url  # if no redirect, use given
        return {"name": name, "url": url}
    except (HTTPError, URLError) as e:
        raise SystemExit(f"Failed to query SourceForge: {e}")


def main():
    termux_re = os.getenv("TERMUX_ASSET_REGEX", r"(?i)termux.*universal.*\.apk$")
    emacs_direct = os.getenv("EMACS_DIRECT_URL", "").strip()
    emacs_project = os.getenv("EMACS_SOURCEFORGE_PROJECT", "").strip()
    emacs_re = os.getenv("EMACS_ASSET_REGEX", r"(?i).*\.apk$")

    termux = latest_termux_asset(termux_re)

    if emacs_direct:
        emacs = {"name": os.path.basename(emacs_direct.split("?")[0]) or "emacs.apk", "url": emacs_direct}
    elif emacs_project:
        emacs = latest_sourceforge_file(emacs_project)
    else:
        # If not configured, fail clearly so the user sets EMACS_SOURCEFORGE_PROJECT or EMACS_DIRECT_URL
        print("::error::Set EMACS_SOURCEFORGE_PROJECT or EMACS_DIRECT_URL to locate Emacs APK", file=sys.stderr)
        sys.exit(2)

    out = {"termux": termux, "emacs": emacs}
    print(json.dumps(out))

if __name__ == "__main__":
    main()
