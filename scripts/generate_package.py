#!/usr/bin/env python3
import argparse
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

def main():
    ap = argparse.ArgumentParser(description="Generate OpenClaw RLS onboarding starter package")
    ap.add_argument("--client-name", required=True)
    ap.add_argument("--client-slug", required=True)
    ap.add_argument("--industry", default="")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    template_dir = skill_dir / "assets" / "templates"
    out_dir = Path(args.out) if args.out else Path.cwd() / "records" / args.client_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    values = {"client_name": args.client_name, "client_slug": args.client_slug, "industry": args.industry}

    written = []
    for name in TEMPLATES:
        src = template_dir / f"{name}.tpl"
        dst = out_dir / name
        dst.write_text(render(src.read_text(), values), encoding="utf-8")
        written.append(dst)
    print("Generated RLS package:")
    for p in written:
        print(f"- {p}")

if __name__ == "__main__":
    main()
