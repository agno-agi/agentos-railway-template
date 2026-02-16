# Incident Response Runbook — Acme Corp

**Owner:** Site Reliability Engineering
**Last Updated:** 2024-12-01
**Review Cadence:** Quarterly

---

## Severity Levels

| Severity | Definition | Example | Response Time | Resolution Target |
|----------|-----------|---------|---------------|-------------------|
| **SEV1** | Complete service outage or data breach affecting all users | API returning 503 globally, database corruption | 5 minutes | 1 hour |
| **SEV2** | Major feature degraded, affecting >25% of users | Payment processing failures, auth service down | 15 minutes | 4 hours |
| **SEV3** | Minor feature degraded, affecting <25% of users | Search latency elevated, report generation slow | 30 minutes | 24 hours |
| **SEV4** | Cosmetic or low-impact issue, no user-facing degradation | Dashboard widget misaligned, non-critical log noise | Next business day | 5 business days |

---

## Escalation Procedures

### Automated Escalation (PagerDuty)

- **0 min:** Alert fires and pages the primary on-call engineer.
- **10 min:** If unacknowledged, escalates to secondary on-call.
- **20 min:** If still unacknowledged, escalates to the engineering manager on rotation.
- **30 min:** VP Engineering is paged automatically for SEV1 only.

### Manual Escalation

If the on-call engineer determines the incident exceeds their expertise:

1. Page the relevant service owner via PagerDuty (`Escalate` button).
2. Post in #incidents with the tag `@incident-commander` to request an IC.
3. For customer-data incidents, immediately notify #security and the DPO (privacy@acme.io).

---

## Incident Commander Responsibilities

The Incident Commander (IC) is the single point of coordination during an active incident.

- **Declare the incident** in #incidents using the `/incident declare` Slack command.
- **Assign roles:** Communications Lead, Technical Lead, Scribe.
- **Establish a war room:** Create a Zoom bridge and pin the link in #incidents.
- **Coordinate work streams:** Ensure parallel investigation tracks do not conflict.
- **Authorize changes:** All production changes during the incident require IC approval.
- **Call the all-clear:** Confirm resolution, update status page, and close the war room.
- **Initiate post-mortem:** Schedule within 48 hours for SEV1/SEV2 incidents.

---

## Communication Templates

### Internal (Slack #incidents)

```
INCIDENT DECLARED — SEV[X]
Service: [service name]
Impact: [description of user impact]
IC: [name]
War Room: [Zoom link]
Status Page: [link]
Next Update: [time]
```

### External (Status Page — Statuspage.io)

```
Title: [Service] — Elevated Error Rates
Body: We are currently investigating elevated error rates affecting [feature].
Our engineering team is actively working on a resolution. We will provide
an update within [30 minutes / 1 hour].
```

### Executive Update (email to leadership@acme.io)

```
Subject: [SEV1/SEV2] Incident Update — [short description]
- Started: [timestamp UTC]
- Duration: [elapsed time]
- Impact: [user-facing impact, estimated affected users]
- Root Cause: [known / under investigation]
- Current Status: [mitigating / resolved / monitoring]
- ETA to Resolution: [estimate]
```

---

## Post-Mortem Process

All SEV1 and SEV2 incidents require a blameless post-mortem.

1. **Timeline:** IC or Scribe assembles a minute-by-minute timeline from logs and Slack.
2. **Root Cause Analysis:** Use the "5 Whys" technique to identify contributing factors.
3. **Action Items:** Each action item must have an owner, a priority, and a due date.
4. **Review Meeting:** Held within 48 hours. Attendees: IC, Tech Lead, affected team leads.
5. **Publication:** Post-mortem document is stored in Confluence under `Engineering > Post-Mortems` and linked in #engineering.

### Post-Mortem Document Template

| Section | Content |
|---------|---------|
| Summary | One-paragraph description of the incident |
| Impact | Users affected, duration, revenue impact if applicable |
| Timeline | Timestamped sequence of events |
| Root Cause | Technical root cause and contributing factors |
| What Went Well | Effective response actions |
| What Went Poorly | Gaps in detection, response, or tooling |
| Action Items | Table: action, owner, priority, due date, JIRA ticket |

---

## SLA Targets by Severity

| Severity | Detection | Acknowledgment | Mitigation | Resolution | Post-Mortem |
|----------|-----------|----------------|------------|------------|-------------|
| SEV1 | < 2 min | < 5 min | < 30 min | < 1 hr | Within 48 hrs |
| SEV2 | < 5 min | < 15 min | < 1 hr | < 4 hrs | Within 72 hrs |
| SEV3 | < 15 min | < 30 min | < 4 hrs | < 24 hrs | Optional |
| SEV4 | < 1 hr | Next biz day | — | < 5 biz days | Not required |
