# Infrastructure Setup Guide (Phase 1)

## 1. Local Environment Setup
```bash
mkdir PAI_MHC && cd PAI_MHC
python -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows
pip install fastapi uvicorn pymongo psycopg2-binary mlflow 
```

## 2. Databases
- PostgreSQL for biometric and profile data  
- MongoDB for chat history  
- Create Local containers:
```bash
docker run --name pai_postgres -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres
docker run --name pai_mongo -p 27017:27017 -d mongo
```

## 3. Folder Layout
see /docs, /backend, /models, /mlops

## Version Control
```bash
git init
git add .
git commit -m "Phase 1 setup: governance, architecture, infra guide"
```

