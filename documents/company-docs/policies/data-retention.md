# Acme Corp Data Retention Policy

**Policy Number:** SEC-003
**Effective Date:** March 1, 2024
**Last Reviewed:** August 20, 2024
**Document Owner:** Legal & Compliance
**Approved By:** Chief Information Security Officer, General Counsel

## 1. Purpose

This policy establishes requirements for the retention, archival, and disposal of data across Acme Corp systems. It ensures compliance with applicable regulations including GDPR, CCPA, SOC 2, and industry-specific requirements.

## 2. Scope

This policy applies to all data created, collected, stored, or processed by Acme Corp employees, contractors, and third-party service providers, across all systems and media (digital and physical).

## 3. Data Classification

All data at Acme Corp must be classified into one of four tiers:

| Classification | Description | Examples |
|---------------|-------------|----------|
| **Public** | Information intended for public disclosure | Marketing materials, blog posts, open-source code |
| **Internal** | Business information not for external sharing | Wikis, meeting notes, project plans, Slack messages |
| **Confidential** | Sensitive business information with restricted access | Financial reports, contracts, roadmaps, compensation data |
| **Restricted** | Highly sensitive data subject to regulatory requirements | PII, PHI, payment card data, credentials, encryption keys |

Data owners are responsible for classifying their data at creation time. When in doubt, classify at the higher tier.

## 4. Retention Schedules

### 4.1 Customer Data
- **Active customer records:** Duration of relationship plus 1 year after contract termination.
- **Customer PII:** Deleted or anonymized within 90 days of a verified deletion request (GDPR/CCPA).
- **Customer usage analytics:** Aggregated and anonymized after 24 months. Raw event data purged after 13 months.
- **Support tickets:** 3 years after resolution, then archived for an additional 2 years.

### 4.2 Employee Data
- **Active employee records:** Duration of employment plus 7 years post-separation.
- **Recruitment data (hired):** 3 years after hire date.
- **Recruitment data (not hired):** Deleted 1 year after final disposition, unless consent given for talent pool.
- **Payroll and tax records:** 7 years per IRS requirements.

### 4.3 Financial and System Data
- **General ledger, invoices, expense reports:** 7 years. Audit reports: permanent retention.
- **Application logs:** 12 months hot storage, 24 months cold storage.
- **Security event logs (SIEM):** 18 months minimum, 36 months for incidents.
- **Access control logs:** 24 months. Backup data: 90 days daily, 12 months monthly snapshots.

## 5. Deletion Procedures

Data exceeding its retention period must be permanently deleted within 30 days. Data subject requests (GDPR Article 17, CCPA) must be acknowledged within 48 hours and fulfilled within 30 calendar days. The Privacy team coordinates cross-system deletion and provides confirmation to the requestor.

**Secure Disposal:** Digital media requires cryptographic erasure or NIST 800-88 compliant wiping. Physical media requires cross-cut shredding (P-4 or higher). Hardware disposal requires a certificate of destruction from approved vendors.

## 6. Audit and Compliance

- **Quarterly reviews:** Data owners must certify compliance with retention schedules quarterly.
- **Annual audit:** Internal Audit conducts an annual data retention audit, reported to the Audit Committee.
- **Legal holds:** When litigation is anticipated, the Legal team issues a preservation notice. All automated deletion for affected data must be suspended until the hold is released.
- **Regulatory reporting:** Compliance maintains records of all deletion activities for regulatory inquiries.

## 7. Exceptions

Exceptions require written approval from both the CISO and General Counsel. All exceptions are reviewed annually and documented in the Policy Exception Register.

---

*For questions about data retention, contact the Privacy team at privacy@acmecorp.com or file a request in the #data-governance Slack channel.*
