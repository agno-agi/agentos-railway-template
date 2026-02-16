# Deployment Runbook — Acme Corp

**Owner:** Platform Engineering
**Last Updated:** 2024-11-15
**Applies To:** All production services (acme-api, acme-web, acme-worker)

---

## Deployment Strategy: Blue-Green

Acme Corp uses a blue-green deployment model. Two identical production environments (blue and green) run behind a shared load balancer. At any given time, one environment serves live traffic while the other remains idle for the next release.

- **Active environment** receives 100% of traffic via the ALB weighted target group.
- **Idle environment** is updated, tested, and then promoted by shifting the ALB weight.
- DNS cutover is handled automatically by the deployment pipeline; no manual Route 53 changes are required.

---

## Pre-Deploy Checklist

Before initiating a production deployment, confirm every item below:

- [ ] All CI checks pass on the release branch (unit, integration, contract tests).
- [ ] Database migrations have been applied to staging and verified.
- [ ] Feature flags for unreleased functionality are defaulted to OFF.
- [ ] The on-call engineer has been notified in #deployments Slack channel.
- [ ] Change request ticket (JIRA `DEPLOY-*`) is approved by the release manager.
- [ ] Rollback procedure has been reviewed with at least one other engineer.
- [ ] Artifact SHA has been promoted from staging — never build directly for prod.

---

## Deployment Steps

1. Open the deployment dashboard at `https://deploy.internal.acme.io`.
2. Select the target service and the promoted artifact SHA.
3. Click **Deploy to Idle Environment**. The pipeline will:
   - Pull the container image from ECR.
   - Run Terraform apply for any infrastructure changes.
   - Start the new task definition in the idle ECS cluster.
   - Wait for health checks to pass (HTTP 200 on `/healthz`).
4. Once health checks are green, click **Shift Traffic** to move 10% of traffic to the new environment.
5. Monitor dashboards for 5 minutes. If metrics are stable, proceed to 50%, then 100%.
6. Mark the deployment as **Complete** in the dashboard.

---

## Smoke Test Checklist

Run immediately after traffic shift begins:

- [ ] `GET /healthz` returns `200 OK` with build SHA matching the release.
- [ ] `POST /api/v2/auth/token` returns a valid JWT within 200ms.
- [ ] `GET /api/v2/users/me` returns the authenticated user profile.
- [ ] Background job queue depth is stable (check Grafana panel "Worker Queue Depth").
- [ ] No new ERROR-level log entries in Datadog within the first 2 minutes.

---

## Rollback Procedure

**Trigger:** Rollback if any of the following occur within 15 minutes of traffic shift:

- p99 latency exceeds 800ms (baseline is ~350ms).
- Error rate exceeds 1% of total requests.
- Any SEV1 or SEV2 alert fires.

**Steps:**

1. In the deployment dashboard, click **Rollback — Shift to Previous Environment**.
2. Traffic returns to the previously active environment within 30 seconds.
3. Verify rollback by confirming the build SHA on `/healthz` matches the prior release.
4. Post in #incidents with the rollback reason and link to the deploy ticket.
5. The failed release must go through a full root-cause analysis before re-deployment.

---

## Post-Deploy Monitoring

For 30 minutes after a completed deployment, the deploying engineer must monitor:

| Metric | Dashboard | Threshold |
|--------|-----------|-----------|
| p50 / p99 latency | Grafana — API Latency | p99 < 800ms |
| Error rate (5xx) | Datadog — Error Budget | < 0.5% |
| CPU / Memory | Grafana — ECS Resources | CPU < 70%, Mem < 80% |
| Queue depth | Grafana — Worker Queue | < 500 messages |
| Active connections | Grafana — RDS Connections | < 180 (max 200) |

---

## Emergency Contacts

| Role | Name | Phone | Slack |
|------|------|-------|-------|
| Release Manager | Dana Chen | +1-555-0142 | @dana.chen |
| Platform Lead | Marcus Rivera | +1-555-0198 | @marcus.rivera |
| SRE On-Call | (rotation) | PagerDuty | @sre-oncall |
| VP Engineering | Priya Sharma | +1-555-0117 | @priya.sharma |
