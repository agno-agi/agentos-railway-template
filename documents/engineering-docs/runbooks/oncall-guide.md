# On-Call Guide — Acme Corp

**Owner:** Site Reliability Engineering
**Last Updated:** 2024-11-20
**Applies To:** All engineering teams participating in on-call rotations

---

## Rotation Schedule

On-call rotations run **Monday 09:00 UTC to the following Monday 09:00 UTC** (7 days).

| Team | Rotation Size | Primary + Secondary | Schedule Tool |
|------|--------------|---------------------|---------------|
| Platform | 6 engineers | Yes | PagerDuty — `platform-oncall` |
| Backend API | 8 engineers | Yes | PagerDuty — `backend-oncall` |
| Data Pipeline | 4 engineers | Primary only | PagerDuty — `data-oncall` |
| Frontend | 5 engineers | Primary only | PagerDuty — `frontend-oncall` |

- Rotations are managed in PagerDuty. Swap requests must be submitted at least 48 hours in advance.
- Each engineer is on-call approximately once every 6-8 weeks.
- Holiday coverage is coordinated in #oncall-swaps by November 1 each year.

---

## Alert Triage Process

When an alert fires, follow this decision tree:

1. **Acknowledge** the alert in PagerDuty within 5 minutes.
2. **Assess severity** using the [Incident Response Runbook](./incident-response.md) severity definitions.
3. **Check dashboards** — open the linked Grafana dashboard from the alert payload.
4. **Determine if action is required:**
   - If the alert is a known transient spike (e.g., deploy-related), monitor for 5 minutes and resolve if it self-heals.
   - If the alert indicates a real issue, begin troubleshooting or escalate.
5. **Document** your triage decision in the PagerDuty alert notes.

---

## Common Alerts and Remediation

### High API Latency (`api-p99-latency-high`)

- **Threshold:** p99 > 800ms for 5 minutes
- **Common Causes:** Database connection pool exhaustion, upstream dependency slowdown
- **Remediation:**
  1. Check RDS connection count in Grafana (`RDS Connections` panel).
  2. If connections > 180, restart the API service: `kubectl rollout restart deployment/acme-api -n production`.
  3. If RDS is healthy, check upstream services in the service mesh dashboard.

### Worker Queue Backlog (`worker-queue-depth-high`)

- **Threshold:** Queue depth > 1000 messages for 10 minutes
- **Common Causes:** Worker pod crash loop, Redis connection failure
- **Remediation:**
  1. Check worker pod status: `kubectl get pods -n production -l app=acme-worker`.
  2. If pods are in CrashLoopBackOff, check logs: `kubectl logs -n production -l app=acme-worker --tail=100`.
  3. If Redis is unreachable, verify the ElastiCache cluster status in AWS Console.

### Database CPU High (`rds-cpu-utilization-high`)

- **Threshold:** CPU > 85% for 10 minutes
- **Common Causes:** Long-running query, missing index, connection storm
- **Remediation:**
  1. Connect to the read replica and run: `SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC LIMIT 10;`
  2. Identify and terminate long-running queries if safe: `SELECT pg_terminate_backend(pid);`
  3. If caused by a missing index, file a JIRA ticket and escalate to the database team.

### Certificate Expiry Warning (`tls-cert-expiring`)

- **Threshold:** Certificate expires within 14 days
- **Remediation:**
  1. Certificates are managed by cert-manager in Kubernetes.
  2. Check cert-manager logs: `kubectl logs -n cert-manager deployment/cert-manager`.
  3. If auto-renewal failed, manually trigger: `kubectl delete certificate <cert-name> -n production` (cert-manager will recreate it).

---

## Escalation Paths

| Situation | Escalate To | Method |
|-----------|------------|--------|
| Cannot diagnose within 30 min | Secondary on-call | PagerDuty escalation |
| Database issue | DBA team (@db-oncall) | Slack #dba-support |
| Infrastructure / AWS issue | Platform team (@platform-oncall) | PagerDuty |
| Security concern | Security team (@security-oncall) | PagerDuty + Slack #security |
| Customer-reported outage | Customer Success + Engineering Manager | Slack #escalations |

---

## Handoff Procedures

At the end of your on-call shift:

1. **Write a handoff summary** in #oncall-handoff covering:
   - Active or recently resolved incidents.
   - Alerts that fired but were transient (with context).
   - Any ongoing investigations or follow-up items.
2. **Update PagerDuty** — confirm the next on-call engineer is correct.
3. **Transfer context** — if an incident is ongoing, brief the incoming engineer on a 15-minute call.

---

## Tools Access

Ensure you have access to the following before your on-call shift:

| Tool | URL | Access Request |
|------|-----|----------------|
| PagerDuty | pagerduty.com/acme | IT Help Desk (JIRA `IT-ACCESS`) |
| Grafana | grafana.internal.acme.io | Auto-provisioned via SSO |
| Datadog | app.datadoghq.com | IT Help Desk (JIRA `IT-ACCESS`) |
| AWS Console | acme-prod.signin.aws.amazon.com | IAM request via #platform-support |
| Kubernetes | Via `kubectl` + VPN | Platform team provisions kubeconfig |
| Statuspage | manage.statuspage.io | Communications team grants access |

---

## Expectations and Compensation

### Expectations

- Acknowledge alerts within **5 minutes** during on-call hours.
- Maintain a reliable internet connection and have your laptop accessible.
- Stay within areas with cell reception (no flights, remote hikes, etc.).
- Limit alcohol consumption to remain response-capable.
- If you are unable to respond for any period, arrange coverage with a teammate and update PagerDuty.

### Compensation

| Component | Amount |
|-----------|--------|
| Weekly on-call stipend | $500 USD |
| Weeknight page (10pm-7am local) | +$75 per incident |
| Weekend / holiday page | +$100 per incident |
| Incident lasting > 2 hours | +$150 bonus |
| Comp time for overnight incidents | 4 hours flex time next business day |

Compensation is processed through the monthly payroll cycle. Log incidents in the #oncall-compensation Slack channel for finance tracking.
