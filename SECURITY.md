# Security Overview – PAI-MHC

## Logging & Data Storage
- Application avoids persisting raw conversation transcripts in plaintext logs. Operational logs capture status codes and identifiers only.
- Emotion classifications, wellness snapshots (PWI), and related metadata are stored together with UTC timestamps to enable audit trails.

## Authentication & Secrets
- OAuth/JWT credentials remain in server memory; refresh uses re-authentication rather than token persistence on disk.
- Client and server secrets (JWT secret, database URI, etc.) are injected via environment variables (`.env`) and never hard-coded.

## Database Practices
- MongoDB collections leverage indexes on `timestamp`, `subject_id`, and `emotions` fields to speed retrieval while limiting full collection scans.
- Chat records include only minimum necessary fields (emotion label, probability, wellness summary, recommendations) to reduce sensitive surface area.

## Least Privilege
- Backend services authenticate requests with bearer tokens issued through `/login`. Unauthorized requests to protected endpoints (`/chat`, `/history`, `/recommendations`, `/wellness/{id}`) return HTTP 401.
- Internal utilities read environment configuration through `pydantic-settings` ensuring consistent enforcement of secret management.

## Secure Client Handling
- Mobile client stores JWT tokens using Expo Secure Store (encrypted at rest) and only attaches them in HTTPS requests to the FastAPI backend.
- Streamlit dashboard holds the JWT in session state for the active browser session; tokens are not written to disk.

## Future Hardening (Planned)
- Integrate centralized structured logging with redaction of user-input fields.
- Enable TLS termination for public endpoints and rotate JWT secrets on a defined schedule.
- Expand audit logging in Mongo (Capped collections or Atlas audit) to track administrative access.


