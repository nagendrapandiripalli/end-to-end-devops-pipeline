# Jenkins operations

The sample pipeline requires a Maven application with a Dockerfile, registry
credentials configured on the agent, and an authorized Kubernetes context.
Replace the example repository and registry before running it.

Deployment waits up to 300 seconds for the Kubernetes rollout. An image update
alone does not prove a deployment is healthy. A failed or timed-out rollout
returns a nonzero exit code and fails the Jenkins stage. Automatic rollback is
not enabled: inspect pod events and logs before selecting a known-good image.

Validate in a test environment with a healthy image and then a deliberately
invalid image. The healthy rollout should succeed; the invalid image should
fail the stage within the timeout. This requires Jenkins and a test cluster.
