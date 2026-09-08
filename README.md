# Personal AI Assistant

![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-E10098?style=for-the-badge&logo=langchain&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-6566F1?style=for-the-badge&logo=openai&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![OpenShift](https://img.shields.io/badge/OpenShift-EE0000?style=for-the-badge&logo=red-hat-openshift&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)

An enterprise-grade, conversational AI personal assistant web application built with a Microservices Architecture. Powered by LangGraph agent orchestration, it connects directly to Google Workspace services (Calendar, Gmail, Tasks) and external web search, enforced by **deterministic safety policies, conflict detection, and autonomy gating**.

The application manages schedules, emails, and tasks while maintaining persistent memory across sessions. It is containerized with Docker and designed for enterprise deployment on Red Hat OpenShift and Kubernetes.

---

## Key Capabilities & Architectural Innovations

### 1. Confidence-Gated Autonomy Engine (`risk_engine.py`)
To prevent autonomous LLM agents from executing risky or destructive actions without oversight, the system implements a **deterministic risk evaluation layer**:
- **Zero-LLM Decision Path:** Risk level calculation cannot be bypassed or hallucinated by the model.
- **Three Autonomy Tiers:**
  - **`LOW RISK` (`AUTO_EXECUTE`)**: Read-only actions (viewing calendar, checking free slots, conflict scanning) execute immediately.
  - **`MEDIUM RISK` (`CONFIRM_FIRST`)**: Creating non-conflicting events or updating minor details stages a pending action and requests explicit user approval.
  - **`HIGH RISK` (`ALWAYS_ASK`)**: Irreversible actions (event deletions), rescheduling (time modifications), or scheduling conflicting events trigger high-risk warnings and require explicit user approval.
- **Pending Action Lifecycle:** Gated tool calls stage arguments in an in-memory store assigning a short unique `action_id`. Execution only occurs when `approve_pending_action` is called. If the user declines, `reject_pending_action` cancels the action safely.

### 2. Deterministic Priority Scoring Engine (`priority_engine.py`)
Replaces fuzzy LLM judgments with a transparent, rule-based mathematical scoring model (0–100):
- **Factors Evaluated:**
  1. **Event Importance & Category** (Interviews, Deadlines, Client Meetings vs. Team Syncs, Personal Tasks, Workouts, Optional Events).
  2. **Urgency & Keyword Analysis** (Urgent, ASAP, Critical, etc.).
  3. **Deadline Proximity Decay** (Dynamic scaling based on hours remaining until the event).
  4. **User-Defined Priority Overrides**.
- **Conflict Resolution Guidance:** When scheduling collisions occur, the engine compares priority scores between competing events and provides deterministic trade-off recommendations to the user.

### 3. Deterministic Calendar Conflict Detection
- Scans existing schedules to identify overlapping time intervals before event creation or rescheduling.
- Dedicated `check_calendar_conflicts` tool allows users to proactively inspect daily or multi-day calendars for scheduling clashes.

### 4. Advanced LangGraph Multi-Agent Architecture
- **Smart Router Node:** Evaluates incoming user queries and delegates tasks to specialized domain agents:
  - **Calendar Expert Agent** (Event management, conflict checking, free slot finder, priority ranking, autonomy gates)
  - **Email Expert Agent** (Gmail search, autonomous draft generation, preview confirmation before sending)
  - **Task Expert Agent** (Google Tasks CRUD with natural language due date parsing)
  - **Search Expert Agent** (Real-time online information retrieval via Tavily with mandatory source citations)
  - **Conversational Node** (General chit-chat and context continuity)
- **Persistent State & Checkpoints:** Uses SQLite to store conversation history and checkpoints, allowing users to resume or switch conversations across sessions.

---

## Architecture Diagram

```mermaid
graph TD
    User["User (Web Interface)"] <--> Frontend["Frontend (Next.js / Tailwind CSS)"];
    Frontend <-->|HTTP / JSON (REST)| Backend["Backend API (FastAPI)"];
    
    subgraph "Backend Core"
        Router{"Smart Router (LangGraph)"};
        Backend --> Router;
        
        Router --> Calendar[Calendar Agent];
        Router --> Email[Email Agent];
        Router --> Search[Search Agent];
        Router --> Tasks[Task Agent];
        
        subgraph "Deterministic Safety & Scoring"
            RiskEngine["Risk Engine (Confidence Gate)"]
            PriorityEngine["Priority Scoring Engine"]
            ConflictDetector["Conflict Detection"]
        end
        
        Calendar --> RiskEngine
        Calendar --> PriorityEngine
        Calendar --> ConflictDetector
        
        RiskEngine -->|Pending Actions / Approval| Calendar
        
        Calendar <-->|OAuth2| GCal["Google Calendar API"];
        Email <-->|OAuth2| GMail["Gmail API"];
        Tasks <-->|OAuth2| GTasks["Google Tasks API"];
        Search <--> Tavily["Tavily Search API"];
        
        DB[("SQLite (LangGraph Checkpoints)")]
        Router -.->|Persist State| DB
    end
```

---

## Tech Stack

#### Backend
- **Framework:** FastAPI
- **Agent Orchestration:** LangGraph & LangChain
- **LLM Providers:** OpenRouter (`nvidia/nemotron-3.5-lightning:free`) or Groq (`openai/gpt-oss-120b`, `llama-3`)
- **Safety & Scoring:** Custom deterministic modules (`risk_engine.py`, `priority_engine.py`)
- **Persistence:** SQLite (`conversations.sqlite`)
- **Web Server:** Uvicorn
- **Google Integrations:** `google-api-python-client`, `google-auth-oauthlib`, `parsedatetime`, `python-dateutil`

#### Frontend
- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **UI Components & Styling:** React & Tailwind CSS
- **Features:** Multi-session sidebar, real-time thinking states, formatted markdown/markup responses, action confirmation dialogues

#### DevOps & Infrastructure
- **Containerization:** Docker & Docker Compose
- **Cloud Orchestration:** Red Hat OpenShift / Kubernetes
- **Web Server:** Nginx (production container reverse proxy)

---

## Installation & Setup

### Option A: Local Development Setup

#### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/berkyalkn/ai-personal-assistant.git
cd ai-personal-assistant

# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\activate      # Windows
# or: source venv/bin/activate # macOS/Linux
```

#### 2. Configure Backend Environment
Create a `.env` file in the `server/` directory:
```env
# Choose OpenRouter or Groq (or both)
OPENROUTER_API_KEY="your_openrouter_api_key"
GROQ_API_KEY="your_groq_api_key"

# Search API
TAVILY_API_KEY="your_tavily_api_key"
```

#### 3. Google OAuth Setup
1. Download your OAuth 2.0 Client ID JSON from the Google Cloud Console with Calendar, Gmail, and Tasks API scopes enabled.
2. Ensure `http://localhost:8090/oauth2callback` is added as an **Authorized Redirect URI**.
3. Save the file as `server/credentials.json`.

#### 4. Install Dependencies
```bash
# Backend dependencies
cd server
pip install -r requirements.txt

# Frontend dependencies
cd ../client
npm install
```

#### 5. Run the Application
**Terminal 1 — Backend:**
```bash
cd server
uvicorn main:app_fastapi --host 127.0.0.1 --port 5001 --reload
```

**Terminal 2 — Frontend:**
```bash
cd client
npm run dev
```

Open your browser at `http://localhost:3000`.

---

### Option B: Docker Compose Setup

```bash
# Build and launch all services
docker-compose up --build
```
- First-time authentication: Follow the OAuth URL printed in the backend console to generate `token.json`.
- Access the web interface at `http://localhost:3000`.

---

## Running Automated Tests

The deterministic engines include a comprehensive test suite (72 unit tests):

```bash
cd server
pytest test_risk_engine.py test_priority_engine.py -v
```

**Test Coverage Highlights:**
- **`test_risk_engine.py` (23 tests):** Evaluates risk classifications for read/write actions, dynamic escalation upon conflicts, reschedule escalation, delete safety defaults, and the full lifecycle of the pending action store.
- **`test_priority_engine.py` (49 tests):** Validates category classifiers, importance calculations, keyword urgency weights, deadline proximity decay, tie-breakers, and overlap interval detection.

---

## Cloud Deployment (Red Hat OpenShift)

Production-ready Kubernetes manifests for Red Hat OpenShift are located in the `openshift/` directory:

```bash
# 1. Login to OpenShift and create a project
oc new-project personal-assistant

# 2. Create secrets for backend environment and Google credentials
oc create secret generic backend-secrets --from-env-file=server/.env
oc create secret generic google-credentials --from-file=server/credentials.json

# 3. Create persistent storage (PVC) for SQLite database and tokens
oc apply -f openshift/storage.yaml

# 4. Deploy Backend
oc apply -f openshift/backend.yaml

# 5. Build & Deploy Frontend container
cd client
docker build --build-arg NEXT_PUBLIC_API_URL=http://YOUR_BACKEND_ROUTE_URL -t youruser/personal-assistant-frontend:v1 .
docker push youruser/personal-assistant-frontend:v1
oc apply -f openshift/frontend.yaml
```

---

## Example Usage & Confirmation Flows

### 1. Creating an Event with Conflict Detection & Risk Gating
> **User:** "Schedule a Client Review meeting tomorrow from 3 PM to 4 PM."  
> **Assistant:**  
> ⚠️ **Confirmation Required (High Risk)**  
> This event conflicts with your existing *Team Sync (3:30 PM - 4:30 PM)*.  
> - **Client Review:** Priority Score 85 (High Importance)  
> - **Team Sync:** Priority Score 55 (Medium Importance)  
> - **Recommendation:** Client Review has higher priority.  
> To confirm this action, please reply **"Confirm action a1b2c3d4"**.

### 2. Approving Pending Actions
> **User:** "Yes, go ahead and confirm a1b2c3d4."  
> **Assistant:** Action a1b2c3d4 approved and executed successfully. The event 'Client Review' has been created for tomorrow at 3:00 PM.

### 3. Safe Deletions
> **User:** "Delete my interview on Friday."  
> **Assistant:** 🗑️ Deleting 'Interview with Acme Corp' is irreversible. Autonomy Level: **ALWAYS_ASK** (ID: `f9e8d7c6`). Would you like me to proceed?