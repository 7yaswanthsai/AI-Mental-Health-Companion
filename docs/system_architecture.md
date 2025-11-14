# System Architecture Blueprint

## Overview
The PAI-MHC follows a **microservices-based architecture** with separate components for chat, analytics, and recommendation.

## Components
1. **Frontend (React Native)** – Chat UI and mood dashboard  
2. **Backend APIs (FastAPI)** – Handles chat, emotion inference, and data storage  
3. **Databases**  
   - MongoDB → chat logs  
   - PostgreSQL → biometric data, user profiles  
4. **AI Layer** – NLP + Fusion + Recommendation models  
5. **MLOps Stack** – MLflow + Docker + CI/CD for retraining  
6. **Security Layer** – JWT auth, HTTPS, encryption at rest

## Data Flow Diagram
User App → API Gateway → Microservices → Databases ↔ ML Layer ↔ Visualization Dashboard

## Deployment Layout
- Dev / Test / Prod environments
- Cloud (AWS / GCP) or local Docker
- Load balancer + Auto-scaling (2 replicas per service)
