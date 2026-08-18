#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://cbt-cards.github.io"
ZERO_SHA = "0" * 40


def public_html_url(path):
    path = path.strip().lstrip("./")
    if not path.endswith(".html") or path == "404.html":
        return None
    if path == "index.html":
        return ORIGIN + "/"
    if path.endswith("/index.html"):
        return ORIGIN + "/" + path[: -len("index.html")]
    return ORIGIN + "/" + path


def sitemap_urls():
    import xml.etree.ElementTree as ET

    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return sorted({node.text for node in tree.findall("s:url/s:loc", ns) if node.text})


def changed_urls(base, head):
    if not base or base == ZERO_SHA:
        return sitemap_urls()

    proc = subprocess.run(
        ["git", "diff", "--name-status", base, head, "--"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    urls = set()
    for raw in proc.stdout.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        paths = parts[1:]
        if status.startswith("R") or status.startswith("C"):
            candidates = paths[:2]
        else:
            candidates = paths[:1]
        for path in candidates:
            url = public_html_url(path)
            if url:
                urls.add(url)
    return sorted(urls)


def load_config():
    config_path = ROOT / "data/indexnow.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    key = config["key"]
    key_file = ROOT / f"{key}.txt"
    if not key_file.exists():
        raise RuntimeError(f"IndexNow key file is missing: {key_file.name}")
    if key_file.read_text(encoding="utf-8").strip() != key:
        raise RuntimeError("IndexNow key file contents do not match data/indexnow.json")
    return config


def submit(urls, config):
    if not urls:
        print("IndexNow: no changed public HTML URLs to submit.")
        return 0
    if len(urls) > 10000:
        raise RuntimeError(f"IndexNow URL batch is too large: {len(urls)}")

    payload = {
        "host": config["host"],
        "key": config["key"],
        "keyLocation": config["key_location"],
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        config["endpoint"],
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "CBT-Cards-IndexNow/1.0",
        },
        method="POST",
    )

    print(f"IndexNow: submitting {len(urls)} changed URL(s):")
    for url in urls:
        print(f"- {url}")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.status
            if status not in {200, 202}:
                raise RuntimeError(f"IndexNow returned unexpected HTTP {status}")
            print(f"IndexNow: HTTP {status}")
            return 0
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"IndexNow HTTP error {exc.code}: {detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"IndexNow network error: {exc}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="Notify IndexNow about changed CBT Cards HTML URLs.")
    parser.add_argument("--base", required=True, help="Git commit before the deployed push")
    parser.add_argument("--head", required=True, help="Git commit being deployed")
    args = parser.parse_args()

    config = load_config()
    if config.get("host") != "cbt-cards.github.io":
        raise RuntimeError("Unexpected IndexNow host")
    if config.get("endpoint") != "https://api.indexnow.org/indexnow":
        raise RuntimeError("Unexpected IndexNow endpoint")

    urls = changed_urls(args.base, args.head)
    return submit(urls, config)


if __name__ == "__main__":
    raise SystemExit(main())
