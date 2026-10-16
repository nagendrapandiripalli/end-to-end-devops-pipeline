"""Offline consistency checks for this repository's example configuration."""
import json
from pathlib import Path
import sys
import yaml

def validate(root):
    root = Path(root)
    errors = []
    def load(path):
        return yaml.safe_load((root / path).read_text(encoding="utf-8"))
    try:
        d = load("4-orchestration/deployment.yaml")["spec"]
        s = load("4-orchestration/service.yaml")
        ingress = load("4-orchestration/ingress.yaml")
        pdb = load("4-orchestration/pdb.yaml")["spec"]
        labels = d["template"]["metadata"]["labels"]
        for name, selector in [("Service", s["spec"]["selector"]), ("PDB", pdb["selector"]["matchLabels"])]:
            if not selector or any(labels.get(k) != v for k, v in selector.items()):
                errors.append(f"{name} selector does not match pod labels")
        ports = {p["containerPort"] for c in d["template"]["spec"]["containers"] for p in c.get("ports", [])}
        for port in s["spec"]["ports"]:
            if port["targetPort"] not in ports:
                errors.append("Service targetPort is not an exposed container port")
        for rule in ingress["spec"]["rules"]:
            for path in rule["http"]["paths"]:
                backend = path["backend"]["service"]
                if backend["name"] != s["metadata"]["name"] or backend["port"]["number"] not in {p["port"] for p in s["spec"]["ports"]}:
                    errors.append("Ingress backend does not match Service")
        if not isinstance(pdb["minAvailable"], int) or not 0 < pdb["minAvailable"] < d["replicas"]:
            errors.append("PDB must leave room for a voluntary disruption")
        config_path = root / "5-monitoring/prometheus/prometheus.yml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        for pattern in config.get("rule_files", []):
            matches = list(config_path.parent.glob(pattern))
            if not matches:
                errors.append(f"Prometheus rule file missing: {pattern}")
            for match in matches:
                rules = yaml.safe_load(match.read_text(encoding="utf-8"))
                if not isinstance(rules.get("groups"), list):
                    errors.append(f"Rule file has no groups: {match.name}")
        json.loads((root / "5-monitoring/grafana/dashboard.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError, TypeError, AttributeError, yaml.YAMLError) as exc:
        errors.append(f"Invalid configuration: {exc}")
    return errors

if __name__ == "__main__":
    errors = validate(Path(__file__).resolve().parents[1])
    for error in errors:
        print(error, file=sys.stderr)
    print("Configuration checks failed" if errors else "Configuration consistency checks passed")
    sys.exit(bool(errors))
