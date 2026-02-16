# Q4 2024 Metrics Report — Acme Corp

**Prepared By:** Data & Analytics Team
**Report Period:** October 1 – December 31, 2024
**Distribution:** Engineering Leadership, Product, Finance
**Classification:** Internal — Confidential

---

## Executive Summary

Q4 2024 was a strong quarter for Acme Corp. Annual recurring revenue crossed the $50M milestone, driven by enterprise tier upgrades and a 14% increase in new customer acquisition. Engineering velocity improved with deployment frequency increasing to 18 deploys per week while maintaining a sub-2% change failure rate. Customer satisfaction remained high with an NPS of 62.

---

## Key Business Metrics

### Revenue

| Metric | Q3 2024 | Q4 2024 | QoQ Change |
|--------|---------|---------|------------|
| Annual Recurring Revenue (ARR) | $45.2M | $51.8M | +14.6% |
| Monthly Recurring Revenue (MRR) | $3.77M | $4.32M | +14.6% |
| Average Revenue Per Account (ARPA) | $896 | $1,024 | +14.3% |
| Net Revenue Retention | 112% | 118% | +6pp |
| Expansion Revenue (upsells) | $1.1M | $1.6M | +45.5% |

### Users and Engagement

| Metric | Q3 2024 | Q4 2024 | QoQ Change |
|--------|---------|---------|------------|
| Total Tenants | 3,850 | 4,230 | +9.9% |
| Monthly Active Users (MAU) | 28,400 | 33,100 | +16.5% |
| Daily Active Users (DAU) | 11,200 | 13,800 | +23.2% |
| DAU/MAU Ratio | 39.4% | 41.7% | +2.3pp |
| Avg. Session Duration | 12.3 min | 14.1 min | +14.6% |
| API Calls (monthly avg.) | 142M | 178M | +25.4% |
| Features Adopted per Tenant (avg.) | 4.2 | 4.8 | +14.3% |

---

## Engineering Metrics (DORA)

### Deployment Frequency

| Month | Deploys | Deploys/Week |
|-------|---------|-------------|
| October | 68 | 15.5 |
| November | 74 | 18.5 |
| December | 72 | 18.0 |
| **Q4 Average** | **71.3/mo** | **17.3** |
| Q3 Average | 58.0/mo | 14.5 |

### Lead Time for Changes

| Metric | Q3 2024 | Q4 2024 | Target |
|--------|---------|---------|--------|
| Commit to PR merge | 4.2 hrs | 3.1 hrs | < 4 hrs |
| PR merge to production | 2.8 hrs | 1.9 hrs | < 2 hrs |
| Total lead time | 7.0 hrs | 5.0 hrs | < 6 hrs |

### Change Failure Rate

| Month | Total Deploys | Failed Deploys | Failure Rate |
|-------|--------------|----------------|-------------|
| October | 68 | 2 | 2.9% |
| November | 74 | 1 | 1.4% |
| December | 72 | 1 | 1.4% |
| **Q4 Average** | — | — | **1.9%** |
| Q3 Average | — | — | 3.4% |
| Industry Benchmark (Elite) | — | — | < 5% |

### Mean Time to Recovery (MTTR)

| Severity | Q3 2024 | Q4 2024 | SLA Target |
|----------|---------|---------|------------|
| SEV1 | 38 min | 22 min | < 60 min |
| SEV2 | 2.1 hrs | 1.4 hrs | < 4 hrs |
| SEV3 | 8.5 hrs | 6.2 hrs | < 24 hrs |

### Incident Summary

| Category | Q3 2024 | Q4 2024 |
|----------|---------|---------|
| SEV1 incidents | 2 | 1 |
| SEV2 incidents | 5 | 3 |
| SEV3 incidents | 14 | 11 |
| SEV4 incidents | 38 | 29 |
| Total incidents | 59 | 44 |
| Post-mortems completed | 7 | 4 |
| Action items closed (%) | 82% | 91% |

---

## Infrastructure Metrics

| Metric | Q3 2024 | Q4 2024 |
|--------|---------|---------|
| Uptime (all services) | 99.94% | 99.97% |
| Avg. API p50 latency | 45ms | 42ms |
| Avg. API p99 latency | 380ms | 340ms |
| Database CPU (avg.) | 62% | 58% |
| Monthly AWS spend | $186K | $198K |
| Cost per 1M API calls | $1.31 | $1.11 |

---

## Customer Success Metrics

### Net Promoter Score (NPS)

| Quarter | Promoters | Passives | Detractors | NPS |
|---------|-----------|----------|------------|-----|
| Q1 2024 | 54% | 31% | 15% | 39 |
| Q2 2024 | 58% | 28% | 14% | 44 |
| Q3 2024 | 62% | 24% | 14% | 48 |
| Q4 2024 | 70% | 22% | 8% | **62** |

### Churn and Retention

| Metric | Q3 2024 | Q4 2024 | Target |
|--------|---------|---------|--------|
| Logo churn rate (quarterly) | 2.8% | 2.1% | < 3.0% |
| Revenue churn rate (quarterly) | 1.9% | 1.2% | < 2.0% |
| Gross retention rate | 96.2% | 97.1% | > 95% |
| Net retention rate | 112% | 118% | > 110% |

### Support Metrics

| Metric | Q3 2024 | Q4 2024 |
|--------|---------|---------|
| Total support tickets | 1,842 | 1,654 |
| Avg. first response time | 2.4 hrs | 1.8 hrs |
| Avg. resolution time | 18.3 hrs | 14.1 hrs |
| Customer satisfaction (CSAT) | 4.2 / 5.0 | 4.5 / 5.0 |
| Self-service resolution rate | 34% | 41% |

---

## Q1 2025 Targets

| Area | Metric | Target |
|------|--------|--------|
| Revenue | ARR | $58M |
| Growth | New tenants | 500+ |
| Engineering | Deployment frequency | 20/week |
| Engineering | Change failure rate | < 1.5% |
| Engineering | MTTR (SEV1) | < 20 min |
| Customer | NPS | 65+ |
| Customer | Logo churn | < 2.0% |
| Infrastructure | Uptime | 99.98% |
| Infrastructure | Cost per 1M API calls | < $1.00 |
