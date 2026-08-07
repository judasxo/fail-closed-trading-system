import ast
import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicReleaseTests(unittest.TestCase):
    def test_demo_has_no_network_or_process_execution_imports(self) -> None:
        forbidden = {"http", "requests", "socket", "subprocess", "urllib"}
        for path in (ROOT / "src" / "failclosed_demo").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".", 1)[0] for alias in node.names}
                    self.assertTrue(roots.isdisjoint(forbidden), path.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".", 1)[0], forbidden, path.name)

    def test_release_contains_no_private_windows_paths(self) -> None:
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".txt"}:
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"(?i)[a-z]:\\users\\", path.as_posix())

    def test_public_release_uses_generic_vendor_description(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (ROOT / "README.md", ROOT / "evidence" / "outcomes.json")
        )
        self.assertNotIn("ya" + "hoo", public_text)

    def test_evidence_is_sanitized_and_hash_shaped(self) -> None:
        evidence = json.loads((ROOT / "evidence" / "outcomes.json").read_text(encoding="utf-8"))
        serialized = json.dumps(evidence, sort_keys=True).lower()
        for forbidden in ("account_id", "order_id", "client_order_id", "raw_price", "api_secret"):
            self.assertNotIn(forbidden, serialized)
        hashes = re.findall(r'\b[A-F0-9]{64}\b', json.dumps(evidence))
        self.assertGreaterEqual(len(hashes), 12)

    def test_manifest_matches_public_files(self) -> None:
        manifest_path = ROOT / "PUBLIC_MANIFEST.json"
        if not manifest_path.exists():
            self.skipTest("Manifest is generated during release packaging")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest["files"]), 10)
        for item in manifest["files"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
            self.assertEqual(actual, item["sha256"], item["path"])


if __name__ == "__main__":
    unittest.main()
