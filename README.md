## TL;DR
A production-inspired authentication and onboarding backend that demonstrates:
- OTP-based login
- State-driven user onboarding (LIMITED → FULL)
- JWT access + refresh token issuance
- Redis-backed rate limiting
- Async, layered architecture with FastAPI

📄 API Docs: (https://finguard-backend-4o9g.onrender.com/docs#/Auth/submit_phone_v1_auth_signup_phone_post)  
📦 Deployed on Render  
🐳 Dockerized for local & prod parity


# user-onboarding-service

**Production-inspired backend authentication service** built with FastAPI and async SQLAlchemy.  
Demonstrates OTP-based authentication, state-driven onboarding, token issuance, and modular architecture inspired by real-world product flows.

## 🎯 Purpose
Most real-world authentication systems go beyond simple email/password flows.
This project is inspired by patterns commonly seen in fintech and high-security products, such as OTP-based signup and state-driven onboarding.

It demonstrates how production backend systems handle:
- Multi-step onboarding
- Explicit account state transitions
- Partial users flows
- Security and abuse prevention

The goal is to showcase how complex authentication and onboarding flows can be orchestrated in a modular, testable, and async-first backend architecture.



---

## 🚀 Key Features

- State-driven authentication & onboarding engine
- OTP-based identity verification with abuse protection
- Explicit account lifecycle: UNVERIFIED → LIMITED → FULL
- JWT access & refresh token model with scoped permissions
- Redis-backed rate limiting for OTP and login attempts
- Async-first, layered architecture

## 🔐 Authentication & Onboarding Flow
The system models real-world signup and login flows as explicit state transitions rather than implicit conditionals.

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
            L6. Login result contract (auth state, account tier, token payload)

 ## API Documentation
Interactive API documentation is available via Swagger UI.

This exposes:
- Auth and onboarding endpoints
- Request/response contracts
- Error and state transition responses

👉 Swagger Link: (https://finguard-backend-4o9g.onrender.com/docs#/Auth/submit_phone_v1_auth_signup_phone_post) 

## Try it in 60 Seconds

This deployment exposes a frictionless demo flow that completes a full OTP-based signup path.

### Demo Rules
- OTP verification is mocked in demo mode
- **OTP value is always:** `000000`
- OTP rate-limits are enforced but reset automatically
- KYC, risk evaluation, and compliance steps are stubbed
- Focus is on backend flow orchestration, not real compliance

---

## End-to-End Signup Flow

### 1. Send OTP (Rate-limit + Abuse Checks)


curl -X POST https://finguard-backend-4o9g.onrender.com/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+15555555555"
  }'


### 2. Verify OTP
curl -X POST https://finguard-backend-4o9g.onrender.com/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+15555555555",
    "otp": "000000"
  }'

### 3. Start Signup (PreUser Creation)

curl -X POST https://finguard-backend-4o9g.onrender.com/v1/auth/signup/phone \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+15555555555"
  }'

### Verify Signup OTP

curl -X POST https://finguard-backend-4o9g.onrender.com/v1/auth/signup/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+15555555555",
    "otp": "000000"
  }'

### 5. Set Password
curl -X POST https://finguard-backend-4o9g.onrender.com/v1/auth/signup/set-password \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+15555555555",
    "password": "StrongPassword@123"
  }'

## Modeled Account Lifecycle
UNVERIFIED (PreUser)
   ↓
OTP Verified
   ↓
Credentials Set
   ↓
LIMITED Account
   ↓
(KYC + Risk Evaluation — Stubbed)
   ↓
FULL Account


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
            L6. Login result contract (auth state, account tier, token payload)


Note: KYC, risk evaluation, and external compliance-related components are intentionally mocked or simplified. The goal of this project is to demonstrate backend system design, flow orchestration, and code structure, not to replicate real-world fintech compliance.








