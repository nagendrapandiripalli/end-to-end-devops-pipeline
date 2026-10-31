# Offline configuration validation

```sh
python -m pip install -r scripts/requirements.txt
python scripts/validate_config.py
python -m unittest discover -s tests -v
```

Checks the example Service/Deployment/Ingress relationships, numeric port types
and range (1–65535), integer PDB budget,
Prometheus rule file references and Grafana JSON syntax without cloud credentials.
Tests mutate temporary copies to verify common mistakes are rejected.

These checks target this repository's numeric ports and integer PDB convention;
they are not a general Kubernetes schema validator or PromQL evaluator. Run
server-side Kubernetes validation in your deployment environment. Jenkins execution, application health and live metrics still need
integration testing.

## Platform coverage

GitHub Actions runs the configuration checker, network example and full Python
test suite on both Ubuntu and Windows using Python 3.12. Matrix fail-fast is
disabled so a failure on one platform does not hide the other result. The
Ansible syntax check remains Linux-only, separate from these portable scripts.

The example requires HTTP startup, readiness and liveness probes. Each numeric
probe port must match a port declared by its own container; this catches stale
health-check ports after application port changes. Other valid Kubernetes probe
types and named ports are outside this example checker's scope.

## Native Prometheus validation

A separate Linux CI job runs Prometheus 3.2.1's promtool in its official container
to validate the configuration and referenced alert rules, including PromQL and
annotation templates. The configuration directory is mounted read-only; no
Prometheus server or cloud resources are started. Docker must be available to
repeat this check locally:

```sh
docker run --rm --entrypoint /bin/promtool -v "$PWD/5-monitoring/prometheus:/etc/prometheus:ro" prom/prometheus:v3.2.1 check config /etc/prometheus/prometheus.yml
```

This checks syntax, not live scrape connectivity or alert behavior over time.

## Alert behavior regression test

CI also runs promtool rule tests with synthetic samples. ServiceDown must stay
inactive while healthy, wait for its two-minute pending period, fire with the
expected labels and annotations, then resolve after the target recovers.
This validates the rule without a running Prometheus server. It does not
verify exporter reachability or Alertmanager notification delivery.
