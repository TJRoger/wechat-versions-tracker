#!/usr/bin/env python3
"""Check the latest WeChat installer versions for Mac and Windows.

For each platform, download the latest installer from the official Tencent CDN,
extract the version string, and if it is new, create a GitHub Release with the
installer attached and append a record to versions.json.
"""
import hashlib
import json
import os
import plistlib
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSIONS_FILE = REPO_ROOT / "versions.json"

SOURCES = {
    "mac": ("https://dldir1.qq.com/weixin/mac/WeChatMac.dmg", ".dmg"),
    "windows": ("https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe", ".exe"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    print(f"[download] {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "wechat-versions-tracker"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)


def get_mac_version(dmg_path: Path) -> str | None:
    """Extract CFBundleShortVersionString from WeChat.app/Contents/Info.plist inside the DMG."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            ["7z", "x", "-y", f"-o{tmp}", str(dmg_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"[mac] 7z extraction failed: {result.stderr[:500]}", file=sys.stderr)
            return None
        for plist_path in sorted(Path(tmp).rglob("Info.plist")):
            try:
                with open(plist_path, "rb") as f:
                    data = plistlib.load(f)
            except Exception:
                continue
            bundle_id = (data.get("CFBundleIdentifier") or "").lower()
            if "xinwechat" in bundle_id and "mainapp" not in bundle_id:
                v = data.get("CFBundleShortVersionString")
                if v:
                    return v
    return None


def get_windows_version(exe_path: Path) -> str | None:
    result = subprocess.run(
        ["exiftool", "-FileVersion", "-ProductVersion", "-json", str(exe_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[win] exiftool failed: {result.stderr[:500]}", file=sys.stderr)
        return None
    data = json.loads(result.stdout or "[]")
    if not data:
        return None
    return data[0].get("ProductVersion") or data[0].get("FileVersion")


def load_versions() -> list[dict]:
    if VERSIONS_FILE.exists():
        return json.loads(VERSIONS_FILE.read_text())
    return []


def save_versions(versions: list[dict]) -> None:
    VERSIONS_FILE.write_text(
        json.dumps(versions, indent=2, ensure_ascii=False) + "\n"
    )


def gh_request(method: str, url: str, *, data: bytes | None = None,
               extra_headers: dict | None = None) -> dict:
    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def create_release(tag: str, name: str, body: str) -> dict:
    repo = os.environ["GITHUB_REPOSITORY"]
    payload = json.dumps({
        "tag_name": tag,
        "name": name,
        "body": body,
        "draft": False,
        "prerelease": False,
    }).encode()
    return gh_request(
        "POST",
        f"https://api.github.com/repos/{repo}/releases",
        data=payload,
        extra_headers={"Content-Type": "application/json"},
    )


def upload_asset(upload_url_template: str, asset_path: Path, asset_name: str) -> dict:
    base = upload_url_template.split("{")[0]
    url = f"{base}?name={urllib.parse.quote(asset_name)}"
    with open(asset_path, "rb") as f:
        body = f.read()
    return gh_request(
        "POST", url, data=body,
        extra_headers={"Content-Type": "application/octet-stream"},
    )


def append_output(key: str, value: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a") as f:
        f.write(f"{key}={value}\n")


def main() -> int:
    versions = load_versions()
    seen = {(v["platform"], v["version"]) for v in versions}
    new_entries: list[dict] = []
    new_labels: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        for platform, (url, ext) in SOURCES.items():
            dest = Path(tmp) / f"WeChat-{platform}{ext}"
            try:
                download(url, dest)
            except Exception as e:
                print(f"[{platform}] download failed: {e}", file=sys.stderr)
                continue

            version = (
                get_mac_version(dest) if platform == "mac"
                else get_windows_version(dest)
            )
            if not version:
                print(f"[{platform}] could not extract version", file=sys.stderr)
                continue
            print(f"[{platform}] detected version: {version}")

            if (platform, version) in seen:
                print(f"[{platform}] {version} already recorded, skipping")
                continue

            checksum = sha256(dest)
            size = dest.stat().st_size

            if os.environ.get("GITHUB_TOKEN"):
                tag = f"{platform}-{version}"
                asset_name = f"WeChat-{platform}-{version}{ext}"
                release = create_release(
                    tag,
                    f"WeChat {platform.capitalize()} {version}",
                    f"Source: {url}\n\nSHA256: `{checksum}`\nSize: {size} bytes",
                )
                asset = upload_asset(release["upload_url"], dest, asset_name)
                download_url = asset["browser_download_url"]
                release_url = release["html_url"]
            else:
                download_url = ""
                release_url = ""

            entry = {
                "platform": platform,
                "version": version,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "size": size,
                "sha256": checksum,
                "source_url": url,
                "release_url": release_url,
                "download_url": download_url,
            }
            new_entries.append(entry)
            new_labels.append(f"{platform} {version}")

    if new_entries:
        versions = new_entries + versions
        save_versions(versions)
        append_output("has_updates", "true")
        append_output("new_versions", ", ".join(new_labels))
        print(f"Added {len(new_entries)} new entries: {new_labels}")
    else:
        append_output("has_updates", "false")
        print("No new versions found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
