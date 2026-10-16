import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_package.py"
EXPECTED = {
    "rls_matrix.yaml",
    "AGENTS_rls_addendum.md",
    "onsite_rls_checklist.md",
    "rls_test_cases.md",
    "manual_platform_permissions.md",
}


class GeneratePackageTests(unittest.TestCase):
    def run_generator(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_generates_complete_safe_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "package"
            result = self.run_generator(
                "--client-name",
                'Example "North" Company',
                "--client-slug",
                "example-north",
                "--industry",
                "professional-services",
                "--out",
                str(out),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({path.name for path in out.iterdir()}, EXPECTED)

            matrix = (out / "rls_matrix.yaml").read_text(encoding="utf-8")
            self.assertIn('name: "Example \\"North\\" Company"', matrix)
            self.assertIn("schema_version: \"1.1\"", matrix)
            self.assertIn("source_permissions_authoritative: true", matrix)
            self.assertIn("pending_id_default: deny_all_governed_internal_data", matrix)
            payload = yaml.safe_load(matrix)
            self.assertEqual(payload["schema_version"], "1.1")
            self.assertTrue(payload["scope"]["source_permissions_authoritative"])
            self.assertEqual(
                payload["roles"]["ai_consultant"]["can_read"],
                ["company_shared", "assigned_department_general"],
            )
            for generated in out.iterdir():
                self.assertNotIn("{{", generated.read_text(encoding="utf-8"))

    def test_rejects_path_traversal_slug(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_generator(
                "--client-name",
                "Example Company",
                "--client-slug",
                "../escape",
                "--out",
                str(Path(temp_dir) / "package"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("client_slug must use", result.stderr)

    def test_rejects_multiline_client_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_generator(
                "--client-name",
                "Example\nInjected",
                "--client-slug",
                "example",
                "--out",
                str(Path(temp_dir) / "package"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("single printable line", result.stderr)

    def test_refuses_all_overwrites(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "package"
            args = (
                "--client-name",
                "Example Company",
                "--client-slug",
                "example",
                "--out",
                str(out),
            )
            first = self.run_generator(*args)
            self.assertEqual(first.returncode, 0, first.stderr)
            matrix = out / "rls_matrix.yaml"
            original = matrix.read_text(encoding="utf-8")

            second = self.run_generator(*args)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("refusing to overwrite", second.stderr)
            self.assertEqual(matrix.read_text(encoding="utf-8"), original)

    def test_refuses_symlink_output_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "package"
            out.mkdir()
            protected = Path(temp_dir) / "protected.yaml"
            protected.write_text("do-not-change", encoding="utf-8")
            (out / "rls_matrix.yaml").symlink_to(protected)

            result = self.run_generator(
                "--client-name",
                "Example Company",
                "--client-slug",
                "example",
                "--out",
                str(out),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stderr)
            self.assertEqual(protected.read_text(encoding="utf-8"), "do-not-change")

    def test_skill_frontmatter_and_public_docs_have_no_client_placeholder(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: rls-onboarding-wizard", skill)
        self.assertIn('description: "', skill)
        public_docs = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "README.md", ROOT / "SKILL.md")
        )
        self.assertNotIn("Jasper 現場", public_docs)
        self.assertNotIn("{{client_name}}", public_docs)


if __name__ == "__main__":
    unittest.main()
