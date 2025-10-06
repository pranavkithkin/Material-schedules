# 🚀 COMPLETE IMPLEMENTATION ROADMAP
## Material Delivery Dashboard - 5 Week Plan

---

## 🚀 IMPLEMENTATION PHASES

### PHASE 1: Core Dashboard (Week 1)
**Goal:** Working manual dashboard without AI

#### Step 1.1: Environment Setup
**What to ask Claude:**
```
"Set up a Flask project with this structure:
- Virtual environment
- Required packages: Flask, SQLAlchemy, Flask-CORS, python-dotenv
- Project folder organization
- Database initialization
I'm using [Windows/Mac/Linux], Python 3.x"
```

#### Step 1.2: Database Design
**What to ask Claude:**
```
"Create SQLAlchemy models for these tables:

MATERIALS: [paste your exact fields]
PURCHASE_ORDERS: [paste your exact fields]
PAYMENTS: [paste your exact fields]
DELIVERIES: [paste your exact fields]
AI_SUGGESTIONS: id, material_id, source, suggestion_type, extracted_data (JSON), 
                confidence_score, status, ai_reasoning, created_date, reviewed_by, reviewed_date

Include relationships and a 'created_by' field (Human/AI) for audit trail."
```

#### Step 1.3: Basic Dashboard UI
**What to ask Claude:**
```
"Create Flask routes and HTML templates for:
1. Dashboard home - overview with statistics
2. Materials list - table view with all materials
3. Add material form - all fields: [list your fields]
4. Edit material page
5. Material detail view - showing all related PO, payment, delivery info
6. Delete confirmation

Use Tailwind CSS for styling. Include:
- Responsive design
- Status badges with colors
- Search and filter functionality"
```

#### Step 1.4: File Upload System
**What to ask Claude:**
```
"Implement file upload/download for documents:
- Allowed formats: PDF, Word, Excel, Images
- Max size: [specify, e.g., 20MB]
- Store in /uploads folder with organized structure
- Display uploaded files with download links
- Multiple files per material if needed"
```

**✅ Deliverable:** Working dashboard where you can manually enter and view all data

---

### PHASE 1B: Advanced AI Agent System (Week 1.5-2) ⭐ NEW
**Goal:** Intelligent document processing with conversational AI that asks clarifying questions

> **Note:** See detailed implementation plan in `AI_AGENT_IMPLEMENTATION_PLAN.md`

#### Step 1B.1: Enhanced AI Service with Conversation
**What to ask Claude:**
```
"Create an advanced AI agent service that:
1. Extracts structured data from documents (PO, invoices, delivery notes)
2. Tracks conversation context across multiple messages
3. Detects missing fields and generates clarifying questions
4. Supports multi-turn conversations for data entry
5. Maintains confidence scoring per field
6. Can process: email text, PDF attachments, images (with OCR)

Files to create:
- services/ai_agent.py (conversational AI with memory)
- models/conversation.py (chat history tracking)
- routes/ai_agent.py (API endpoints for document processing)

Use cases:
- Email with PO attachment → Extract → Ask for missing info → Create PO
- Natural language: 'Add cement PO for 50k' → AI asks questions → Complete record
- Document upload → Show extracted fields → User approves/edits"
```

#### Step 1B.2: Document Upload Interface
**What to ask Claude:**
```
"Create a document upload page (templates/document_upload.html):
- Drag-and-drop zone for PDF/images
- Real-time AI extraction preview
- Show confidence score per field (color-coded)
- Editable form with AI suggestions
- 'Ask AI for help' button for unclear fields
- Side-by-side: Original document vs Extracted data
- Approve/Edit/Discard actions

Include:
- OCR support for scanned documents (using pytesseract)
- PDF text extraction (using PyPDF2)
- Image upload (PNG, JPG)
- Progress indicators during extraction"
```

#### Step 1B.3: Conversational Data Entry
**What to ask Claude:**
```
"Enhance the chat interface for natural language data entry:

User: 'Add a PO for steel from XYZ, 50 tons, 80k AED'
AI: 'Got it! I'll create a PO. What's the PO number?'
User: 'PO-5678'
AI: 'When do you expect delivery?'
User: 'Next Monday'
AI: '✅ Created PO-5678 for Steel:
     - Supplier: XYZ
     - Quantity: 50 tons
     - Amount: AED 80,000
     - Expected: 2025-10-07
     
     Missing: Supplier email. Add it or skip?'

Features needed:
- Multi-turn conversation tracking
- Entity extraction (numbers, dates, material types)
- Smart defaults (today's date, currency: AED)
- Confirmation before creating records
- Show summary with 'Confirm' button"
```

#### Step 1B.4: Email Monitoring with n8n
**What to ask Claude:**
```
"Create n8n workflow for automatic email processing:

Workflow:
1. Email Trigger (IMAP) - Monitor inbox every 5 minutes
2. Filter: Subject contains 'PO', 'Purchase Order', 'Invoice', 'Delivery'
3. Extract attachments (PDF/images)
4. HTTP Request POST /api/ai-agent/process-document
   Body: {
     file: base64_encoded_attachment,
     source: 'email',
     metadata: {sender, subject, date}
   }
5. AI processes document → Returns extracted data + confidence
6. Decision Node:
   - If confidence ≥90%: Auto-create PO + Send success notification
   - If 60-89%: Send 'Review Needed' email/WhatsApp
   - If <60%: Send clarification request to sender

Include:
- Error handling for unreadable files
- Notification templates
- Webhook for real-time processing
- Complete workflow JSON export"
```

#### Step 1B.5: API Endpoints for AI Agent
**What to ask Claude:**
```
"Create these new API endpoints in routes/ai_agent.py:

POST /api/ai-agent/process-document
- Input: file (PDF/image), source (email/upload/whatsapp), metadata
- Output: extracted_data, confidence, missing_fields, clarification_questions
- Process: OCR/extract text → AI analysis → Return structured data

POST /api/ai-agent/chat
- Input: message, conversation_id (for context)
- Output: response, action (if any), extracted_data
- Process: Understand intent → Query DB if needed → Conversational response

POST /api/ai-agent/clarify
- Input: suggestion_id, clarifications {field: value}
- Output: updated_data, ready_to_create (boolean)
- Process: Merge clarifications → Validate → Return complete data

GET /api/ai-agent/conversations
- Output: List of active conversations with context
- Process: Fetch from conversation history

Include comprehensive error handling and validation."
```

**✅ Deliverable:** Intelligent AI agent that extracts data, asks questions, and auto-fills forms

---

### PHASE 2: API Security & AI Agent (Week 2-3)
**Goal:** Smart document processing and conversational data entry

> **📋 DETAILED AI AGENT SYSTEM:** See [AI Agents Roadmap](AI_AGENTS_ROADMAP.md) for complete agent specifications, priorities, and implementation plan

#### Step 2.1: API Authentication ✅ COMPLETE
- API key authentication system (routes/auth.py)
- 7 n8n webhook endpoints created
- Test suite implemented
- Documentation complete

#### Step 2.2: AI Document Extraction Service (NEXT)
**📋 See:** [AI Agents Roadmap](AI_AGENTS_ROADMAP.md#sprint-2-week-2-document-processing) - Sprint 2
**What to ask Claude:**
```
"Create AI agent service (services/ai_agent.py) that:
1. Accepts uploaded PDF files
2. Extracts text from PDF (PyPDF2)
3. Uses Claude API to analyze and extract:
   - Purchase Order details (PO number, supplier, amount, date)
   - Invoice details (invoice number, amount, payment terms)
   - Delivery notes (delivery date, items, status)
4. Returns structured JSON with confidence scores per field
5. Identifies missing/unclear fields
6. Generates clarifying questions for user

Features:
- Handle scanned PDFs (OCR with pytesseract - optional)
- Multiple document types (PO, Invoice, Delivery Note)
- Field-level confidence scoring
- AI reasoning for transparency
- Error handling for corrupted/unreadable files

Integration:
- Add 'Process with AI' button on uploads page
- Show extracted fields with confidence indicators
- Allow user to edit before approving
- Save to AISuggestions table for review"
```

#### Step 2.3: Enhanced Chat Interface
**📋 See:** [AI Agents Roadmap](AI_AGENTS_ROADMAP.md#sprint-3-week-3-conversational-ai) - Sprint 3

**What to ask Claude:**
```
"Enhance chat service (services/chat_service.py) for natural language data entry:

1. Multi-turn Conversation Tracking:
   - Create models/conversation.py to store chat history
   - Track conversation context across multiple messages
   - Remember user preferences and partial data

2. Natural Language Data Entry:
   User: 'Add a PO for steel from ABC, 50 tons, 80k'
   AI: 'Got it! What's the PO number?'
   User: 'PO-5678'
   AI: 'When do you expect delivery?'
   User: 'Next Monday'
   AI: '✅ Created PO-5678 for Steel. Missing supplier email - add it or skip?'

3. Smart Features:
   - Entity extraction (dates, amounts, material names)
   - Smart defaults (today's date, AED currency)
   - Confirmation before creating records
   - Show summary with edit option
   - Handle corrections: 'Actually, make it 60 tons'

4. Query Capabilities:
   - 'When is cement delivery?'
   - 'Show pending POs'
   - 'What's the total payment for supplier ABC?'
   - 'List delayed deliveries'

Include conversation persistence, context awareness, and error handling."
```

**✅ Deliverable:** Smart AI agent that processes documents and enables conversational data entry

---

### PHASE 3: n8n Automation Workflows (Week 3-4)
**Goal:** Automated workflows for reminders and notifications

> **📋 DETAILED AUTOMATION AGENTS:** See [AI Agents Roadmap](AI_AGENTS_ROADMAP.md#sprint-5-week-5-automation--reminders) - Sprint 5

#### Step 3.1: Delivery Reminder Workflow
**What to ask Claude:**
```
"Create scheduled n8n workflow:
1. Schedule Trigger - Run daily at 8 AM
2. HTTP Request GET /api/pending-deliveries?days=7
3. For each pending delivery:
   - Check if delivery date is within [X] days
   - Generate reminder message
4. Send notifications via:
   - Email (SMTP)
   - WhatsApp (optional, using Twilio)
   - Telegram (optional)
5. Log notifications sent to dashboard API

Provide workflow JSON and notification templates."
```

#### Step 3.4: Weekly Report Generation
**What to ask Claude:**
```
"Create scheduled n8n workflow:
1. Schedule Trigger - Run weekly (e.g., Friday 5 PM)
2. HTTP Request GET /api/materials (fetch all data)
3. Process data:
   - Count materials by status
   - Calculate payment completion %
   - Identify delayed deliveries
   - List pending POs
4. HTTP Request to Claude API:
   Prompt: 'Generate a professional weekly summary report from this data: [JSON]'
5. Send report via email
6. Optionally save as PDF

Provide workflow JSON and report template."
```

**✅ Deliverable:** Automated delivery reminders and weekly reports

---

### PHASE 4: Advanced Features (Week 4-5)
**Goal:** Analytics, predictions, and advanced automation

#### Step 4.3: Enhanced Query Handling
**What to ask Claude:**
```
"Improve chat to handle:
- Multi-material queries: 'Status of DB and Fire Alarm'
- Date-based queries: 'Deliveries this week'
- Comparative queries: 'Which is more delayed, X or Y?'
- Aggregations: 'Total pending payments'
- Trend questions: 'Are deliveries improving?'

Use SQLAlchemy queries to fetch accurate data before sending to AI."
```

**✅ Deliverable:** Working chat interface for querying data

---

### PHASE 5: Advanced Features (Week 5)

#### Step 5.1: Confidence Tuning
**What to ask Claude:**
```
"Create admin settings page:
- Adjust confidence thresholds (auto-update, review-needed, discard)
- View AI accuracy over time (approved vs rejected suggestions)
- Retrain prompts based on feedback
- Test AI extraction with sample documents"
```

#### Step 5.2: Predictive Alerts
**What to ask Claude:**
```
"Create n8n workflow for delay prediction:
1. Schedule: Run daily
2. Fetch materials with upcoming deliveries
3. Analyze patterns:
   - Supplier's past delays
   - Material type typical lead time
   - Current status (PO released? Payment done?)
4. Claude API: 'Based on this data, predict likelihood of delay'
5. If high risk: Create alert in dashboard
6. Send proactive notification

Provide workflow JSON and prediction prompt."
```

#### Step 5.3: Invoice Reconciliation
**What to ask Claude:**
```
"Create workflow for payment validation:
1. Trigger: New invoice PDF uploaded
2. Extract: Invoice amount, PO number, date
3. Query dashboard API for matching PO
4. Compare amounts:
   - If match: Suggest payment update
   - If mismatch: Flag discrepancy with details
5. POST suggestion with explanation

Provide workflow and validation logic."
```

**✅ Deliverable:** Complete system with predictive features

---

## 🔐 Security & Configuration

### Environment Variables (.env)
```bash
# Dashboard
FLASK_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/delivery_db
API_KEY=your-n8n-api-key

# AI APIs
CLAUDE_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/
N8N_API_KEY=your-n8n-key

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password

# Confidence Thresholds
AUTO_UPDATE_THRESHOLD=90
REVIEW_THRESHOLD=60
```

---

## 🎨 AI Prompt Templates

### Email Extraction Prompt
```
You are a data extraction assistant. Extract the following information from this supplier email:

Email Content:
{email_body}

Extract these fields:
- PO Number (format: PO-YYYY-NNNN)
- Material Name
- Supplier Name
- Delivery Date (ISO format: YYYY-MM-DD)
- Amount (number only, no currency symbols)
- Status Update (any status mentioned)

Return JSON:
{
  "po_number": "...",
  "material_name": "...",
  "supplier_name": "...",
  "delivery_date": "...",
  "amount": ...,
  "status": "...",
  "confidence_score": 0-100,
  "reasoning": "Explain why you're confident or uncertain"
}

If any field cannot be found, set it to null. Be conservative with confidence scores.
```

### PDF Invoice Extraction Prompt
```
You are processing an invoice document. Extract:

Document Text:
{pdf_text}

Fields to extract:
- Invoice Number
- PO Number (if referenced)
- Invoice Date
- Total Amount
- Payment Terms
- Due Date

Return JSON with confidence scoring for each field individually:
{
  "invoice_number": {"value": "...", "confidence": 0-100},
  "po_number": {"value": "...", "confidence": 0-100},
  ...
  "overall_confidence": 0-100,
  "reasoning": "..."
}
```

### Chat Query Prompt
```
You are a helpful assistant for a construction delivery tracking system.

User Question: {user_query}

Available Data:
{database_results}

Instructions:
1. Answer the user's question based ONLY on the data provided
2. Be concise and direct
3. Use bullet points for multiple items
4. Mention specific material names, dates, and amounts
5. If the data shows delays or issues, highlight them
6. If data is missing, say so clearly

Response:
```

---

## 📊 Sample Workflows

### High-Confidence Auto-Update Flow
```
Email Received → AI Extraction (confidence: 95%) → Auto-Update Database
                                                   ↓
                                        Log in AI_Suggestions (approved)
                                                   ↓
                                        Dashboard shows "Last updated by AI"
```

### Medium-Confidence Review Flow
```
PDF Uploaded → AI Extraction (confidence: 75%) → Create Suggestion (Pending)
                                                  ↓
                                        Dashboard shows in Review Panel
                                                  ↓
                                        Human reviews → Approves/Rejects
                                                  ↓
                                        Update Database or Discard
```

### Low-Confidence Discard Flow
```
Portal Data → AI Extraction (confidence: 45%) → Log as Low Confidence
                                                 ↓
                                        Optional: Notify for manual check
                                        Do NOT create suggestion
```

---

## 🧪 Testing Plan

### Phase 1 Testing: Manual Dashboard
- [ ] Add material manually
- [ ] Edit all fields
- [ ] Upload document
- [ ] Download document
- [ ] Delete material
- [ ] View material details
- [ ] Filter and search

### Phase 2 Testing: API
- [ ] Call API with valid key
- [ ] Call API with invalid key
- [ ] Submit high-confidence suggestion (should auto-approve)
- [ ] Submit low-confidence suggestion (should flag for review)
- [ ] Approve suggestion from UI
- [ ] Reject suggestion from UI

### Phase 3 Testing: n8n Workflows
- [ ] Send test email → Check if extracted correctly
- [ ] Upload test PDF → Check if data appears in review panel
- [ ] Wait for scheduled reminder → Check if notification received
- [ ] Wait for weekly report → Check if report generated

### Phase 4 Testing: Chat Interface
- [ ] Ask: "Which materials are delayed?"
- [ ] Ask: "When is [material name] arriving?"
- [ ] Ask: "Show payment status"
- [ ] Ask: "Summary of this week"
- [ ] Ask unclear question → Check if AI asks for clarification

---

---

### PHASE 5: Email Monitor Workflow (OPTIONAL - Final Phase)
**Goal:** Automated email parsing for unstructured supplier communications

> **📋 DETAILED EMAIL AGENT:** See [AI Agents Roadmap](AI_AGENTS_ROADMAP.md#sprint-7-optional---week-7-email-integration) - Sprint 7 (Optional)

**Note:** This is moved to the end because emails are often unstructured and parsing them requires significant effort for limited value. Prioritize manual upload + AI extraction first.

#### Step 5.1: Email Monitoring Setup
**What to ask Claude:**
```
"Create n8n workflow for email monitoring:
1. IMAP Email Trigger - Monitor inbox every 30 minutes
2. Filter emails - Keywords: PO, Purchase Order, Delivery, Invoice
3. Extract email body + attachments (PDF)
4. HTTP Request to Claude API:
   Prompt: 'Extract from this email: PO number, material name, delivery date, 
            supplier name, amount. Return JSON with confidence score.
            If unclear, set low confidence.'
5. Parse Claude response
6. POST to /api/n8n/ai-suggestion
7. Notification based on confidence:
   - High (≥90%): Success notification
   - Medium (60-89%): Review needed
   - Low (<60%): Ignore or flag

Include:
- Error handling for email parsing failures
- Attachment handling (PDF/images only)
- Spam/irrelevant email filtering
- Rate limiting for API calls
- Complete workflow JSON export"
```

**Why This is Last:**
- Emails are often unstructured (casual language, incomplete info)
- Low accuracy compared to manual PDF upload
- Requires extensive prompt engineering
- Better to focus on structured data entry first
- Can always add later if email quality improves

**✅ Deliverable:** Email monitoring (only if needed after core features work well)

---

## 📅 Timeline Summary (Updated)

| Week | Phase | Focus | Deliverable |
|------|-------|-------|-------------|
| 1 | Phase 1 | Core Dashboard | ✅ Manual data entry system |
| 2 | **Phase 2.1** | **API Security** | **✅ n8n authentication + webhooks** |
| 2-3 | **Phase 2.2** | **AI Document Extraction** | **⏳ Smart PDF processing** ← **NEXT**
| 3 | **Phase 2.3** | **Enhanced Chat** | **⏳ Conversational data entry** |
| 3-4 | Phase 3 | n8n Workflows | ✅ Delivery reminders + reports |
| 4-5 | Phase 4 | Advanced Features | ⏳ Analytics + predictions |
| 5+ | Phase 5 | Email Monitor | ⏳ Optional email parsing (if needed) |

**Updated Focus:**
- Week 1: ✅ Core dashboard complete with PKP branding
- Week 1.5-2: 🔄 **AI Agent with conversational abilities** ← **Current**
- Week 2-3: n8n automation workflows
- Week 4-5: Advanced AI features and analytics

---

## ✅ Current Status (October 6, 2025)

### COMPLETED:
- ✅ Phase 1.1: Environment Setup
- ✅ Phase 1.2: Database Design (5 models)
- ✅ Phase 1.3: Basic Dashboard UI (6 pages)
- ✅ Phase 1.4: File Upload System (100%)
- ✅ All templates working with PKP branding
- ✅ All API endpoints created (30+)
- ✅ Database initialized with sample data
- ✅ **Phase 2.1: API Security (100%)** - API key authentication + 7 n8n webhook endpoints
- ✅ **Phase 2.2: Document Intelligence (95%)** - AI extraction working
  - AI Smart Upload interface with real-time progress tracking
  - Intelligent material type detection from item descriptions
  - Auto-linking for Delivery Notes/Invoices to existing POs
  - Purchase Order extraction working (85-95% accuracy)
  - Enhanced AI prompt with comprehensive material detection
  - End-to-end workflow tested successfully
  - Cloudflare tunnel setup for n8n connectivity
- ✅ **Phase 3: Automation Workflows (100%)** ← **JUST COMPLETED!**
  - 3 new API endpoints created (pending-deliveries, weekly-report-data, log-notification)
  - 2 n8n workflow JSON files created (daily reminder, weekly report)
  - Workflows work without email (console logging for now)
  - Ready to import and test in n8n

### TESTING PHASE:
- 🧪 **Phase 2.2: Final Polish (5% remaining)**
  - Test Invoice extraction
  - Test Delivery Note extraction
  - Update n8n workflow with improved AI prompt
  - Add document type badges to uploads page

- 🧪 **Phase 3: n8n Workflow Testing**
  - Import workflows to n8n
  - Configure API key credential
  - Test manual execution
  - Activate scheduled runs
  - Monitor console logs

### PENDING:
- ⏳ **Phase 4: Enhanced Chat Interface (Week 4)** ← **NEXT PRIORITY**
  - Conversational data entry (multi-turn conversations)
  - Natural language queries
  - Context-aware responses
  - Entity extraction (dates, amounts, material names)
  
- ⏳ Phase 5: Advanced Features (Week 5)
  - Analytics dashboards
  - Delay prediction based on supplier history
  - Confidence tuning interface
  - Predictive alerts

**🎯 Overall Progress:** 75% Complete! (was 65%)

**📊 Sprint Status:**
- ✅ Sprint 1: Core Dashboard - COMPLETE (100%)
- ✅ Sprint 2: Document Intelligence - COMPLETE (95% - testing remaining)
- ✅ Sprint 3: Automation Workflows - COMPLETE (100% - testing required)
- ⏳ Sprint 4: Enhanced Chat - STARTING NEXT
- ⏳ Sprint 5: Advanced Features - PENDING

---

## 🎯 Next Immediate Steps (Updated October 6, 2025)

### **Option 1: Phase 4 - Enhanced Chat Interface** ⭐ **RECOMMENDED NEXT**

**Goal:** Conversational AI that helps with data entry and queries

**What to build:**
1. **Multi-turn Conversation System**
   - Create `models/conversation.py` to track chat history
   - Store conversation context across messages
   - Remember user preferences and partial data entries

2. **Natural Language Data Entry**
   ```
   User: "Add a PO for steel from ABC, 50 tons, 80k"
   AI: "Got it! What's the PO number?"
   User: "PO-5678"
   AI: "When do you expect delivery?"
   User: "Next Monday"
   AI: "✅ Created PO-5678 for Steel:
        - Supplier: ABC
        - Quantity: 50 tons
        - Amount: AED 80,000
        - Expected: 2025-10-13
        
        Missing: Supplier email. Add it or skip?"
   ```

3. **Smart Query Handling**
   - "Which materials are delayed?"
   - "When is cement delivery?"
   - "Show payment status for supplier ABC"
   - "Total pending payments this month"

4. **Entity Extraction**
   - Dates: "next Monday", "in 3 days", "October 15"
   - Amounts: "50k", "AED 80,000", "fifty thousand"
   - Material types: "DB", "VRF", "Fire Fighting"
   - Smart defaults: AED currency, today's date

**Files to create/enhance:**
- `models/conversation.py` - Conversation tracking model
- Enhance `services/chat_service.py` - Add conversation context
- Enhance `routes/chat.py` - Add conversation endpoints
- Update `templates/chat.html` - Better chat UI

**Estimated time:** 1-2 days
**Value:** High - Makes data entry much faster and more intuitive

---

### **Option 2: Polish & Testing** 🧪

**Complete remaining 5% of Document Intelligence:**
1. Test Invoice extraction (upload sample invoice PDF)
2. Test Delivery Note extraction
3. Update n8n workflow with improved prompt
4. Add document type badges to uploads page

**Test Phase 3 Automation:**
1. Import n8n workflows
2. Configure credentials
3. Test manual execution
4. Verify console logging works
5. Activate scheduled runs

**Estimated time:** 1 day
**Value:** Medium - Ensures everything works properly

---

### **Option 3: Phase 5 - Advanced Features** 🚀

**Analytics & Predictions:**
1. **Delay Prediction Workflow**
   - Analyze supplier history
   - Predict delivery delays
   - Send proactive alerts

2. **Payment Reconciliation**
   - Auto-match invoices to POs
   - Flag amount discrepancies
   - Suggest payment updates

3. **Analytics Dashboard**
   - Supplier performance metrics
   - Delivery timeline charts
   - Payment completion trends
   - Material status overview

**Estimated time:** 2-3 days
**Value:** High - Business intelligence and proactive management

---
