#!/usr/bin/env python3
"""Regenerate the version table in README.md from versions.json."""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSIONS_FILE = REPO_ROOT / "versions.json"
README = REPO_ROOT / "README.md"

START = "<!-- versions:start -->"
END = "<!-- versions:end -->"


def human_size(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def render_table(versions: list[dict]) -> str:
    if not versions:
        return "_No versions tracked yet._"
    lines = [
        "| Platform | Version | Date | Size | SHA256 | Download |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for v in versions:
        download = v.get("download_url") or v.get("source_url") or ""
        link = f"[installer]({download})" if download else "—"
        sha = v.get("sha256", "")
        sha_short = sha[:12] if sha else "—"
        lines.append(
            f"| {v['platform']} | `{v['version']}` | {v.get('date', '')} | "
            f"{human_size(v.get('size', 0))} | `{sha_short}` | {link} |"
        )
    return "\n".join(lines)


def main() -> None:
    versions = json.loads(VERSIONS_FILE.read_text() or "[]")
    table = render_table(versions)
    text = README.read_text()
    if START not in text or END not in text:
        raise SystemExit("README markers missing")
    before, _, rest = text.partition(START)
    _, _, after = rest.partition(END)
    new = f"{before}{START}\n{table}\n{END}{after}"
    README.write_text(new)
    print(f"Updated README with {len(versions)} versions")


if __name__ == "__main__":
    main()
