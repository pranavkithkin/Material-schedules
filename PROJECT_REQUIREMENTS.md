# 🎯 PROJECT RULES & REQUIREMENTS# AI-Powered Delivery Schedule Tracking Dashboard - Project Requirements

## Material Delivery Dashboard - Complete Development Standards

## PROJECT CONTEXT

**Last Updated:** October 4, 2025

### Material Types to Track (35 items)

---1. PVC Conduits & Accessories

2. Light Fittings (Internal & External)

## 📖 CRITICAL DEVELOPMENT RULES3. Light Fittings (Decorative Light fittings)

4. Cable Gland & Accessories

### Rule #1: Always Use WSL for Python/Git Commands5. Earthing & LPS System

**MANDATORY for all Python and Git operations:**6. GI Conduit & Accessories

7. Cables & Wires

```bash8. Wiring Accessories

# ✅ CORRECT - Run in WSL9. DB

wsl bash -c "cd '/mnt/c/.../9. material delivery dashboard' && source venv/bin/activate && python app.py"10. GRMS

11. Fire Alarm system

# ❌ WRONG - Don't run in PowerShell12. Emergency Lighting system

python app.py13. Structured Cabling System & cctv -low current system

```14. Isolator

15. VRF System

**Why:** SQLite database created in WSL cannot be reliably accessed from Windows Python. Flask MUST run in WSL.16. ERV Unit

17. GI Duct

**Commands that MUST use WSL:**18. Duct Heater

- `python` (any Python script)19. Dampers

- `pip install`20. Air Outlets

- `flask run`  21. Duct Insulation (Thermal)

- `git add/commit/push`22. Duct Insulation (Thermal)(Alternative)

- Database operations23. Duct Insulation (Acoustic)

24. Sealent. Adhesives,Coating & Vapour Barrier

---25. Flexible Duct

26. Aluminum Tape

### Rule #2: Follow Project Structure - No Python Files in Root27. Flexible Duct Connector

**ALL files must follow this structure:**28. Fire Fighting system

29. Fire Extinguisher

```30. PPR pipe and fittings

9. material delivery dashboard/31. Condensation drainpipe

├── app.py                      # Main Flask app ✅32. PEX pipe and fittings

├── config.py                   # Configuration ✅33. Valves

├── init_db.py                  # Database init ✅34. Sanitary wares

├── requirements.txt            # Dependencies ✅35. Solar Water heater system

├── Procfile                    # Render config ✅

├── runtime.txt                 # Python version ✅## SYSTEM ARCHITECTURE

├── .env                        # Environment variables (not in Git)

├── .env.example                # Environment template ✅- **Primary**: Flask web dashboard for manual data entry and viewing

├── .gitignore                  # Git ignore rules ✅- **Secondary**: n8n workflows (runs intermittently on office PC) for AI automation

│- **Database**: Shared between Dashboard and n8n

├── models/                     # Database Models- **AI Models**: Claude API and OpenAI API for data extraction

│   ├── __init__.py

│   ├── material.py## KEY REQUIREMENTS

│   ├── purchase_order.py

│   ├── payment.py### 1. DUAL-MODE OPERATION

│   ├── delivery.py- **Manual Mode**: Always available - users can add/edit all data manually

│   ├── ai_suggestion.py- **AI Mode**: When n8n is running - AI suggests updates, human approves/rejects

│   └── file.py- AI only updates automatically if confidence > 90%, otherwise flags for review

│

├── routes/                     # API Routes### 2. DASHBOARD FEATURES

│   ├── __init__.py

│   ├── dashboard.py#### Material Tracking Fields

│   ├── materials.py- Approved

│   ├── purchase_orders.py- Approved as Noted

│   ├── payments.py- Pending

│   ├── deliveries.py- Under Review

│   ├── ai_suggestions.py- Revise & Resubmit

│   ├── chat.py

│   ├── uploads.py#### PO Tracking Fields

│   ├── auth.py                 # Authentication- Quote Ref

│   └── n8n_webhooks.py         # n8n integration- PO Ref

│- PO Date

├── services/                   # Business Logic- Supplier Name

│   ├── __init__.py- Total Amount

│   ├── ai_service.py- etc.

│   ├── chat_service.py

│   └── notification_service.py#### PO Status Options

│- Not Released

├── scripts/                    # Utility Scripts ✅- Released

│   ├── generate_api_key.py- Cancelled

│   └── quick_keygen.py

│#### Payment Tracking Fields

├── tests/                      # Test Suite ✅- Total Amount

│   ├── test_api_auth.py- Paid Amount

│   └── test_upload.py- Payment Percentage

│- Payment Date

├── templates/                  # HTML Templates

│   ├── base.html#### Payment Structure

│   ├── dashboard.html- Single Payment

│   ├── materials.html- Advance + Balance

│   ├── purchase_orders.html

│   ├── payments.html#### Currency

│   ├── deliveries.html- AED

│   ├── ai_suggestions.html

│   └── uploads.html#### Delivery Tracking Fields

│- Expected Delivery Date

├── static/                     # Static Files- Actual Delivery Date

│   ├── css/- Delivery Status

│   │   └── style.css

│   ├── js/#### Delivery Status Options

│   │   ├── main.js- Pending

│   │   └── chat.js- In Transit

│   └── uploads/               # User uploaded files- Partial Delivery

│       └── .gitkeep- Completed

│- Delayed

├── prompts/                    # AI Prompt Templates

│   ├── po_extraction.txt#### Additional Features

│   ├── invoice_extraction.txt- AI Suggestions review panel

│   ├── delivery_extraction.txt- Natural language chat interface for queries

│   └── chat_queries.txt- AI must ask if some data is missing with buttons and text fields as suitable (human can skip also)

│

├── instance/                   # SQLite Database### 3. N8N AUTOMATION WORKFLOWS

│   └── delivery_dashboard.db- Email monitoring (extract PO details from supplier emails)

│- PDF document processing (extract data from submittals, invoices)

└── Documentation (Root - MD files only) ✅- Delivery status updates (with confidence scoring)

    ├── README.md- Payment validation (cross-check invoices vs PO)

    ├── PROJECT_REQUIREMENTS.md (this file)- Delay predictions and alerts

    ├── COMPLETE_ROADMAP.md- Weekly/monthly report generation

    ├── CURRENT_STATUS.md- Notification system (email/WhatsApp/telegram when n8n is on)

    ├── API_SECURITY_GUIDE.md

    ├── RENDER_DEPLOY.md### 4. AI CONFIDENCE SYSTEM

    └── Other .md files- Extract data with confidence score (0-100%)

```- **If confidence >= 90%**: Auto-update with "AI Updated" flag

- **If confidence 60-89%**: Flag for human review with AI suggestion

**Rules:**- **If confidence < 60%**: Discard or flag as low confidence

- ✅ Only `.md`, `README`, `requirements.txt`, `Procfile`, `runtime.txt`, `app.py`, `config.py`, `init_db.py` allowed in root- Always show AI reasoning for transparency

- ✅ Python scripts → `scripts/` folder

- ✅ Tests → `tests/` folder### 5. NATURAL LANGUAGE INTERFACE

- ✅ Routes → `routes/` folder- Chat box on dashboard

- ✅ Models → `models/` folder- Example queries:

- ✅ Services → `services/` folder  - "Which materials are delayed?"

- ❌ NEVER put random `.py` files in root  - "When is DB arriving?"

  - "Show payment status"

---- AI queries database and responds in natural language

- Show data sources in response

### Rule #3: Never Create "Updated" or Versioned Documentation

**ONE authoritative version of each document:**### 6. DATABASE DESIGN



**❌ WRONG - Don't create:**#### Main Tables

- `UPDATED_ROADMAP_N8N.md`- Materials

- `COMPLETE_ROADMAP_V2.md`- PurchaseOrders

- `PHASE_2_1_COMPLETE.md`- Payments

- `PROJECT_REQUIREMENTS_NEW.md`- Deliveries



**✅ CORRECT - Update existing files:**#### AI Tracking

- Update `COMPLETE_ROADMAP.md` in-place- AI Suggestions table (stores pending/approved/rejected updates)

- Update `CURRENT_STATUS.md` with new progress

- Use Git for version history#### Audit Trail

- Track who updated (Human/AI) and when

**Documentation Structure:**- Confidence scores stored with AI updates

- `PROJECT_REQUIREMENTS.md` - This file (requirements + rules)

- `COMPLETE_ROADMAP.md` - Implementation phases### 7. API ENDPOINTS FOR N8N

- `CURRENT_STATUS.md` - Current progress- `POST /api/suggestion` - n8n submits AI-extracted data

- `API_SECURITY_GUIDE.md` - API reference- `GET /api/materials` - n8n fetches current data

- `RENDER_DEPLOY.md` - Deployment guide- `POST /api/notification` - n8n sends alerts

- `GET /api/pending-deliveries` - n8n gets upcoming deliveries for reminders

---

### 8. TECHNICAL SETUP

### Rule #4: Update Code In-Place, Don't Duplicate- Flask backend with RESTful API

**Modify existing functions, don't create alternatives:**- SQLite or PostgreSQL database

- JWT or API key authentication for n8n

**❌ WRONG:**- File upload/download for documents

```python- Responsive UI with Tailwind CSS

def process_file():- Chat interface using Claude/OpenAI API

    # old implementation

    pass## DELIVERABLES NEEDED



def process_file_v2():1. Complete project structure with all files

    # new implementation2. Database schema with all tables

    pass3. Flask app with routes and API endpoints

```4. Dashboard HTML templates

5. n8n workflow JSON files (examples)

**✅ CORRECT:**6. AI prompt templates for extraction tasks

```python7. Setup documentation

def process_file():8. Sample data for testing

    # updated implementation

    pass## IMPORTANT CONSTRAINTS

```

- n8n runs intermittently (not 24/7)

**Delete old code when updating:**- Manual entry must always work independently

- Remove unused functions- High confidence threshold before auto-updates

- Clean up commented code- All AI actions must be auditable

- Keep codebase maintainable- System should gracefully handle n8n being offline



---## PROJECT DEVELOPMENT RULES



### Rule #5: Check Progress Before Starting Work### Environment & Execution

**BEFORE starting ANY task:**1. **ALWAYS use WSL terminal** for all Python/Git commands

   - Use `wsl` command before running any Python scripts

1. ✅ Read `CURRENT_STATUS.md` - See what's complete   - Activate venv in WSL: `source venv/bin/activate`

2. ✅ Read `COMPLETE_ROADMAP.md` - Understand phases   - Run all Flask/Python commands in WSL environment

3. ✅ Ask user: "Where are we? What's next?"   - Execute Git commands through WSL (not PowerShell)

4. ✅ Confirm phase before coding

### File Management

---2. **NEVER create "updated", "renewed", or versioned documentation files**

   - Update existing files in-place (e.g., `COMPLETE_ROADMAP.md`)

## 🏗️ PROJECT ARCHITECTURE   - Do NOT create: `UPDATED_ROADMAP_N8N.md`, `COMPLETE_ROADMAP_V2.md`, etc.

   - Keep ONE authoritative version of each document

### System Overview   - Use Git for version history, not multiple files

- **Primary**: Flask web dashboard (manual data entry + viewing)

- **Secondary**: n8n workflows (intermittent AI automation)3. **Consolidate documentation**

- **Database**: SQLite (shared between Flask and n8n)   - One roadmap file: `COMPLETE_ROADMAP.md`

- **AI**: Claude API + OpenAI API for extraction   - One architecture file: `PROJECT_REQUIREMENTS.md` (this file)

   - Delete redundant or duplicate documentation

### Dual-Mode Operation   - Update sections within existing files rather than creating new ones

1. **Manual Mode**: Always available - users can add/edit data manually

2. **AI Mode**: When n8n runs - AI suggests updates, human approves/rejects### Code Changes

3. **Auto-Update**: Only if AI confidence ≥ 90%, otherwise flag for review4. **Update, don't duplicate**

   - Modify existing functions/classes in-place

---   - Don't create `function_v2()` or `new_function()` alongside old ones

   - Replace old code, don't append alternatives

## 📊 DATA MODELS   - Keep codebase clean and maintainable



### Material Types (35 items)### Communication

1. PVC Conduits & Accessories5. **Clear and concise**

2. Light Fittings (Internal & External)   - Provide direct answers without excessive explanations

3. Light Fittings (Decorative)   - Show actual code/terminal output when relevant

4. Cable Gland & Accessories   - Summarize changes made rather than showing full file contents

5. Earthing & LPS System   - Focus on what matters to the user

6. GI Conduit & Accessories

7. Cables & Wires---

8. Wiring Accessories

9. DB**Project Start Date**: October 3, 2025

10. GRMS
11. Fire Alarm system
12. Emergency Lighting system
13. Structured Cabling System & CCTV
14. Isolator
15. VRF System
16. ERV Unit
17. GI Duct
18. Duct Heater
19. Dampers
20. Air Outlets
21. Duct Insulation (Thermal)
22. Duct Insulation (Thermal)(Alternative)
23. Duct Insulation (Acoustic)
24. Sealants, Adhesives, Coating & Vapour Barrier
25. Flexible Duct
26. Aluminum Tape
27. Flexible Duct Connector
28. Fire Fighting system
29. Fire Extinguisher
30. PPR pipe and fittings
31. Condensation drainpipe
32. PEX pipe and fittings
33. Valves
34. Sanitary wares
35. Solar Water heater system

### Database Tables
- **Materials**: Track material submissions and approvals
- **PurchaseOrders**: PO tracking with supplier details
- **Payments**: Payment tracking (advance/balance)
- **Deliveries**: Delivery schedule and status
- **AISuggestions**: AI-extracted data pending review
- **Files**: Uploaded documents with metadata

### Field Details

**Material Status:**
- Approved
- Approved as Noted
- Pending
- Under Review
- Revise & Resubmit

**PO Status:**
- Not Released
- Released
- Cancelled

**Payment Structure:**
- Single Payment
- Advance + Balance

**Delivery Status:**
- Pending
- In Transit
- Partial Delivery
- Completed
- Delayed

**Currency:** AED

---

## 🤖 AI CONFIDENCE SYSTEM

**Thresholds:**
- **Confidence ≥ 90%**: Auto-update with "AI Updated" flag
- **Confidence 60-89%**: Flag for human review with AI suggestion
- **Confidence < 60%**: Discard or flag as low confidence

**Always show:**
- AI reasoning for transparency
- Confidence score
- Source (email, PDF, manual)
- Timestamp and reviewer

---

## 🔐 API SECURITY

**Authentication:**
- API key required for all n8n endpoints (except `/health`)
- Header: `X-API-Key: your-key-here`
- Generate keys: `python scripts/generate_api_key.py`

**Endpoints:**
- `GET /api/n8n/health` - Health check (no auth)
- `POST /api/n8n/ai-suggestion` - Submit AI-extracted data
- `POST /api/n8n/conversation` - Store chat messages
- `POST /api/n8n/clarification` - Handle follow-up questions
- `GET /api/n8n/pending-reviews` - Get items needing review
- `GET /api/n8n/stats` - Get statistics

---

## 📝 CODING STANDARDS

### Python Style
```python
"""
Module: routes/example.py
Purpose: Brief description
Phase: Phase X.X - Feature Name
"""

# Import order:
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from flask import Blueprint, request, jsonify

# 3. Local
from models import db
from models.material import Material
```

### Naming Conventions
- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **HTML templates**: `snake_case.html`
- **Documentation**: `SCREAMING_SNAKE.md`

---

## 🧪 TESTING

**Before committing:**
1. Test in WSL environment
2. Verify database operations
3. Check API endpoints work
4. Run test suite: `python tests/test_api_auth.py`

---

## 📦 DEPLOYMENT

**Platforms:**
- **Development**: WSL + Flask dev server
- **Production**: Render.com (free tier)

**Deployment files:**
- `Procfile`: `web: gunicorn "app:create_app()"`
- `runtime.txt`: `python-3.11.0`
- `requirements.txt`: All dependencies

---

## 🚫 CONSTRAINTS

1. n8n runs intermittently (not 24/7)
2. Manual entry must always work independently
3. High confidence threshold before auto-updates
4. All AI actions must be auditable
5. System must handle n8n being offline gracefully

---

## ✅ CURRENT PROGRESS

**Completed Phases:**
- ✅ Phase 1: Core Dashboard (100%)
- ✅ Phase 1.4: File Upload System (100%)
- ✅ Phase 2.1: API Security & n8n Webhooks (100%)

**Next Phases:**
- ⏳ Phase 2.2: n8n Email Monitor Workflow
- ⏳ Phase 2.3: AI Agent Service (document extraction)
- ⏳ Phase 2.4: Enhanced Chat Interface

**Overall Progress:** 50% Complete

---

## 📞 QUICK REFERENCE

**Start Flask:**
```bash
wsl bash -c "cd '/mnt/c/.../9. material delivery dashboard' && source venv/bin/activate && python app.py"
```

**Generate API Key:**
```bash
python scripts/generate_api_key.py
```

**Run Tests:**
```bash
python tests/test_api_auth.py
```

**Initialize Database:**
```bash
python init_db.py --with-samples -y
```

**Git Commands (always in WSL):**
```bash
git add .
git commit -m "message"
git push origin main
```

---

**For detailed phase-by-phase implementation, see `COMPLETE_ROADMAP.md`**  
**For current progress, see `CURRENT_STATUS.md`**
