#!/usr/bin/env python3
import argparse
import json
import os
import re
import tempfile
from pathlib import Path

TEMPLATES = [
    "rls_matrix.yaml",
    "AGENTS_rls_addendum.md",
    "onsite_rls_checklist.md",
    "rls_test_cases.md",
    "manual_platform_permissions.md",
]

def render(text, values):
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def single_line(value, field, max_length=120):
    value = value.strip()
    if not value:
        raise ValueError(f"{field} must not be empty")
    if len(value) > max_length:
        raise ValueError(f"{field} must be at most {max_length} characters")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"{field} must be a single printable line")
    return value


def safe_slug(value):
    value = value.strip()
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62})", value):
        raise ValueError("client_slug must use 1-63 lowercase letters, digits, or hyphens")
    return value


def atomic_write(path, content):
    if path.is_symlink():
        raise ValueError(f"refusing to write through symlink: {path}")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

def main():
    ap = argparse.ArgumentParser(description="Generate OpenClaw RLS onboarding starter package")
    ap.add_argument("--client-name", required=True)
    ap.add_argument("--client-slug", required=True)
    ap.add_argument("--industry", default="")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    try:
        client_name = single_line(args.client_name, "client_name")
        client_slug = safe_slug(args.client_slug)
        industry = single_line(args.industry, "industry") if args.industry.strip() else ""
    except ValueError as exc:
        ap.error(str(exc))

    skill_dir = Path(__file__).resolve().parents[1]
    template_dir = skill_dir / "assets" / "templates"
    out_dir = Path(args.out).expanduser() if args.out else Path.cwd() / "records" / client_slug
    values = {
        "client_name": client_name,
        "client_slug": client_slug,
        "industry": industry,
        "client_name_yaml": json.dumps(client_name, ensure_ascii=False),
        "client_slug_yaml": json.dumps(client_slug, ensure_ascii=False),
        "industry_yaml": json.dumps(industry, ensure_ascii=False),
    }

    rendered = []
    for name in TEMPLATES:
        src = template_dir / f"{name}.tpl"
        dst = out_dir / name
        content = render(src.read_text(encoding="utf-8"), values)
        if re.search(r"{{[a-zA-Z0-9_]+}}", content):
            raise SystemExit(f"unresolved template variable in {src.name}")
        rendered.append((dst, content))

    existing = [dst for dst, _ in rendered if dst.exists() or dst.is_symlink()]
    if existing:
        names = ", ".join(path.name for path in existing)
        raise SystemExit(
            "refusing to overwrite existing files; generate into a new directory and review the diff: "
            f"{names}"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    for dst, content in rendered:
        atomic_write(dst, content)

    print("Generated RLS package:")
    for p, _ in rendered:
        print(f"- {p}")

if __name__ == "__main__":
    main()
