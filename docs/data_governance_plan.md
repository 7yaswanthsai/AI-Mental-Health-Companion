# Data Governance & Security Plan (HIPAA / GDPR)

## Overview
The PAI-MHC system handles sensitive user data such as chat conversations, emotional state, and biometric metrics (heart rate, sleep data). This plan ensures compliance with HIPAA and GDPR standards.

## Data Collected
- Chat and emotional context
- Physiological data from wearables (e.g., heart rate, sleep)
- User metadata (age, preferences, app usage)

## Storage Policy
| Data Type | Storage | Security |
|------------|----------|----------|
| Chat text | MongoDB | AES-256 encryption at rest |
| Biometric | PostgreSQL | Encrypted columns + access tokens |
| Model data | MLflow (cloud/local) | Controlled access via IAM roles |

## Data Flow
User → API Gateway (HTTPS) → Microservices → Databases → Analytics / Models

## Compliance Checklist
- ✅ Data minimization – only necessary attributes stored  
- ✅ End-to-end encryption (HTTPS, TLS 1.2+)  
- ✅ User consent and deletion rights (GDPR Art. 17)  
- ✅ Access logs and audit trails  
- ✅ Role-based access control (RBAC)

## Risk Management
- Regular vulnerability scans  
- Database backups every 24 h  
- Masked PII during ML training  
- Signed ML models to prevent tampering

---

📄 *Document Owner:* PAI-MHC Team  
📅 *Last Updated:* October 2025
