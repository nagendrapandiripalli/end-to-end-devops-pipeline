"""Exercise the actual CLI, not just the validation function."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_network.py"
EXAMPLE = ROOT / "1-infrastructure/network.tfvars.json.example"

class NetworkCLITests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, timeout=10)

    def test_committed_example(self):
        result = self.invoke(EXAMPLE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Network input checks passed", result.stdout)

    def test_no_arguments(self):
        self.assertEqual(self.invoke().returncode, 2)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.invoke(Path(directory) / "missing.json")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{broken", encoding="utf-8")
            result = self.invoke(path)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_overlapping_subnets(self):
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        data["private_subnet_cidrs"] = data["public_subnet_cidrs"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "overlap.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = self.invoke(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Overlapping subnets", result.stdout)
