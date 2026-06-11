#!/usr/bin/env python3
"""Initialize historical versions by attempting downloads from versioned URLs.

Based on the official download patterns:
- Mac: https://dldir1v6.qq.com/weixin/Universal/Mac/WeChatMac_{version}.dmg
- Windows: https://dldir1.qq.com/weixin/Windows/WeChatSetup_{version}.exe (not available)

This tries version ranges commonly seen in releases and checks if downloads succeed.
"""
import hashlib
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Configure SOCKS proxy if ALL_PROXY is set
if os.environ.get("ALL_PROXY"):
    import socks
    import socket
    proxy_url = os.environ["ALL_PROXY"]
    if proxy_url.startswith("socks5://"):
        proxy_host_port = proxy_url.replace("socks5://", "").split(":")
        socks.set_default_proxy(socks.SOCKS5, proxy_host_port[0], int(proxy_host_port[1]))
        socket.socket = socks.socksocket

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_version

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSIONS_FILE = REPO_ROOT / "versions.json"

# Known version patterns to try
MAC_VERSIONS = [
    "4.1.10", "4.1.9", "4.1.8", "4.1.7", "4.1.6", "4.1.5", "4.1.4", "4.1.3", "4.1.2", "4.1.1", "4.1.0",
    "4.0.3", "4.0.2", "4.0.1", "4.0.0.24",
    "3.9.10", "3.9.9", "3.9.8", "3.9.7", "3.9.6", "3.9.5",
    "3.8.10.17", "3.8.9.20", "3.8.8.25", "3.8.7.28",
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def try_download(url: str, dest: Path) -> bool:
    """Attempt to download a URL, return True if successful."""
    try:
        print(f"[init] trying {url}", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "wechat-versions-tracker"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
        print(f"[init] failed: {e}", file=sys.stderr)
        return False

def main() -> int:
    versions = check_version.load_versions()
    seen = {(v["platform"], v["version"]) for v in versions}
    new_entries: list[dict] = []

    with tempfile.TemporaryDirectory() as tmp:
        for version in MAC_VERSIONS:
            if ("mac", version) in seen:
                print(f"[mac] {version} already recorded, skipping")
                continue

            url = f"https://dldir1v6.qq.com/weixin/Universal/Mac/WeChatMac_{version}.dmg"
            dest = Path(tmp) / f"WeChat-mac-{version}.dmg"

            if not try_download(url, dest):
                continue

            # The URL path embeds the version (e.g. WeChatMac_4.1.10.dmg) and the
            # CDN returns HTTP 404 for non-existent versions, so a successful
            # download is itself confirmation. Only try to extract from the DMG
            # as a sanity check; if extraction fails (newer 4.x layouts can hide
            # Info.plist behind formats hdiutil/7z don't fully unpack), trust
            # the URL.
            detected_version = check_version.get_mac_version(dest)
            if detected_version and detected_version != version:
                print(f"[mac] version mismatch: URL has {version}, dmg has {detected_version}")
                version = detected_version
                if ("mac", version) in seen:
                    print(f"[mac] {version} already recorded after detection, skipping")
                    continue
            elif not detected_version:
                print(f"[mac] extraction failed; trusting URL version {version}")

            print(f"[mac] confirmed version: {version}")
            checksum = sha256(dest)
            size = dest.stat().st_size

            if os.environ.get("GITHUB_TOKEN"):
                tag = f"mac-{version}"
                asset_name = f"WeChat-mac-{version}.dmg"
                try:
                    release = check_version.create_release(
                        tag,
                        f"WeChat Mac {version}",
                        f"Source: {url}\n\nSHA256: `{checksum}`\nSize: {size} bytes",
                    )
                    asset = check_version.upload_asset(release["upload_url"], dest, asset_name)
                    download_url = asset["browser_download_url"]
                    release_url = release["html_url"]
                except Exception as e:
                    print(f"[mac] release/upload failed for {version}: {e}", file=sys.stderr)
                    download_url = ""
                    release_url = ""
            else:
                download_url = ""
                release_url = ""

            entry = {
                "platform": "mac",
                "version": version,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "size": size,
                "sha256": checksum,
                "source_url": url,
                "release_url": release_url,
                "download_url": download_url,
            }
            new_entries.append(entry)
            seen.add(("mac", version))

            # Clean up to save space
            dest.unlink()

    if new_entries:
        versions = new_entries + versions
        check_version.save_versions(versions)
        check_version.append_output("has_updates", "true")
        check_version.append_output("new_versions", ", ".join(f"mac {e['version']}" for e in new_entries))
        print(f"Added {len(new_entries)} historical entries")
    else:
        check_version.append_output("has_updates", "false")
        print("No new historical versions found")

    return 0

if __name__ == "__main__":
    sys.exit(main())
