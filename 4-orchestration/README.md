# Application health checks

The application must serve HTTP `/healthz` on port 8080. Replace the placeholder
image in `deployment.yaml` before deploying to your own test cluster.

The startup probe allows approximately 150 seconds (30 attempts, five seconds
apart) for initialization. Kubernetes delays readiness and liveness probes until
startup succeeds, avoiding premature liveness restarts during initialization.
An application that never becomes healthy is restarted after the startup budget
is exhausted. Adjust this budget using measured startup times.

Readiness controls whether a pod receives Service traffic. Liveness detects an
unhealthy running process. The shared endpoint should check local application
health; a temporary external database outage should not trigger restart loops.
Applications with separate readiness and liveness endpoints should configure
those endpoints accordingly.

## Verify in a test cluster

After configuring your own image and Kubernetes context:

```sh
kubectl apply --dry-run=server -f 4-orchestration/deployment.yaml
kubectl apply -f 4-orchestration/deployment.yaml
kubectl rollout status deployment/myapp-deployment --timeout=300s
kubectl get pods -l app=myapp
kubectl describe pods -l app=myapp
```

Test a deliberately slow-starting application: it should remain unready during
initialization without liveness-triggered restarts, then become ready after
`/healthz` succeeds. Also test an application that never returns success: it
should restart after the startup budget. These require a running test cluster;
manifest parsing alone does not verify runtime behavior.
