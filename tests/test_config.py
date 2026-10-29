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

    def test_boolean_budget(self):
        self.change("4-orchestration/pdb.yaml", lambda d: d["spec"].update(minAvailable=True))
        self.assertIn("PDB must leave room for a voluntary disruption", validate(self.root))

    def test_boolean_replicas(self):
        self.change("4-orchestration/deployment.yaml", lambda d: d["spec"].update(replicas=True))
        self.assertIn("PDB must leave room for a voluntary disruption", validate(self.root))

    def test_bad_deployment_selector(self):
        self.change("4-orchestration/deployment.yaml", lambda d: d["spec"]["selector"]["matchLabels"].update(app="wrong"))
        self.assertIn("Deployment selector does not match pod labels", validate(self.root))

    def test_invalid_numeric_ports(self):
        # Keep references consistent: relational equality alone must not pass
        # invalid ports, including Python's True == 1 and 8080.0 == 8080.
        for value in [True, False, 0, -1, 65536, 8080.0, "8080", None]:
            with self.subTest(value=value):
                self.change("4-orchestration/deployment.yaml", lambda d: d["spec"]["template"]["spec"]["containers"][0]["ports"][0].update(containerPort=value))
                self.change("4-orchestration/service.yaml", lambda d: d["spec"]["ports"][0].update(port=value, targetPort=value))
                self.change("4-orchestration/ingress.yaml", lambda d: d["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"]["port"].update(number=value))
                errors = validate(self.root)
                for field in ["containerPort", "Service port", "Service targetPort", "Ingress backend port"]:
                    self.assertIn(f"{field} must be an integer from 1 to 65535", errors)

    def test_numeric_port_boundaries(self):
        for value in [1, 65535]:
            with self.subTest(value=value):
                self.change("4-orchestration/deployment.yaml", lambda d: d["spec"]["template"]["spec"]["containers"][0]["ports"][0].update(containerPort=value))
                self.change("4-orchestration/service.yaml", lambda d: d["spec"]["ports"][0].update(port=value, targetPort=value))
                self.change("4-orchestration/ingress.yaml", lambda d: d["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"]["port"].update(number=value))
                def update_probes(d):
                    c = d["spec"]["template"]["spec"]["containers"][0]
                    for name in ["startupProbe", "readinessProbe", "livenessProbe"]:
                        c[name]["httpGet"]["port"] = value
                self.change("4-orchestration/deployment.yaml", update_probes)
                self.assertEqual(validate(self.root), [])

    def test_probe_port_mismatch(self):
        for name in ["startupProbe", "readinessProbe", "livenessProbe"]:
            with self.subTest(probe=name):
                self.change("4-orchestration/deployment.yaml", lambda d: d["spec"]["template"]["spec"]["containers"][0][name]["httpGet"].update(port=9090))
                self.assertIn(f"{name} port must match its container port", validate(self.root))

    def test_missing_probe(self):
        for name in ["startupProbe", "readinessProbe", "livenessProbe"]:
            with self.subTest(probe=name):
                self.change("4-orchestration/deployment.yaml", lambda d: d["spec"]["template"]["spec"]["containers"][0].pop(name))
                self.assertIn(f"{name} must define an HTTP health check", validate(self.root))

    def test_invalid_probe_port(self):
        for value in [True, 0, 65536, "8080", 8080.0]:
            with self.subTest(port=value):
                self.change("4-orchestration/deployment.yaml", lambda d: d["spec"]["template"]["spec"]["containers"][0]["startupProbe"]["httpGet"].update(port=value))
                self.assertIn("startupProbe port must be an integer from 1 to 65535", validate(self.root))
