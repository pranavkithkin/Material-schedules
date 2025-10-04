# 🔄 HYBRID ARCHITECTURE - IMPLEMENTATION GUIDE
## Python (Flask) + n8n Integration

**Last Updated:** October 4, 2025  
**Status:** Sprint 1 in Progress  

---

## 📋 QUICK REFERENCE

### **What Goes Where?**

| Component | Location | Why |
|-----------|----------|-----|
| **Data validation** | 🐍 Python | Instant response, direct DB |
| **Duplicate detection** | 🐍 Python | Direct DB queries needed |
| **AI document extraction** | 🔀 n8n | Async (10-30s), Claude API |
| **Chat UI** | 🐍 Python | Fast rendering, session mgmt |
| **Chat AI logic** | 🔀 n8n | GPT-4 API, easier to modify |
| **Scheduled reminders** | 🔀 n8n | Cron triggers, notifications |
| **Email monitoring** | 🔀 n8n | IMAP trigger built-in |
| **Analytics/Reports** | 🐍 Python | Pandas, complex calculations |

---

## 🏗️ ARCHITECTURE DIAGRAM

```
USER INTERACTION
      │
      ├─── Form Submit ────────────┐
      │                            │
      ├─── File Upload ────────────┼─────────┐
      │                            │         │
      ├─── Chat Message ───────────┼─────────┼───────┐
      │                            │         │       │
      └─── View Dashboard ─────────┼─────────┼───────┼──────┐
                                   │         │       │      │
                                   ▼         ▼       ▼      ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FLASK DASHBOARD (Python/WSL)                    │
│                                                                   │
│  ✅ Agent 1: Data Processing                                     │
│     └─ Validation, Duplicates, Matching (INSTANT)                │
│                                                                   │
│  ✅ Agent 6: Analytics                                            │
│     └─ Pandas calculations, Reports (FAST)                       │
│                                                                   │
│  📊 Database (SQLite - Direct Access)                            │
│  🌐 API Endpoints (for n8n)                                      │
│     ├─ POST /api/n8n/document-processed                          │
│     ├─ POST /api/n8n/chat-response                               │
│     └─ GET  /api/n8n/pending-reminders                           │
│                                                                   │
│  🚀 Webhook Triggers (to n8n)                                    │
│     ├─ File uploaded → trigger document processing               │
│     ├─ Chat sent → trigger AI response                           │
│     └─ Manual reminder → trigger notification                    │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        │ HTTP Webhooks
                        │ http://office-pc:5678/webhook/...
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│              n8n (Self-hosted on Office PC)                       │
│              http://localhost:5678                                │
│                                                                   │
│  🔀 Agent 2: Document Intelligence Workflow                       │
│     1. Webhook trigger (file uploaded)                           │
│     2. Extract text from PDF/image                               │
│     3. Claude API → structured extraction                        │
│     4. POST back to Flask → /api/n8n/document-processed          │
│                                                                   │
│  🔀 Agent 3: Conversational AI Workflow                           │
│     1. Webhook trigger (chat message)                            │
│     2. GPT-4 API → intent parsing & entity extraction            │
│     3. POST back to Flask → /api/n8n/chat-response               │
│                                                                   │
│  🔀 Agent 4: Automation Workflows (4 workflows)                   │
│     A. Delivery Reminder (cron: daily 8 AM)                      │
│        1. GET /api/n8n/pending-deliveries                        │
│        2. Generate reminders                                     │
│        3. Send WhatsApp/Email                                    │
│                                                                   │
│     B. Payment Reminder (cron: daily 8 AM)                       │
│     C. Submittal Follow-up (cron: weekly Monday 9 AM)            │
│     D. Upload Reminder (cron: daily 9 AM)                        │
│                                                                   │
│  🔀 Agent 5: Email Processing Workflow                            │
│     1. IMAP trigger (every 30 min)                               │
│     2. Classify email                                            │
│     3. Extract attachments → trigger doc processing              │
│                                                                   │
│  🔌 External APIs                                                 │
│     ├─ Anthropic Claude (document extraction)                    │
│     ├─ OpenAI GPT-4 (conversational AI)                          │
│     ├─ Twilio (WhatsApp)                                         │
│     └─ SMTP (Email)                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🐍 PYTHON IMPLEMENTATION (Sprint 1-2)

### **Sprint 1: Data Processing Agent** (Week 1)

**Status:** ✅ 50% Complete

**Files to create:**
```
services/
├── data_processing_agent.py        ✅ Created (validation + duplicates + matching)
└── __init__.py

routes/
├── agents.py                        ⏳ TODO (API endpoints for agents)
└── __init__.py

tests/
└── test_data_processing_agent.py   ⏳ TODO (unit tests)
```

**API Endpoints to add:**
```python
# routes/agents.py

@app.route('/api/agents/validate-and-check', methods=['POST'])
@require_api_key  # Secure with API key
def validate_and_check():
    """
    Validate data + check duplicates + match invoice to LPO
    Called by: Forms (before save), n8n workflows (after AI extraction)
    
    Request:
    {
        "record_type": "lpo_release",
        "data": {...},
        "check_duplicates": true,
        "match_invoice_to_lpo": false
    }
    
    Response:
    {
        "is_valid": true,
        "errors": [],
        "warnings": ["⚠️ Amount higher than typical"],
        "duplicates": [],
        "matched_lpo_id": null,
        "ready_to_save": true
    }
    """
    pass
```

**Next Steps:**
1. ⏳ Create `routes/agents.py` with validation endpoint
2. ⏳ Update existing forms to call validation before save
3. ⏳ Write unit tests
4. ⏳ Document API endpoint

---

### **Sprint 5: Analytics Agent** (Week 5)

**Files to create:**
```
services/
├── analytics_agent.py              ⏳ TODO (pattern recognition, insights)
└── __init__.py

routes/
└── analytics.py                    ⏳ TODO (analytics endpoints)

templates/
└── analytics.html                  ⏳ TODO (analytics dashboard page)
```

**Features:**
- Historical data analysis (Pandas)
- Supplier performance metrics
- Smart suggestions during data entry
- Report generation (PDF/CSV)
- Trend visualization

---

## 🔀 n8n IMPLEMENTATION (Sprint 2-4, 6)

### **Sprint 2: Document Intelligence Workflow** (Week 2)

**Workflow:** `Document Intelligence - AI Extraction`

**Trigger:** Webhook  
**URL:** `http://localhost:5678/webhook/document-process`

**Workflow Steps:**
1. **Webhook Trigger**
   - Receives: `{ file_path, record_type, source }`
   
2. **Read File Node**
   - Binary data from file path
   
3. **PDF Text Extraction**
   - Node: `PDF Parse` or custom function
   - Extract all text from PDF
   
4. **Claude API Call**
   - Node: `HTTP Request` to Anthropic API
   - Prompt: "Extract structured data from this document..."
   - Response: JSON with fields + confidence scores
   
5. **Validate Data**
   - Node: `HTTP Request` to Flask
   - POST `/api/agents/validate-and-check`
   
6. **Return to Flask**
   - Node: `HTTP Request`
   - POST `/api/n8n/document-processed`
   - Body: Extracted + validated data

**Python API Endpoint Needed:**
```python
# routes/n8n_webhooks.py (already exists!)

@app.route('/api/n8n/document-processed', methods=['POST'])
@require_api_key
def document_processed():
    """
    Receives AI-extracted document data from n8n
    Saves to database or prompts user for review
    """
    data = request.json
    # data = {
    #     "document_id": "doc-123",
    #     "classification": {"type": "invoice", "confidence": 0.95},
    #     "extracted_fields": {...},
    #     "validation_result": {...}
    # }
    
    # Save to database or create AI suggestion for review
    pass
```

**To trigger from Flask:**
```python
# When user uploads file
import requests

def trigger_document_processing(file_path, record_type):
    """Trigger n8n document processing workflow"""
    response = requests.post(
        'http://localhost:5678/webhook/document-process',
        json={
            'file_path': file_path,
            'record_type': record_type,
            'source': 'upload'
        },
        timeout=60  # Document processing can take 30+ seconds
    )
    return response.json()
```

---

### **Sprint 3: Conversational AI Workflow** (Week 3)

**Workflow:** `Conversational AI - Intent Parser`

**Trigger:** Webhook  
**URL:** `http://localhost:5678/webhook/chat`

**Workflow Steps:**
1. **Webhook Trigger**
   - Receives: `{ message, conversation_id, user_id }`
   
2. **Load Conversation History**
   - Node: `HTTP Request` to Flask
   - GET `/api/conversations/{conversation_id}`
   
3. **GPT-4 API Call**
   - Node: `HTTP Request` to OpenAI API
   - Prompt: Conversation history + new message
   - Extract: intent, entities, response
   
4. **Return to Flask**
   - Node: `HTTP Request`
   - POST `/api/n8n/chat-response`
   - Body: Intent, entities, response text

**Python API Endpoints Needed:**
```python
# routes/chat.py

@app.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """
    User sends chat message
    Triggers n8n workflow for AI processing
    """
    message = request.json['message']
    conversation_id = request.json.get('conversation_id')
    
    # Save message to database
    # Trigger n8n workflow
    response = requests.post(
        'http://localhost:5678/webhook/chat',
        json={
            'message': message,
            'conversation_id': conversation_id,
            'user_id': session.get('user_id')
        }
    )
    
    return jsonify(response.json())

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
@require_api_key
def get_conversation_history(conversation_id):
    """
    n8n calls this to get conversation context
    Returns last 10 messages
    """
    # Query database
    messages = Conversation.query.filter_by(
        conversation_id=conversation_id
    ).order_by(Conversation.timestamp.desc()).limit(10).all()
    
    return jsonify([
        {'role': msg.role, 'content': msg.content}
        for msg in messages
    ])

@app.route('/api/n8n/chat-response', methods=['POST'])
@require_api_key
def chat_response():
    """
    n8n sends AI response back
    Save to database and return to user
    """
    data = request.json
    # Save AI response
    # Return to chat UI via WebSocket or polling
    pass
```

---

### **Sprint 4: Automation Workflows** (Week 4)

**4 Separate Workflows:**

#### **A. Delivery Reminder Workflow**

**Trigger:** Cron - Daily at 8:00 AM  
**Workflow Steps:**
1. **Schedule Trigger** (cron: `0 8 * * *`)
2. **Get Pending Deliveries**
   - HTTP Request to Flask
   - GET `/api/n8n/pending-deliveries?days=7`
3. **Loop Through Each**
   - For each pending delivery...
4. **Generate Reminder Message**
   - Function node: Create message text
5. **Send WhatsApp** (optional)
   - Twilio node
6. **Send Email**
   - SMTP node
7. **Log Notification**
   - HTTP Request to Flask
   - POST `/api/n8n/notification-sent`

**Python API Endpoint:**
```python
@app.route('/api/n8n/pending-deliveries', methods=['GET'])
@require_api_key
def get_pending_deliveries():
    """
    Returns LPOs with upcoming delivery dates
    """
    days = request.args.get('days', 7, type=int)
    today = datetime.now()
    future_date = today + timedelta(days=days)
    
    pending = LPORelease.query.filter(
        LPORelease.expected_delivery_date.between(today, future_date),
        LPORelease.actual_delivery_date.is_(None)
    ).all()
    
    return jsonify([
        {
            'id': lpo.id,
            'lpo_number': lpo.lpo_number,
            'material': lpo.material.name,
            'supplier': lpo.supplier_name,
            'expected_delivery_date': lpo.expected_delivery_date.isoformat(),
            'days_until_delivery': (lpo.expected_delivery_date - today).days
        }
        for lpo in pending
    ])
```

#### **B. Payment Reminder Workflow**
- Similar structure to delivery reminder
- Check invoices with upcoming due dates

#### **C. Submittal Follow-up Workflow**
- Weekly cron (Monday 9 AM)
- Check submittals pending > 7 days

#### **D. Upload Reminder Workflow**
- Daily cron (9 AM)
- Check records without documents

---

### **Sprint 6: Email Processing Workflow** (Week 6-7, Optional)

**Workflow:** `Email Processing - Monitor & Route`

**Trigger:** IMAP Email Trigger  
**Poll:** Every 30 minutes

**Workflow Steps:**
1. **IMAP Trigger**
   - Connect to email inbox
   - Filter: Subject contains "PO", "Invoice", "Delivery"
   
2. **Extract Attachments**
   - Get PDF/image attachments
   
3. **Classify Email**
   - GPT-4 API: Determine email type
   
4. **Route Based on Type**
   - If has attachment → Trigger document processing
   - If order confirmation → Create LPO
   - If inquiry → Log for review
   
5. **Log Email Processing**
   - POST to Flask `/api/n8n/email-processed`

---

## 🔐 SECURITY & CONFIGURATION

### **Environment Variables**

**Flask (.env):**
```env
# n8n Integration
N8N_WEBHOOK_BASE_URL=http://localhost:5678/webhook
N8N_API_KEY=<your-n8n-api-key>

# API Keys for n8n to call Flask
N8N_TO_FLASK_API_KEY=<generate-with-scripts/generate_api_key.py>
```

**n8n (Environment Variables):**
```env
# Claude API
ANTHROPIC_API_KEY=<your-claude-api-key>

# OpenAI API
OPENAI_API_KEY=<your-openai-api-key>

# Flask Dashboard
FLASK_API_URL=http://localhost:5000
FLASK_API_KEY=<same-as-N8N_TO_FLASK_API_KEY>

# Twilio (optional)
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your-email>
SMTP_PASS=<your-app-password>
```

---

## 📝 IMPLEMENTATION CHECKLIST

### **Sprint 1: Data Processing Agent (Week 1)** ⏳ IN PROGRESS

**Python Side:**
- [x] Create `services/data_processing_agent.py`
- [ ] Create `routes/agents.py` with validation endpoint
- [ ] Update forms to call validation before save
- [ ] Write unit tests
- [ ] Document API endpoint

**Deliverable:** Forms validate data instantly before save

---

### **Sprint 2: Document Intelligence (Week 2)** ⏳ TODO

**Python Side:**
- [ ] Add `/api/n8n/document-processed` endpoint
- [ ] Add file upload trigger to call n8n webhook
- [ ] Create AI suggestions review page

**n8n Side:**
- [ ] Build "Document Intelligence" workflow
- [ ] Configure Claude API credentials
- [ ] Test PDF extraction
- [ ] Test end-to-end: Upload → Extract → Save

**Deliverable:** Upload PDF → AI extracts data → User reviews → Save

---

### **Sprint 3: Conversational AI (Week 3)** ⏳ TODO

**Python Side:**
- [ ] Create `models/conversation.py`
- [ ] Create `routes/chat.py`
- [ ] Add `/api/conversations/<id>` endpoint
- [ ] Add `/api/n8n/chat-response` endpoint
- [ ] Update chat UI

**n8n Side:**
- [ ] Build "Conversational AI" workflow
- [ ] Configure OpenAI API credentials
- [ ] Test intent parsing
- [ ] Test end-to-end conversation

**Deliverable:** Chat with AI to create/query records

---

### **Sprint 4: Automation (Week 4)** ⏳ TODO

**Python Side:**
- [ ] Add `/api/n8n/pending-deliveries` endpoint
- [ ] Add `/api/n8n/pending-payments` endpoint
- [ ] Add `/api/n8n/pending-submittals` endpoint
- [ ] Add `/api/n8n/pending-uploads` endpoint
- [ ] Add `/api/n8n/notification-sent` endpoint

**n8n Side:**
- [ ] Build "Delivery Reminder" workflow (cron)
- [ ] Build "Payment Reminder" workflow (cron)
- [ ] Build "Submittal Follow-up" workflow (cron)
- [ ] Build "Upload Reminder" workflow (cron)
- [ ] Configure WhatsApp/Email

**Deliverable:** Automated daily/weekly reminders

---

### **Sprint 5: Analytics (Week 5)** ⏳ TODO

**Python Side:**
- [ ] Create `services/analytics_agent.py`
- [ ] Create `routes/analytics.py`
- [ ] Create analytics dashboard page
- [ ] Add pattern recognition logic
- [ ] Add report generation

**Deliverable:** Analytics dashboard with insights

---

### **Sprint 6: Email Processing (Week 6-7, Optional)** ⏳ TODO

**n8n Side:**
- [ ] Build "Email Processing" workflow (IMAP trigger)
- [ ] Configure email account
- [ ] Test email classification
- [ ] Test attachment extraction

**Deliverable:** Emails auto-processed into system

---

## 🚀 GETTING STARTED

### **Step 1: Continue Python Development**
```bash
cd "c:\Users\PKP\Documents\PRANAV\Projects\With a clear picture\9. material delivery dashboard"

# Activate WSL and run Flask
wsl
source venv/bin/activate
python app.py
```

### **Step 2: Set Up n8n (when ready for Sprint 2)**
```bash
# Your self-hosted n8n should already be running
# Access at: http://localhost:5678

# Add credentials:
# - Anthropic (Claude API key)
# - OpenAI (GPT-4 API key)
# - HTTP Auth (Flask API key)
# - Twilio (optional)
# - SMTP (optional)
```

### **Step 3: Test Integration**
1. Flask running on `http://localhost:5000`
2. n8n running on `http://localhost:5678`
3. Test webhook: Flask → n8n → Flask roundtrip

---

## 📞 SUPPORT & QUESTIONS

**Questions?**
- Architecture decisions: Review this guide
- API endpoint specs: See roadmap
- Token optimization: Check cost analysis in roadmap

**Ready to implement Sprint 1?** Let's finish the Data Processing Agent! 🚀
