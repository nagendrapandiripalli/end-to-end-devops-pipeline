import shutil
import tempfile
import unittest
from pathlib import Path
import sys
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_config import validate

class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for folder in ["4-orchestration", "5-monitoring"]:
            shutil.copytree(source/folder, self.root/folder)

    def change(self, path, edit):
        f = self.root/path
        data = yaml.safe_load(f.read_text())
        edit(data)
        f.write_text(yaml.safe_dump(data))

    def test_valid(self):
        self.assertEqual(validate(self.root), [])

    def test_bad_service_selector(self):
        self.change("4-orchestration/service.yaml", lambda d: d["spec"]["selector"].update(app="wrong"))
        self.assertIn("Service selector does not match pod labels", validate(self.root))

    def test_bad_target_port(self):
        self.change("4-orchestration/service.yaml", lambda d: d["spec"]["ports"][0].update(targetPort=9999))
        self.assertIn("Service targetPort is not an exposed container port", validate(self.root))

    def test_blocking_budget(self):
        self.change("4-orchestration/pdb.yaml", lambda d: d["spec"].update(minAvailable=3))
        self.assertIn("PDB must leave room for a voluntary disruption", validate(self.root))

    def test_missing_rules(self):
        (self.root/"5-monitoring/prometheus/alert_rules.yml").unlink()
        self.assertTrue(any("rule file missing" in e for e in validate(self.root)))

    def test_invalid_dashboard(self):
        (self.root/"5-monitoring/grafana/dashboard.json").write_text("broken")
        self.assertTrue(any("Invalid configuration" in e for e in validate(self.root)))

    def test_bad_ingress(self):
        self.change("4-orchestration/ingress.yaml", lambda d: d["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"].update(name="wrong"))
        self.assertIn("Ingress backend does not match Service", validate(self.root))
