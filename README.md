# End-to-End DevOps Pipeline

A reference architecture showing how Terraform, Ansible, Jenkins, Kubernetes, and Prometheus/Grafana work together as a complete DevOps pipeline — from infrastructure provisioning to deployment automation to monitoring.

## What this demonstrates

This repo ties together the individual components from my other repositories into one coherent workflow:

1. **Provision** infrastructure on AWS using Terraform ([terraform-aws-vpc](https://github.com/nagendrapandiripalli/terraform-aws-vpc))
2. **Configure** servers and deploy the application using Ansible ([ansible-app-deployment](https://github.com/nagendrapandiripalli/ansible-app-deployment))
3. **Automate** build, test, and deployment using a Jenkins CI/CD pipeline ([jenkins-cicd-pipeline](https://github.com/nagendrapandiripalli/jenkins-cicd-pipeline))
4. **Orchestrate** containers using Kubernetes manifests ([k8s-deployment-manifests](https://github.com/nagendrapandiripalli/k8s-deployment-manifests))
5. **Monitor** system health using Prometheus and Grafana ([monitoring-prometheus-grafana](https://github.com/nagendrapandiripalli/monitoring-prometheus-grafana))

## Pipeline Flow

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  Terraform   │ --> │   Ansible    │ --> │   Jenkins    │ --> │  Kubernetes  │ --> │  Prometheus  │
    │  (Provision  │     │  (Configure  │     │  (Build/Test │     │  (Deploy/    │     │  /Grafana    │
    │   AWS infra) │     │   & deploy)  │     │   /Package)  │     │   Scale)     │     │  (Monitor)   │
    └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘

## Structure

    end-to-end-devops-pipeline/
    ├── 1-infrastructure/     # Terraform: provisions VPC, subnets, networking
    ├── 2-configuration/      # Ansible: configures servers, installs dependencies
    ├── 3-cicd/                # Jenkinsfile: build, test, package, deploy
    ├── 4-orchestration/       # Kubernetes manifests: deployment, service, ingress
    ├── 5-monitoring/          # Prometheus + Grafana: metrics, alerts, dashboards
    └── README.md

## How it fits together

1. Terraform provisions the underlying AWS network (VPC, subnets, gateways)
2. Ansible configures the provisioned servers and handles application-level deployment
3. Jenkins automates the CI/CD flow — building, testing, containerizing, and triggering deployment
4. Kubernetes manages container orchestration, scaling, and high availability on top of that infrastructure
5. Prometheus and Grafana continuously monitor the running system, alerting on issues like resource exhaustion before they become critical

## Tech Stack
- **IaC:** Terraform
- **Configuration Management:** Ansible
- **CI/CD:** Jenkins
- **Containers & Orchestration:** Docker, Kubernetes
- **Monitoring:** Prometheus, Grafana
- **Cloud:** AWS

## About
This repository represents the end-to-end DevOps lifecycle I manage in production at Reliance Jio — from infrastructure provisioning through deployment automation to proactive monitoring — consolidated here to demonstrate how these tools work together as a complete system, not just in isolation.