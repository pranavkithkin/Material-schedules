# 📁 Complete File Structure

## Project Root
```
9. material delivery dashboard/
│
├── 📄 README.md                    # Project overview & quick start
├── 📄 QUICK_START.md               # 5-minute setup guide
├── 📄 STEP_BY_STEP_GUIDE.md        # Detailed implementation walkthrough
├── 📄 SETUP_GUIDE.md               # Complete reference guide
├── 📄 PROJECT_REQUIREMENTS.md      # Original requirements (saved)
├── 📄 PROJECT_SUMMARY.md           # What's been created & next steps
├── 📄 CHECKLIST.md                 # Completion checklist
│
├── 📄 app.py                       # ⭐ Main Flask application
├── 📄 config.py                    # ⭐ Configuration (35 material types)
├── 📄 init_db.py                   # ⭐ Database initialization
├── 📄 requirements.txt             # ⭐ Python dependencies
├── 📄 .env.example                 # ⭐ Environment variables template
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 models/                      # Database Models (SQLAlchemy)
│   ├── __init__.py
│   ├── material.py                 # Material tracking
│   ├── purchase_order.py           # PO management
│   ├── payment.py                  # Payment tracking
│   ├── delivery.py                 # Delivery tracking
│   └── ai_suggestion.py            # AI suggestions
│
├── 📁 routes/                      # API Routes (Flask Blueprints)
│   ├── __init__.py
│   ├── dashboard.py                # Dashboard & statistics
│   ├── materials.py                # Material CRUD
│   ├── purchase_orders.py          # PO CRUD
│   ├── payments.py                 # Payment CRUD
│   ├── deliveries.py               # Delivery CRUD
│   ├── ai_suggestions.py           # AI suggestion management
│   └── chat.py                     # Natural language chat
│
├── 📁 services/                    # Business Logic
│   ├── __init__.py
│   ├── ai_service.py               # AI extraction (Claude/OpenAI)
│   ├── chat_service.py             # Chat query processing
│   └── notification_service.py     # Email/WhatsApp/Telegram
│
├── 📁 templates/                   # HTML Templates (Jinja2)
│   ├── base.html                   # Base template with nav
│   ├── dashboard.html              # Main dashboard
│   ├── ai_suggestions.html         # AI review panel
│   ├── materials.html              # (Can be created)
│   ├── purchase_orders.html        # (Can be created)
│   ├── payments.html               # (Can be created)
│   └── deliveries.html             # (Can be created)
│
├── 📁 static/                      # Static Files
│   ├── 📁 css/
│   │   └── style.css               # Custom styling
│   ├── 📁 js/
│   │   ├── main.js                 # Core utilities
│   │   └── chat.js                 # Chat interface
│   └── 📁 uploads/
│       └── .gitkeep                # Uploads directory
│
├── 📁 prompts/                     # AI Prompt Templates
│   ├── po_extraction.txt           # PO extraction
│   ├── invoice_extraction.txt      # Invoice extraction
│   ├── delivery_extraction.txt     # Delivery extraction
│   └── chat_queries.txt            # Chat guidelines
│
└── 📁 n8n_workflows/               # (To be created)
    ├── email_monitor.json          # Email monitoring
    ├── pdf_processor.json          # PDF processing
    ├── delivery_tracker.json       # Delivery updates
    └── report_generator.json       # Report generation
```

---

## File Purposes

### 📚 Documentation (Read These!)

| File | Purpose | When to Read |
|------|---------|--------------|
| `QUICK_START.md` | Get running in 5 minutes | **START HERE** |
| `STEP_BY_STEP_GUIDE.md` | Complete setup walkthrough | After quick start |
| `SETUP_GUIDE.md` | Detailed reference | When you need details |
| `PROJECT_SUMMARY.md` | What's created & next steps | Overview |
| `CHECKLIST.md` | Completion status | Verify everything |
| `README.md` | Project overview | Quick reference |

---

### ⚙️ Core Application Files

| File | Purpose | Edit? |
|------|---------|-------|
| `app.py` | Main Flask app | Rarely |
| `config.py` | Configuration | Yes - for customization |
| `init_db.py` | Database setup | Run once |
| `requirements.txt` | Dependencies | No - auto-generated |
| `.env.example` | Config template | Copy to `.env` |

---

### 🗄️ Database Models (models/)

All models have:
- ✅ CRUD operations
- ✅ Relationships
- ✅ Validation
- ✅ to_dict() methods
- ✅ Audit trails

| Model | Tracks | Key Fields |
|-------|--------|------------|
| `material.py` | Material types & approval | approval_status, quantity |
| `purchase_order.py` | POs & suppliers | po_ref, total_amount |
| `payment.py` | Payments | payment_structure, paid_amount |
| `delivery.py` | Deliveries & delays | delivery_status, delay_days |
| `ai_suggestion.py` | AI suggestions | confidence_score, status |

---

### 🛣️ API Routes (routes/)

Each route provides RESTful API endpoints:

| Route | Endpoints | Purpose |
|-------|-----------|---------|
| `dashboard.py` | `/`, `/api/dashboard/stats` | Statistics |
| `materials.py` | `/api/materials/*` | Material CRUD |
| `purchase_orders.py` | `/api/purchase-orders/*` | PO CRUD |
| `payments.py` | `/api/payments/*` | Payment CRUD |
| `deliveries.py` | `/api/deliveries/*` | Delivery CRUD |
| `ai_suggestions.py` | `/api/ai-suggestions/*` | AI management |
| `chat.py` | `/api/chat` | Natural language |

---

### 🧠 Services (services/)

Business logic layer:

| Service | Purpose | Uses |
|---------|---------|------|
| `ai_service.py` | Extract data from documents | Claude/OpenAI APIs |
| `chat_service.py` | Process natural language | Database queries + AI |
| `notification_service.py` | Send alerts | SMTP/WhatsApp/Telegram |

---

### 🎨 Frontend (templates/ & static/)

**Templates:**
- `base.html` - Shared layout, navigation, chat button
- `dashboard.html` - Main statistics dashboard
- `ai_suggestions.html` - AI review panel

**Static Files:**
- `css/style.css` - Custom styles (beyond Tailwind)
- `js/main.js` - Utilities (loading, toasts, etc.)
- `js/chat.js` - Chat interface logic

---

### 🤖 AI Prompts (prompts/)

Templates for AI extraction:

| Prompt | Extracts | Confidence Factors |
|--------|----------|-------------------|
| `po_extraction.txt` | PO details from emails | PO ref, amount, supplier |
| `invoice_extraction.txt` | Payment info | Invoice ref, paid amount |
| `delivery_extraction.txt` | Delivery status | Tracking, dates, status |
| `chat_queries.txt` | Chat guidelines | Query patterns |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│                   USER INTERFACE                     │
│  (Browser: HTML/CSS/JavaScript + Tailwind)          │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│                  FLASK APPLICATION                   │
│  ┌──────────────────────────────────────────────┐  │
│  │  Routes (API Endpoints)                       │  │
│  │  - dashboard.py                               │  │
│  │  - materials.py                               │  │
│  │  - purchase_orders.py                         │  │
│  │  - payments.py                                │  │
│  │  - deliveries.py                              │  │
│  │  - ai_suggestions.py                          │  │
│  │  - chat.py                                    │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │  Services (Business Logic)                    │  │
│  │  - ai_service.py                              │  │
│  │  - chat_service.py                            │  │
│  │  - notification_service.py                    │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │  Models (Database Layer)                      │  │
│  │  - Material                                   │  │
│  │  - PurchaseOrder                              │  │
│  │  - Payment                                    │  │
│  │  - Delivery                                   │  │
│  │  - AISuggestion                               │  │
│  └──────────────────┬───────────────────────────┘  │
└───────────────────┬─┴────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  SQLite Database      │
        │  delivery_dashboard.db│
        └───────────────────────┘
```

---

## External Integrations

```
┌──────────────────────────────────────────────┐
│                   n8n                         │
│  (Runs intermittently on office PC)          │
│                                               │
│  Workflows:                                   │
│  - Email Monitor    ──────┐                  │
│  - PDF Processor    ──────┤                  │
│  - Delivery Tracker ──────┤                  │
│  - Report Generator ──────┤                  │
└──────────────────────┬────┴──────────────────┘
                       │
                       │ HTTP POST
                       ▼
        ┌─────────────────────────────┐
        │  Flask API Endpoints         │
        │  /api/ai-suggestions         │
        │  /api/notifications          │
        │  /api/materials              │
        │  /api/pending-deliveries     │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  AI Service                  │
        │  - Extract data              │
        │  - Calculate confidence      │
        │  - Create suggestions        │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  Claude API / OpenAI API     │
        │  - PO extraction             │
        │  - Invoice extraction        │
        │  - Delivery extraction       │
        │  - Chat responses            │
        └──────────────────────────────┘
```

---

## Confidence Flow

```
n8n extracts data from email/PDF
           │
           ▼
    Calculate confidence score
           │
           ├── ≥90%? ──Yes─► Auto-apply + flag "AI Updated"
           │     │
           │     No
           │     │
           ├── ≥60%? ──Yes─► Create pending suggestion
           │     │
           │     No
           │     │
           └─────────────►  Discard or log low confidence
```

---

## File Size Reference

| Category | Files | Approx Size |
|----------|-------|-------------|
| Documentation | 7 files | ~50 KB |
| Python Code | 20+ files | ~100 KB |
| Templates | 3+ files | ~30 KB |
| Static Files | 3+ files | ~10 KB |
| Prompts | 4 files | ~5 KB |
| Config | 4 files | ~5 KB |
| **Total** | **40+ files** | **~200 KB** |

---

## What Gets Created When You Run

When you run `python init_db.py --with-samples`:

```
delivery_dashboard.db (SQLite database)
├── materials (5 sample records)
├── purchase_orders (2 sample records)
├── payments (2 sample records)
├── deliveries (2 sample records)
└── ai_suggestions (1 sample record)
```

When you run `python app.py`:
- Flask server starts on port 5000
- All API endpoints become available
- Web interface accessible at http://localhost:5000

When users upload files:
```
static/uploads/
├── pos/
├── invoices/
├── deliveries/
└── submittals/
```

---

## Database Tables Overview

```
┌─────────────────┐
│   materials     │
│─────────────────│
│ id              │──┐
│ material_type   │  │
│ approval_status │  │
│ quantity        │  │
│ created_by      │  │
│ updated_by      │  │
└─────────────────┘  │
                     │
                     │ One to Many
                     │
┌─────────────────┐  │
│ purchase_orders │◄─┘
│─────────────────│
│ id              │──┐
│ material_id     │  │
│ po_ref          │  │
│ supplier_name   │  │
│ total_amount    │  │
│ po_status       │  │
│ created_by      │  │
│ updated_by      │  │
└─────────────────┘  │
          │          │
          ├──────────┤ One to Many
          │          │
          ▼          ▼
┌─────────────────┐  ┌─────────────────┐
│    payments     │  │   deliveries    │
│─────────────────│  │─────────────────│
│ id              │  │ id              │
│ po_id           │  │ po_id           │
│ total_amount    │  │ delivery_status │
│ paid_amount     │  │ is_delayed      │
│ payment_status  │  │ delay_days      │
│ created_by      │  │ tracking_number │
│ updated_by      │  │ created_by      │
└─────────────────┘  │ updated_by      │
                     └─────────────────┘

┌───────────────────┐
│  ai_suggestions   │
│───────────────────│
│ id                │
│ target_table      │
│ target_id         │
│ confidence_score  │
│ suggested_data    │
│ status            │
│ ai_reasoning      │
│ reviewed_by       │
└───────────────────┘
```

---

## Key Relationships

1. **Material → Purchase Orders** (One to Many)
   - One material can have multiple POs

2. **Purchase Order → Payments** (One to Many)
   - One PO can have multiple payments (advance, balance)

3. **Purchase Order → Deliveries** (One to Many)
   - One PO can have multiple deliveries (partial deliveries)

4. **AI Suggestions → Any Table** (Reference)
   - Suggestions can target any table via target_table + target_id

---

## Command Quick Reference

```powershell
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Database
python init_db.py                    # Empty database
python init_db.py --with-samples     # With sample data

# Run
python app.py                        # Start application

# n8n (separate terminal)
n8n start                            # Start n8n
```

---

## URL Reference

| URL | Purpose |
|-----|---------|
| http://localhost:5000 | Main dashboard |
| http://localhost:5000/materials | Materials page |
| http://localhost:5000/purchase-orders | POs page |
| http://localhost:5000/payments | Payments page |
| http://localhost:5000/deliveries | Deliveries page |
| http://localhost:5000/ai-suggestions | AI review panel |
| http://localhost:5678 | n8n interface |

---

**This structure gives you:**
- ✅ Complete separation of concerns
- ✅ Easy maintenance
- ✅ Scalable architecture
- ✅ Clear data flow
- ✅ Modular design
- ✅ RESTful API
- ✅ Comprehensive documentation

---

Last Updated: October 3, 2025
Status: Complete & Ready ✅
