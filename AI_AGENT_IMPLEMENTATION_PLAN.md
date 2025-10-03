# AI Agent Implementation Plan
## Material Delivery Dashboard - AI-Powered Data Entry System

---

## 🎯 OVERVIEW

Transform the Material Delivery Dashboard into an AI-driven system where:
- **AI Agent extracts data** from documents (PO, invoices, delivery notes)
- **Email monitoring** automatically processes attachments
- **Natural language commands** allow conversational data entry
- **Interactive clarification** asks for missing information
- **Human oversight** maintains data accuracy

---

## 🏗️ ARCHITECTURE

### **Component Structure:**

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT SOURCES                        │
├─────────────────────────────────────────────────────────┤
│  1. Email (n8n monitors)                                │
│  2. File Upload (Manual)                                │
│  3. Chat Interface (Natural Language)                   │
│  4. API Webhook (External systems)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   AI PROCESSING LAYER                   │
├─────────────────────────────────────────────────────────┤
│  • Document Text Extraction (OCR if needed)             │
│  • Claude/GPT-4 Analysis                                │
│  • Structured Data Extraction                           │
│  • Confidence Scoring                                   │
│  • Missing Field Detection                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              VALIDATION & CLARIFICATION                 │
├─────────────────────────────────────────────────────────┤
│  • Check completeness                                   │
│  • Validate field formats                               │
│  • Cross-reference existing data                        │
│  • Generate clarification questions                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 ACTION & APPROVAL                       │
├─────────────────────────────────────────────────────────┤
│  High Confidence (≥90%) → Auto-create with notification │
│  Medium (60-89%)        → Show preview for approval     │
│  Low (<60%)             → Request human input           │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 USE CASES

### **Use Case 1: Email PO Processing**
**Scenario:** Supplier sends PO via email

**Workflow:**
1. n8n monitors email inbox (Gmail/Outlook)
2. Detects email with subject containing "PO" or "Purchase Order"
3. Extracts PDF/image attachment
4. Sends to AI agent via webhook
5. AI extracts: PO number, supplier, amount, date, items
6. If complete → Creates PO record + notifies you
7. If incomplete → Sends clarification email/WhatsApp

**Example Email:**
```
From: supplier@abc.com
Subject: PO Release - Project XYZ
Attachment: PO-12345.pdf

AI Extracts:
- PO Number: 12345
- Supplier: ABC Trading LLC
- Amount: AED 125,000
- Date: 2025-10-03
- Material: Cement (500 bags)
- Delivery Date: 2025-10-15

Status: ✅ Complete → Auto-created
```

### **Use Case 2: Natural Language Command**
**Scenario:** You tell AI what to add via chat

**Example Commands:**
```
You: "Add a PO for 50 tons of steel from XYZ Steel, 
      PO number PO-5678, amount 80,000 AED, 
      delivery by next Monday"

AI: "✅ I've created Purchase Order PO-5678:
     - Supplier: XYZ Steel
     - Material: Steel
     - Quantity: 50 tons
     - Amount: AED 80,000
     - Expected Delivery: 2025-10-07
     
     Missing: Supplier contact email. 
     Would you like to add it?"

You: "supplier@xyzsteel.ae"

AI: "✅ Updated! PO is now complete."
```

### **Use Case 3: Document Upload with AI Extraction**
**Scenario:** You upload a scanned PO image

**Workflow:**
1. Click "Upload Document" button
2. Select PDF/JPG/PNG
3. AI extracts text using OCR
4. Shows extracted fields in a form
5. You review and approve/edit
6. Submit to database

**AI Prompts:**
```
AI: "I extracted these details from your PO:
     
     PO Number: PO-9876
     Supplier: ABC Construction Materials
     Amount: AED 45,500
     
     ⚠️ Missing information:
     - Expected delivery date
     - Material type
     - Supplier contact
     
     Can you provide these?"
```

### **Use Case 4: Payment Release Notification**
**Scenario:** Finance sends payment confirmation email

**Email Example:**
```
From: finance@pkp.ae
Subject: Payment Released - PO-12345
Body: We have released advance payment of AED 50,000 
      (40% of total) for PO-12345 to ABC Trading.
      Ref: BANK-REF-7890

AI Actions:
1. ✅ Finds PO-12345 in database
2. ✅ Creates payment record:
   - Type: Advance Payment
   - Amount: AED 50,000
   - Percentage: 40%
   - Reference: BANK-REF-7890
   - Date: Today
3. ✅ Sends WhatsApp: "Payment recorded for PO-12345"
```

### **Use Case 5: Delivery Status Update**
**Scenario:** Driver sends delivery photo via WhatsApp

**WhatsApp Message:**
```
Driver: [Photo of delivery note]
        "Delivered 30 bags cement to Site A"

AI Processing:
1. OCR on delivery note image
2. Extracts: Material, Quantity, Site
3. Matches to pending deliveries
4. Updates delivery status
5. Asks: "Delivery note number?"

You: "DN-4567"

AI: "✅ Delivery DN-4567 marked complete for PO-12345"
```

---

## 🛠️ IMPLEMENTATION PHASES

### **Phase 1: Enhanced AI Service (Week 1)**
**Goal:** Improve current AI extraction with conversational abilities

**Tasks:**
1. ✅ Enhance `ai_service.py` with conversation memory
2. ✅ Add missing field detection
3. ✅ Create clarification question generator
4. ✅ Add confidence scoring improvements
5. ✅ Support multi-turn conversations

**Files to Create/Modify:**
- `services/ai_agent.py` (NEW) - Conversational AI agent
- `services/ai_service.py` (ENHANCE) - Better extraction
- `models/conversation.py` (NEW) - Chat history tracking

### **Phase 2: n8n Email Automation (Week 1-2)**
**Goal:** Monitor emails and auto-process attachments

**n8n Workflow Components:**

```
┌──────────────────┐
│  Email Trigger   │ → Gmail/Outlook IMAP
│  (Every 5 min)   │    Subject: "PO" OR "Purchase Order"
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Extract Attach.  │ → Get PDF/Image files
└────────┬─────────┘
         ↓
┌──────────────────┐
│  OCR if needed   │ → Convert image to text
└────────┬─────────┘
         ↓
┌──────────────────┐
│ HTTP POST to     │ → POST /api/ai-process
│ Flask API        │    Body: {file, email_meta}
└────────┬─────────┘
         ↓
┌──────────────────┐
│ AI Processing    │ → Extract structured data
└────────┬─────────┘
         ↓
         ├─ High Confidence → Auto-create + Notify
         ├─ Medium Conf.   → Send approval email
         └─ Low Conf.      → Request clarification
```

**API Endpoints to Create:**
```python
POST /api/ai-process
POST /api/ai-chat
POST /api/ai-clarify
GET  /api/conversations
```

### **Phase 3: File Upload Interface (Week 2)**
**Goal:** Manual document upload with AI extraction

**UI Components:**
1. Drag-and-drop upload zone
2. Real-time extraction preview
3. Editable form with AI suggestions
4. Confidence indicators per field
5. "Ask AI" button for help

**New Page:** `templates/document_upload.html`

### **Phase 4: Conversational Chat Integration (Week 2-3)**
**Goal:** Natural language data entry

**Features:**
- Multi-turn conversations
- Context awareness (remembers previous messages)
- Entity extraction ("50 tons" → quantity: 50, unit: tons)
- Smart defaults (today's date, currency: AED)
- Confirmation before creating records

**Enhanced Chat Panel:**
```javascript
// Example conversation flow
User: "Add cement PO"
AI:   "Sure! I'll help you create a cement PO. 
       What's the PO number?"

User: "PO-1234"
AI:   "Got it! Who's the supplier?"

User: "ABC Trading"
AI:   "Great! What's the amount?"

User: "50000 AED"
AI:   "Perfect! Expected delivery date?"

User: "Next Friday"
AI:   "✅ Created PO-1234:
       - Supplier: ABC Trading
       - Material: Cement
       - Amount: AED 50,000
       - Delivery: 2025-10-11
       
       Missing: Quantity and supplier contact.
       Should I save it or add more details?"
```

### **Phase 5: WhatsApp Integration (Week 3)**
**Goal:** Receive updates via WhatsApp

**Integration Options:**
1. **Twilio WhatsApp API** (Easiest, $$ paid)
2. **WhatsApp Business API** (Official, requires approval)
3. **n8n WhatsApp Node** (Free, unofficial)

**Use Cases:**
- Send PO updates via WhatsApp
- Receive delivery confirmations
- Quick status queries: "Status of PO-1234?"

---

## 💡 AI AGENT PROMPT DESIGN

### **System Prompt for Data Extraction:**

```python
SYSTEM_PROMPT = """
You are an AI assistant for PKP Engineering Consultants' 
Material Delivery Dashboard. Your role is to extract 
structured data from construction documents and help users 
manage materials, purchase orders, payments, and deliveries.

When extracting data:
1. Look for: PO numbers, supplier names, amounts, dates, 
   material types, quantities
2. Assign confidence scores (0-100%) per field
3. If a field is missing or unclear, mark it for clarification
4. Use UAE conventions (AED currency, DD/MM/YYYY dates)
5. Material types should match our 35 predefined categories

When conversing:
1. Be concise and professional
2. Confirm actions before executing
3. Ask clarifying questions for missing data
4. Provide summaries after creating records
5. Remember context from previous messages

Available Actions:
- create_purchase_order(data)
- create_payment(data)
- create_delivery(data)
- update_record(id, data)
- query_database(filters)
"""
```

### **Example AI Responses:**

**High Confidence:**
```json
{
  "confidence": 95,
  "action": "create_purchase_order",
  "data": {
    "po_number": "PO-12345",
    "supplier_name": "ABC Trading LLC",
    "total_amount": 125000,
    "currency": "AED",
    "po_date": "2025-10-03",
    "material_type": "Cement",
    "quantity": 500,
    "unit": "bags"
  },
  "missing_fields": [],
  "message": "✅ PO extracted successfully. All fields complete. 
              Ready to create?"
}
```

**Medium Confidence - Missing Data:**
```json
{
  "confidence": 75,
  "action": "request_clarification",
  "data": {
    "po_number": "PO-12345",
    "supplier_name": "ABC Trading",
    "total_amount": 125000
  },
  "missing_fields": [
    "material_type",
    "delivery_date",
    "supplier_contact"
  ],
  "clarification_questions": [
    "What material is this PO for? (Cement, Steel, etc.)",
    "When is the expected delivery date?",
    "What's the supplier's email or phone?"
  ]
}
```

---

## 📊 CONFIDENCE SCORING LOGIC

```python
def calculate_confidence(extracted_data, required_fields):
    """
    Confidence Score Calculation:
    - Required field present + validated = 20 points each
    - Optional field present = 10 points each
    - Field format correct (email, phone, date) = +5 bonus
    - Cross-reference match (existing supplier) = +10 bonus
    """
    
    confidence = 0
    total_possible = 100
    
    # Required fields (5 @ 20 points each)
    required = ['po_number', 'supplier_name', 'total_amount', 
                'material_type', 'po_date']
    
    for field in required:
        if field in extracted_data and extracted_data[field]:
            confidence += 20
            if validate_field_format(field, extracted_data[field]):
                confidence += 5  # Bonus for correct format
    
    # Bonus for existing supplier match
    if supplier_exists_in_db(extracted_data.get('supplier_name')):
        confidence += 10
    
    return min(confidence, 100)
```

---

## 🔧 TECHNICAL IMPLEMENTATION

### **New API Endpoints:**

```python
# routes/ai_agent.py

@ai_agent_bp.route('/process-document', methods=['POST'])
def process_document():
    """
    Process uploaded document or email attachment
    
    Input:
        - file: PDF/Image
        - source: 'email', 'upload', 'whatsapp'
        - metadata: {sender, subject, etc}
    
    Output:
        - extracted_data: Structured fields
        - confidence: 0-100
        - missing_fields: List of fields needing clarification
        - suggested_action: 'auto_create', 'review', 'clarify'
    """
    pass

@ai_agent_bp.route('/chat', methods=['POST'])
def ai_chat():
    """
    Natural language conversation
    
    Input:
        - message: User's text
        - conversation_id: Track context
    
    Output:
        - response: AI's reply
        - action: Action to take (if any)
        - data: Extracted structured data
    """
    pass

@ai_agent_bp.route('/clarify', methods=['POST'])
def clarify():
    """
    User provides missing information
    
    Input:
        - suggestion_id: ID of pending suggestion
        - clarifications: {field: value}
    
    Output:
        - updated_data: Complete data
        - ready_to_create: boolean
    """
    pass
```

### **n8n Workflow JSON (Email Monitor):**

```json
{
  "name": "PO Email Monitor",
  "nodes": [
    {
      "name": "Email Trigger",
      "type": "n8n-nodes-base.emailReadImap",
      "parameters": {
        "mailbox": "INBOX",
        "options": {
          "filter": {
            "subject": ["PO", "Purchase Order"]
          }
        }
      }
    },
    {
      "name": "Extract Attachments",
      "type": "n8n-nodes-base.extractFromFile"
    },
    {
      "name": "Send to AI API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5000/api/ai-agent/process-document",
        "authentication": "none",
        "sendHeaders": true
      }
    },
    {
      "name": "Check Confidence",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json.confidence}}",
              "operation": "largerEqual",
              "value2": 90
            }
          ]
        }
      }
    },
    {
      "name": "Auto Create PO",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5000/api/purchase_orders"
      }
    },
    {
      "name": "Send Notification",
      "type": "n8n-nodes-base.telegram"
    }
  ]
}
```

---

## 📱 WHATSAPP INTEGRATION

### **Option 1: Twilio WhatsApp API**

```python
# services/whatsapp_service.py

from twilio.rest import Client

def send_whatsapp_message(to, message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio sandbox
        to=f'whatsapp:{to}',
        body=message
    )
    return message.sid

def receive_whatsapp_webhook():
    """
    Webhook endpoint for incoming WhatsApp messages
    
    Example: User sends "Status of PO-1234"
    AI: "PO-1234 Status: Released
         Amount: AED 125,000
         Delivery: Expected 15/10/2025"
    """
    pass
```

### **Option 2: n8n WhatsApp Node**

```
WhatsApp Trigger → Extract Message → 
AI Processing → Database Query → 
Send WhatsApp Reply
```

---

## 🎨 UI ENHANCEMENTS

### **1. Document Upload Page**

```html
<!-- New page: templates/document_upload.html -->

<div class="upload-zone">
    <div class="dropzone">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag & drop PO, Invoice, or Delivery Note</p>
        <p>or click to browse</p>
    </div>
    
    <!-- After upload -->
    <div class="extraction-preview">
        <h3>AI Extracted Data</h3>
        
        <div class="field-row">
            <label>PO Number</label>
            <input value="PO-12345" />
            <span class="confidence">95%</span>
        </div>
        
        <div class="field-row missing">
            <label>Delivery Date</label>
            <input placeholder="AI couldn't find this" />
            <button onclick="askAI()">🤖 Ask AI</button>
        </div>
        
        <button class="btn-approve">✅ Approve & Create</button>
        <button class="btn-edit">✏️ Edit First</button>
    </div>
</div>
```

### **2. Enhanced Chat Interface**

```javascript
// Conversation context tracking
class AIConversation {
    constructor() {
        this.history = [];
        this.context = {
            current_action: null,
            partial_data: {}
        };
    }
    
    async sendMessage(message) {
        this.history.push({role: 'user', content: message});
        
        const response = await fetch('/api/ai-agent/chat', {
            method: 'POST',
            body: JSON.stringify({
                message: message,
                history: this.history,
                context: this.context
            })
        });
        
        const data = await response.json();
        this.history.push({role: 'assistant', content: data.response});
        
        if (data.action) {
            this.handleAction(data.action, data.data);
        }
        
        return data;
    }
}
```

---

## 🚀 QUICK START IMPLEMENTATION

### **Step 1: Install Required Packages**

```bash
pip install anthropic openai pytesseract pillow PyPDF2 twilio
```

### **Step 2: Create AI Agent Service**

I'll create the files for you in the next step!

### **Step 3: Set up n8n**

```bash
npm install -g n8n
n8n start

# Open http://localhost:5678
# Import workflow from n8n_workflows/ folder
```

### **Step 4: Configure API Keys**

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
TWILIO_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
```

---

## 📈 EXPECTED BENEFITS

### **Time Savings:**
- ⏱️ **Manual data entry**: 5-10 minutes per PO
- ⏱️ **AI-assisted**: 30 seconds (review + approve)
- 💰 **Savings**: ~90% reduction in data entry time

### **Accuracy Improvements:**
- ✅ OCR + AI validation reduces human errors
- ✅ Cross-reference checks prevent duplicates
- ✅ Format validation ensures data consistency

### **Workflow Efficiency:**
- 📧 Email → Database (fully automated)
- 💬 WhatsApp updates (instant notifications)
- 🤖 Natural language commands (no forms needed)

---

## 🎯 NEXT STEPS

Would you like me to:

1. ✅ **Create the AI Agent service** (`services/ai_agent.py`)
2. ✅ **Create new API endpoints** for document processing
3. ✅ **Design n8n workflow templates** (email monitoring)
4. ✅ **Build document upload page** with AI extraction
5. ✅ **Enhance chat interface** for conversational data entry

Let me know which component you'd like to implement first! 🚀
