# FinGuard Backend

**Production-inspired backend authentication service** built with FastAPI and async SQLAlchemy.  
Demonstrates OTP-based authentication, state-driven onboarding, token issuance, and modular architecture inspired by real-world product flows.

## 🎯 Purpose

This project is intended as a backend architecture showcase for learning
and discussion, focusing on authentication, state management, and async service design.


---

## 🚀 Features

- State-driven authentication & onboarding flows  
- OTP-based login and verification  
- Account states: LIMITED → FULL  
- Token-based authentication (JWT)  
- Secure credential and password hashing  
- Rate-limiting using Redis  
- Modular, async-first architecture  
- Stubbed KYC and transaction flows to focus on auth & state management  
 

---
## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-orange?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24-blue?logo=docker&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red?logo=sqlalchemy&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testing-blue?logo=pytest&logoColor=white)
![Docker%20Compose](https://img.shields.io/badge/Docker%20Compose-Orchestration-blue?logo=docker&logoColor=white)



## 📂 Project Structure

.
├── app/

│   ├── api/         
│   ├── auth/           
│   ├── core/           
│   ├── db/            
│   ├── domain/         
│   ├── orchestration/ 
│   ├── repository/    
│   ├── schemas/    
│   ├── services/       
│   └── main.py        
│
├── alembic/            
├── tests/              
├── Dockerfile  
├── docker-compose.yml  
├── pyproject.toml  
└── README.md

This structure separates domain logic, orchestration, and infrastructure concerns
to keep business rules independent from frameworks and external services.


## 🔐 Authentication & Onboarding Flow

1. Phone number submitted
2. Rate-limit and abuse checks
3. OTP issued
4. OTP verified
        │

        ├── Signup Flow
        │
        │   S1. PreUser created (UNVERIFIED, temporary user record)
        │   S2. Credentials set (hashed)
        │   S3. Basic profile completed
        │   S4. Risk gate evaluation
        │   S5. Limited account created
        │   S6. KYC details submitted
        │   S7. KYC verified
        │   S8. Account upgraded to FULL
        │
        └── Login Flow
            L1. Identity lookup
            L2. User status validated (ACTIVE / BLOCKED)
            L3. Account state guard (LIMITED / FULL)
            L4. Step-up check (PIN / secondary auth)
            L5. Token issuance (scoped access + refresh)
            L6. L6. Login result contract (auth state, account tier, token payload)


Note: KYC, risk evaluation, and external compliance-related components are intentionally mocked or simplified. The goal of this project is to demonstrate backend system design, flow orchestration, and code structure, not to replicate real-world fintech compliance.




