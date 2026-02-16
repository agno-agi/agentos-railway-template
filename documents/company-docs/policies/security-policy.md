# Acme Corp Information Security Policy

**Policy Number:** SEC-001
**Effective Date:** January 15, 2024
**Last Reviewed:** October 1, 2024
**Document Owner:** Information Security
**Approved By:** Chief Information Security Officer

## 1. Purpose

This policy defines information security requirements for all Acme Corp employees, contractors, and third parties with access to company systems. It establishes baseline controls to protect the confidentiality, integrity, and availability of information assets.

## 2. Access Controls

All access must follow the principle of least privilege. Elevated or administrative access requires documented justification and manager approval. Access permissions are reviewed quarterly by system owners. Terminated employee accounts must be disabled within 4 hours of HR notification. Role changes trigger an access review within 5 business days. Service accounts must have designated owners and use non-interactive authentication; shared credentials are prohibited.

## 3. Authentication Requirements

### 3.1 Single Sign-On (SSO)
All SaaS applications and internal systems must integrate with the corporate SSO provider (Okta). Applications that do not support SSO require a security exception approved by InfoSec.

### 3.2 Multi-Factor Authentication (MFA)
MFA is mandatory for all employees and contractors. Approved methods: hardware security keys (YubiKey, preferred), authenticator apps (Okta Verify, Google Authenticator), and push notifications. SMS-based MFA is **not permitted** due to SIM-swapping risks.

### 3.3 Password Policy
Minimum 14 characters. Must not appear in known breach databases. Password managers (1Password, company-provisioned) are required. Rotation every 90 days for privileged accounts; annually for standard accounts.

## 4. Device Security

All devices accessing Acme Corp systems must run a supported OS with automatic updates, have CrowdStrike Falcon EDR installed, use full-disk encryption (FileVault/BitLocker), and be enrolled in MDM (Jamf or Intune). Personal devices (BYOD) may access company email and Slack only; access to production systems or Confidential/Restricted data from personal devices is prohibited.

## 5. Incident Reporting

Report suspected security incidents immediately via #security-incidents on Slack, security@acmecorp.com, or +1-555-SEC-TEAM for after-hours critical incidents. Do not attempt to investigate independently. Severity classifications:

| Severity | Description | Response Time |
|----------|-------------|---------------|
| P1 - Critical | Active breach, data exfiltration, ransomware | 15 minutes |
| P2 - High | Compromised credentials, malware detection | 1 hour |
| P3 - Medium | Phishing attempts, policy violations | 4 hours |
| P4 - Low | Suspicious emails, scan alerts | 24 hours |

## 6. Acceptable Use

Company systems are for business purposes. Limited personal use is permitted if it does not violate policy or create liability. Prohibited activities include: installing unauthorized software, connecting unauthorized network devices, storing company data on personal cloud storage, sharing credentials, and circumventing security controls including VPN split tunneling.

## 7. Network Security and Data Handling

All remote access must use the corporate VPN (Tailscale) or approved zero-trust paths. Production networks are isolated from corporate and guest networks. Restricted data must be encrypted at rest (AES-256) and in transit (TLS 1.2+). Confidential data must not be transmitted via email without encryption. All data must be stored in approved, company-managed systems only.

## 8. Training and Compliance

All employees must complete Security Awareness Training within 30 days of hire and annually thereafter. Phishing simulations run monthly; employees who fail two consecutive simulations must complete additional training. Compliance is audited annually as part of SOC 2 Type II certification.

---

*For security questions or to report an incident, contact InfoSec at security@acmecorp.com or in #security on Slack.*
