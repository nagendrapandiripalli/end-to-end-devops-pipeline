# Offline configuration validation

```sh
python -m pip install -r scripts/requirements.txt
python scripts/validate_config.py
python -m unittest discover -s tests -v
```

Checks the example Service/Deployment/Ingress relationships, integer PDB budget,
Prometheus rule file references and Grafana JSON syntax without cloud credentials.
Tests mutate temporary copies to verify common mistakes are rejected.

These checks target this repository's numeric ports and integer PDB convention;
they are not a general Kubernetes schema validator or PromQL evaluator. Run
server-side Kubernetes validation and promtool checks in your deployment
environment. Jenkins execution, application health and live metrics still need
integration testing.
