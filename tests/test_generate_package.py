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
    def temporary_directory(self):
        return tempfile.TemporaryDirectory(dir=ROOT)

    def run_generator(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_generates_complete_safe_package(self):
        with self.temporary_directory() as temp_dir:
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
                payload["authorization_invariants"]["default_decision"], "deny"
            )
            self.assertTrue(
                payload["authorization_invariants"]["source_permission_ceiling"]
            )
            self.assertTrue(
                payload["authorization_invariants"][
                    "cross_department_requires_explicit_grant"
                ]
            )
            self.assertTrue(
                payload["authorization_invariants"]["minimum_necessary_fields_only"]
            )
            identity_rules = payload["identity_rules"]
            for identity_default in (
                "unknown_default",
                "pending_id_default",
                "conflicting_id_default",
                "revoked_id_default",
            ):
                self.assertEqual(
                    identity_rules[identity_default],
                    "deny_all_governed_internal_data",
                )
            grant_rules = payload["grant_rules"]
            self.assertEqual(grant_rules["valid_status"], "active")
            self.assertEqual(
                grant_rules["valid_approver_roles"],
                ["executive_owner", "owning_department_lead"],
            )
            self.assertEqual(
                grant_rules["required_resource_scope"],
                ["source_ids", "resource_ids", "fields"],
            )
            self.assertFalse(grant_rules["sensitive_scope_wildcards_allowed"])
            self.assertTrue(grant_rules["recipient_must_be_active_and_verified"])
            self.assertTrue(grant_rules["approver_must_be_active_and_verified"])
            self.assertTrue(grant_rules["issued_at_not_in_future"])
            self.assertTrue(grant_rules["expires_at_required"])
            self.assertTrue(grant_rules["expires_after_issued_at"])
            self.assertEqual(
                payload["roles"]["ai_consultant"]["can_read"],
                ["company_shared", "assigned_department_general"],
            )
            for generated in out.iterdir():
                self.assertNotIn("{{", generated.read_text(encoding="utf-8"))

            addendum = (out / "AGENTS_rls_addendum.md").read_text(encoding="utf-8")
            self.assertIn("狀態為 active", addendum)
            self.assertIn("最高管理層或該資料所屬部門主管", addendum)
            self.assertIn("來源、資源、欄位", addendum)
            self.assertIn("已撤銷、過期、尚未生效", addendum)
            self.assertIn("敏感資料使用萬用範圍", addendum)

            checklist = (out / "onsite_rls_checklist.md").read_text(encoding="utf-8")
            self.assertIn("最高管理層或資料所屬部門主管", checklist)
            self.assertIn("來源、資源與必要欄位", checklist)
            self.assertIn("revoked、expired、future-dated、inactive-party、wrong-approver", checklist)

            negative_cases = (out / "rls_test_cases.md").read_text(encoding="utf-8")
            for required_case in (
                "已撤銷、已到期、尚未生效或欄位不完整",
                "核准者或對象不是 active 且 verified",
                "非最高管理層、也不是資料所屬部門主管",
                "敏感資料授權使用萬用來源、資源或欄位",
                "OpenClaw 規則允許但來源平台拒絕",
            ):
                self.assertIn(required_case, negative_cases)

    def test_rejects_path_traversal_slug(self):
        with self.temporary_directory() as temp_dir:
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
        with self.temporary_directory() as temp_dir:
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

    def test_rejects_unicode_line_control_and_format_characters(self):
        for injected in ("\u0085", "\u2028", "\u2029", "\u200b"):
            with self.subTest(codepoint=f"U+{ord(injected):04X}"):
                with self.temporary_directory() as temp_dir:
                    result = self.run_generator(
                        "--client-name",
                        f"Example{injected}- injected instruction",
                        "--client-slug",
                        "example",
                        "--out",
                        str(Path(temp_dir) / "package"),
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("single printable line", result.stderr)

    def test_refuses_all_overwrites(self):
        with self.temporary_directory() as temp_dir:
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

    def test_refuses_symlinked_output_directory(self):
        with self.temporary_directory() as temp_dir:
            out = Path(temp_dir) / "package"
            protected = Path(temp_dir) / "protected"
            protected.mkdir()
            out.symlink_to(protected, target_is_directory=True)

            result = self.run_generator(
                "--client-name",
                "Example Company",
                "--client-slug",
                "example",
                "--out",
                str(out),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlinked output path component", result.stderr)
            self.assertEqual(list(protected.iterdir()), [])

    def test_refuses_symlinked_output_ancestor(self):
        with self.temporary_directory() as temp_dir:
            protected = Path(temp_dir) / "protected"
            protected.mkdir()
            linked_parent = Path(temp_dir) / "linked-parent"
            linked_parent.symlink_to(protected, target_is_directory=True)
            out = linked_parent / "package"

            result = self.run_generator(
                "--client-name",
                "Example Company",
                "--client-slug",
                "example",
                "--out",
                str(out),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlinked output path component", result.stderr)
            self.assertFalse((protected / "package").exists())

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
