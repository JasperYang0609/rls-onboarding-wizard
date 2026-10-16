#!/usr/bin/env python3
import argparse
import json
import os
import re
import stat
import unicodedata
from secrets import token_hex
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
    if any(
        (char.isspace() and char != " ")
        or unicodedata.category(char).startswith("C")
        for char in value
    ):
        raise ValueError(f"{field} must be a single printable line")
    return value


def safe_slug(value):
    value = value.strip()
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62})", value):
        raise ValueError("client_slug must use 1-63 lowercase letters, digits, or hyphens")
    return value


def lexical_absolute(path):
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def reject_symlink_components(path):
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"refusing symlinked output path component: {current}")


def atomic_write_at(directory_fd, name, content):
    temp_name = f".{name}.{token_hex(8)}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(temp_name, flags, 0o600, dir_fd=directory_fd)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
    except Exception:
        try:
            os.unlink(temp_name, dir_fd=directory_fd)
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
    out_dir = lexical_absolute(
        Path(args.out) if args.out else Path.cwd() / "records" / client_slug
    )
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
        content = render(src.read_text(encoding="utf-8"), values)
        if re.search(r"{{[a-zA-Z0-9_]+}}", content):
            raise SystemExit(f"unresolved template variable in {src.name}")
        rendered.append((name, content))

    try:
        reject_symlink_components(out_dir)
        if out_dir.exists() or out_dir.is_symlink():
            raise ValueError(
                "refusing to overwrite an existing output directory; generate into a new directory"
            )
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        reject_symlink_components(out_dir.parent)
        out_dir.mkdir(mode=0o700)

        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        directory_fd = os.open(out_dir, flags)
        try:
            opened = os.fstat(directory_fd)
            named = os.lstat(out_dir)
            if not stat.S_ISDIR(opened.st_mode) or (
                opened.st_dev,
                opened.st_ino,
            ) != (named.st_dev, named.st_ino):
                raise ValueError("output directory changed during generation")
            for name, content in rendered:
                atomic_write_at(directory_fd, name, content)
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    print("Generated RLS package:")
    for name, _ in rendered:
        print(f"- {out_dir / name}")

if __name__ == "__main__":
    main()
