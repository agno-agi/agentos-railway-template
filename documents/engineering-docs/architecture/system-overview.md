# System Architecture Overview — Acme Corp

**Owner:** Architecture Review Board
**Last Updated:** 2024-10-28
**Classification:** Internal — Engineering

---

## High-Level Architecture

Acme Corp operates a microservices-based SaaS platform serving B2B customers. The system processes approximately 12,000 requests per second at peak and manages data for over 4,200 enterprise tenants.

The architecture follows a layered approach:

1. **Edge Layer** — CloudFront CDN, WAF, and Route 53 for DNS.
2. **Gateway Layer** — Kong API Gateway handling authentication, rate limiting, and routing.
3. **Service Layer** — Domain-specific microservices communicating via gRPC and async events.
4. **Data Layer** — PostgreSQL (transactional), Redis (caching), Elasticsearch (search), S3 (object storage).
5. **Observability Layer** — Datadog, Grafana, and PagerDuty for monitoring, dashboards, and alerting.

---

## Service Topology

### API Gateway (Kong)

- Handles all external HTTP traffic on port 443.
- Enforces OAuth2 token validation and API key authentication.
- Applies per-tenant rate limiting (configurable via admin API).
- Routes requests to downstream services based on path prefix.

### Core Services

| Service | Language | Purpose | Replicas (Prod) |
|---------|----------|---------|-----------------|
| `acme-api` | Python (FastAPI) | REST API for client applications | 8 |
| `acme-auth` | Go | Authentication, token issuance, SSO | 4 |
| `acme-billing` | Python (FastAPI) | Subscription management, Stripe integration | 3 |
| `acme-notifications` | Node.js | Email, SMS, push notifications | 3 |
| `acme-worker` | Python (Celery) | Background job processing | 6 |
| `acme-search` | Python (FastAPI) | Full-text and semantic search | 4 |
| `acme-analytics` | Go | Event ingestion and metrics aggregation | 4 |

### Inter-Service Communication

- **Synchronous:** gRPC with mutual TLS between services within the mesh (Istio).
- **Asynchronous:** Amazon SQS for job queues; Amazon SNS for fan-out event notifications.
- **Event Bus:** Kafka cluster (3 brokers) for high-throughput event streaming between analytics, billing, and notification services.

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React, TypeScript | React 18, TS 5.3 |
| API Framework | FastAPI | 0.109 |
| Auth Service | Go standard library + chi router | Go 1.22 |
| Database (primary) | PostgreSQL + pgvector | 16.1 |
| Cache | Redis Cluster | 7.2 |
| Search | Elasticsearch | 8.12 |
| Message Queue | Amazon SQS / SNS | Managed |
| Event Streaming | Apache Kafka (MSK) | 3.6 |
| Object Storage | Amazon S3 | Managed |
| Container Runtime | Docker | 24.x |
| Orchestration | Kubernetes (EKS) | 1.29 |
| Service Mesh | Istio | 1.20 |
| CI/CD | GitHub Actions + ArgoCD | Latest |
| IaC | Terraform | 1.7 |

---

## Deployment Infrastructure (Kubernetes)

All services run on Amazon EKS across three availability zones in `us-east-1`.

### Cluster Topology

- **Production cluster:** 24 nodes (m6i.2xlarge), autoscaling 18-36 nodes.
- **Staging cluster:** 8 nodes (m6i.xlarge), autoscaling 4-12 nodes.
- **Namespace isolation:** Each service runs in its own namespace with network policies.

### Deployment Model

- All deployments use Kubernetes `Deployment` resources with rolling update strategy.
- ArgoCD syncs manifests from the `k8s-manifests` repository (GitOps).
- Horizontal Pod Autoscaler (HPA) scales based on CPU (target 60%) and custom metrics (request rate).

### Networking

- Istio service mesh provides mTLS, traffic management, and circuit breaking.
- External traffic enters through AWS ALB Ingress Controller.
- Internal DNS resolution via CoreDNS with service discovery (`<service>.<namespace>.svc.cluster.local`).

---

## Monitoring and Observability

### Metrics

- **Datadog Agent** runs as a DaemonSet, collecting container and host metrics.
- **StatsD** integration for custom application metrics (request counts, latencies, business events).
- **Key dashboards:** API Performance, Database Health, Queue Depths, Billing Pipeline, Tenant Usage.

### Logging

- All services emit structured JSON logs to stdout.
- Fluent Bit (DaemonSet) forwards logs to Datadog Log Management.
- Log retention: 30 days hot, 90 days warm (S3 archive), 1 year cold (Glacier).

### Tracing

- Distributed tracing via OpenTelemetry SDK, exported to Datadog APM.
- Trace sampling: 100% for errors, 10% for successful requests, 100% for requests > 1s.

### Alerting

- PagerDuty integration with Datadog monitors.
- Alert routing based on service ownership tags.
- Runbook links embedded in every alert definition.

---

## Key Design Decisions

| Decision | Rationale | Date | ADR |
|----------|-----------|------|-----|
| PostgreSQL over DynamoDB | Need for complex joins, ACID transactions, and pgvector for AI features | 2023-03 | ADR-012 |
| gRPC for inter-service calls | 3x throughput improvement over REST for internal calls; strong typing via protobuf | 2023-06 | ADR-018 |
| Kafka over pure SQS/SNS | Required replay capability and ordered event processing for billing pipeline | 2023-09 | ADR-024 |
| Istio service mesh | Unified mTLS, traffic splitting for canary deploys, and observability without code changes | 2024-01 | ADR-031 |
| Multi-AZ with single region | Latency requirements favor single region; DR plan uses cross-region S3 replication and RDS read replicas in us-west-2 | 2024-04 | ADR-035 |
| Monorepo for Python services | Simplified dependency management and shared library code; Go services remain in separate repos | 2024-07 | ADR-041 |
