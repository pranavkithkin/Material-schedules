# Sprint 2: Document Intelligence Integration
**Start Date:** October 4, 2025  
**Duration:** 2-3 weeks  
**Goal:** Auto-extract data from delivery orders and enable chatbot queries

---

## 🎯 Sprint 2 Objectives

### Primary Goals
1. **Document Upload & Storage** - Upload delivery order PDFs to system
2. **n8n Workflow Integration** - Connect to n8n for document processing
3. **Claude API Integration** - Extract items & quantities from documents
4. **Chatbot Enhancement** - Answer "Has X been delivered?" queries
5. **Auto-Calculate Delivery %** - Update percentage based on extracted data

### Success Metrics
- ✅ Upload delivery order PDF successfully
- ✅ Extract 90%+ accuracy on item names
- ✅ Extract 85%+ accuracy on quantities
- ✅ Chatbot responds to delivery queries
- ✅ Auto-update delivery percentage
- ✅ Processing time < 30 seconds per document

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
│  ┌────────────────┐         ┌──────────────────┐           │
│  │  Upload Form   │────────▶│ Store PDF File   │           │
│  │  (Delivery)    │         │ /uploads/docs/   │           │
│  └────────────────┘         └──────────┬───────┘           │
│                                        │                     │
│                                        ▼                     │
│                            ┌─────────────────────┐          │
│                            │  Trigger n8n        │          │
│                            │  Webhook            │          │
│                            └──────────┬──────────┘          │
└────────────────────────────────────────┼───────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      n8n Workflow                            │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │  Receive     │─────▶│  Download    │────▶│  Extract   │ │
│  │  Webhook     │      │  PDF File    │     │  Text/OCR  │ │
│  └──────────────┘      └──────────────┘     └─────┬──────┘ │
│                                                     │        │
│                                                     ▼        │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │  Send Result │◀─────│  Parse JSON  │◀────│  Claude    │ │
│  │  to Flask    │      │  Response    │     │  API Call  │ │
│  └──────────────┘      └──────────────┘     └────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application                          │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │  Receive     │─────▶│  Parse Items │────▶│  Update    │ │
│  │  Extracted   │      │  & Quantities│     │  Database  │ │
│  │  Data        │      └──────────────┘     └────────────┘ │
│  └──────────────┘                                   │       │
│                                                      ▼       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Chatbot: Query extracted data to answer questions   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Sprint 2 Tasks Breakdown

### Phase 1: Document Upload (Week 1, Days 1-2)
**Goal:** Enable PDF upload in delivery form

**Tasks:**
- [ ] Add file upload field to delivery form UI
- [ ] Create uploads directory structure
- [ ] Update Delivery model with document metadata
- [ ] Create file upload API endpoint
- [ ] Validate file types (PDF only)
- [ ] Store files with unique names
- [ ] Update database with file path

**Files to Modify:**
- `templates/deliveries.html` - Add file upload field
- `routes/deliveries.py` - Add upload handling
- `models/delivery.py` - Add extracted_data field
- Create `routes/uploads.py` (if not exists)

**Deliverable:** Users can upload delivery order PDFs

---

### Phase 2: n8n Workflow Setup (Week 1, Days 3-4)
**Goal:** Create n8n workflow for document processing

**n8n Workflow Steps:**
1. **Webhook Trigger** - Receive delivery document info from Flask
2. **HTTP Request** - Download PDF from Flask server
3. **PDF Extract** - Extract text/OCR from PDF
4. **Claude API** - Send to Claude with prompt
5. **Parse Response** - Extract JSON data
6. **HTTP Request** - Send back to Flask webhook

**Prompt Template for Claude:**
```
Extract all delivered items from this delivery order document.
Return JSON format:

{
  "delivery_order_number": "DO-2025-001",
  "delivery_date": "2025-10-01",
  "items": [
    {
      "item_name": "Shower Head",
      "quantity": 10,
      "unit": "pieces",
      "delivered": true
    },
    {
      "item_name": "Basin Mixer",
      "quantity": 12,
      "unit": "pieces",
      "delivered": true
    }
  ],
  "total_items_delivered": 22,
  "supplier": "Al Haramain Sanitary Trading LLC"
}
```

**Tasks:**
- [ ] Create n8n workflow
- [ ] Set up webhook endpoints
- [ ] Configure Claude API credentials
- [ ] Test with sample PDF
- [ ] Handle errors gracefully

**Deliverable:** Working n8n workflow that extracts delivery items

---

### Phase 3: Flask Integration (Week 2, Days 1-3)
**Goal:** Integrate n8n workflow with Flask

**Tasks:**
- [ ] Create API endpoint to trigger n8n: `/api/deliveries/<id>/extract`
- [ ] Create webhook endpoint to receive results: `/api/webhooks/delivery-extraction`
- [ ] Store extracted data in database
- [ ] Update delivery percentage based on extracted items
- [ ] Add processing status field (pending, processing, completed, failed)
- [ ] Create UI to show extraction status
- [ ] Add retry mechanism for failed extractions

**New Database Fields:**
```python
class Delivery(db.Model):
    # ... existing fields ...
    
    # Document Intelligence Fields
    extracted_data = db.Column(db.JSON)  # Store full extracted JSON
    extraction_status = db.Column(db.String(50))  # pending, processing, completed, failed
    extraction_date = db.Column(db.DateTime)
    extraction_confidence = db.Column(db.Float)  # 0-100%
    extracted_item_count = db.Column(db.Integer)
```

**API Endpoints:**
```python
# Trigger extraction
POST /api/deliveries/<id>/extract
Request: { "force": false }  # force re-extraction
Response: { "status": "processing", "job_id": "123" }

# Receive extraction results
POST /api/webhooks/delivery-extraction
Request: {
    "delivery_id": 1,
    "status": "completed",
    "data": { /* extracted items */ },
    "confidence": 92.5
}

# Get extraction status
GET /api/deliveries/<id>/extraction-status
Response: {
    "status": "completed",
    "extracted_items": 22,
    "confidence": 92.5,
    "date": "2025-10-04T14:30:00Z"
}
```

**Deliverable:** Full integration between Flask and n8n

---

### Phase 4: Chatbot Enhancement (Week 2, Days 4-5)
**Goal:** Enable chatbot to answer delivery queries

**Tasks:**
- [ ] Create function to search extracted delivery data
- [ ] Update chatbot prompt to include delivery context
- [ ] Add commands: "Has [item] been delivered?"
- [ ] Add commands: "Show deliveries for PO-XXX"
- [ ] Add commands: "What's pending for PO-XXX?"
- [ ] Format responses with delivery details
- [ ] Show quantities and dates

**Chatbot Query Examples:**
```
User: "Has the shower mixer been delivered?"
Bot: "✅ Yes! 8 shower mixers were delivered on Oct 1, 2025
     Delivery Order: DO-2025-001
     PO: PO-2025-001 (Sanitary Wares)
     Received by: Ahmed Hassan"

User: "What's pending for PO-2025-001?"
Bot: "⏳ Pending items for PO-2025-001:
     • WCs: 2 pieces (4/6 delivered)
     • Shattafs: 15 pieces (0/15 delivered)
     Expected delivery: Oct 11, 2025"

User: "Show me all deliveries"
Bot: "📦 Recent Deliveries:
     1. DO-2025-001 - 65% complete - Oct 1, 2025
        • Shower heads (10), Mixers (8), WCs (4/6)
     2. DO-2025-002 - 100% complete - Sep 28, 2025
        • UV-resistant PVC conduits - Full delivery"
```

**Deliverable:** Chatbot can answer delivery-related questions

---

### Phase 5: Auto-Calculate Delivery % (Week 3, Days 1-2)
**Goal:** Automatically update delivery percentage

**Logic:**
```python
def calculate_delivery_percentage(po_id, extracted_items):
    # Get PO total items from initial delivery or PO specification
    # Compare extracted delivered items vs total
    # Calculate percentage
    # Update delivery record
    
    Example:
    PO-2025-001 Total Items: 51
    Delivered in DO-2025-001: 32 items
    Percentage: 32/51 = 62.7% → Round to 63%
```

**Tasks:**
- [ ] Create calculation function
- [ ] Integrate with extraction webhook
- [ ] Auto-update delivery_percentage field
- [ ] Handle multiple deliveries per PO
- [ ] Cumulative percentage calculation
- [ ] Validation and error handling

**Deliverable:** Delivery percentage updates automatically

---

## 🔧 Implementation Plan

### Step 1: Database Schema Update (Day 1)
```bash
# Create migration script
python scripts/create_sprint2_migration.py
```

**Add to Delivery model:**
- `extracted_data` (JSON)
- `extraction_status` (String)
- `extraction_date` (DateTime)
- `extraction_confidence` (Float)
- `extracted_item_count` (Integer)

---

### Step 2: File Upload (Day 1-2)

**Update Delivery Form HTML:**
```html
<!-- Add to templates/deliveries.html -->
<div>
    <label class="block text-gray-700 font-semibold mb-2">
        Upload Delivery Order (PDF)
    </label>
    <input 
        type="file" 
        id="delivery-document" 
        accept=".pdf"
        class="w-full border rounded-lg px-3 py-2"
    >
    <p class="text-xs text-gray-500 mt-1">
        PDF only. Max 10MB. Will be processed for item extraction.
    </p>
</div>

<!-- Show extraction status -->
<div id="extraction-status" class="hidden mt-3">
    <div class="bg-blue-50 border-l-4 border-blue-500 p-3">
        <div class="flex items-center">
            <i class="fas fa-robot text-blue-500 mr-2"></i>
            <span class="text-blue-700 text-sm" id="extraction-message">
                Processing document...
            </span>
        </div>
    </div>
</div>
```

**Update Delivery Save JavaScript:**
```javascript
async function saveDeliveryWithDocument() {
    const formData = new FormData();
    formData.append('po_id', $('#purchase-order-id').val());
    formData.append('delivery_status', $('#delivery-status').val());
    formData.append('delivery_percentage', $('#delivery-percentage').val());
    // ... other fields ...
    
    // Add file if present
    const fileInput = document.getElementById('delivery-document');
    if (fileInput.files.length > 0) {
        formData.append('document', fileInput.files[0]);
    }
    
    // Upload
    const response = await fetch('/api/deliveries', {
        method: 'POST',
        body: formData  // Don't set Content-Type, browser will set it
    });
    
    const result = await response.json();
    
    // If document uploaded, trigger extraction
    if (result.document_uploaded && result.delivery_id) {
        await triggerExtraction(result.delivery_id);
    }
}

async function triggerExtraction(deliveryId) {
    showExtractionStatus('Processing document...');
    
    const response = await fetch(`/api/deliveries/${deliveryId}/extract`, {
        method: 'POST'
    });
    
    const result = await response.json();
    
    if (result.status === 'processing') {
        pollExtractionStatus(deliveryId);
    }
}

function pollExtractionStatus(deliveryId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/deliveries/${deliveryId}/extraction-status`);
        const status = await response.json();
        
        if (status.status === 'completed') {
            clearInterval(interval);
            showExtractionStatus(`✓ Extracted ${status.extracted_items} items (${status.confidence}% confidence)`);
            loadDeliveries();  // Refresh table
        } else if (status.status === 'failed') {
            clearInterval(interval);
            showExtractionStatus('✗ Extraction failed', 'error');
        }
    }, 3000);  // Poll every 3 seconds
}
```

---

### Step 3: n8n Workflow (Day 3-4)

**Workflow Configuration:**
```json
{
  "name": "Delivery Order Document Extraction",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "delivery-extraction",
        "responseMode": "lastNode"
      }
    },
    {
      "name": "Download PDF",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $json.document_url }}",
        "method": "GET",
        "responseFormat": "file"
      }
    },
    {
      "name": "Extract PDF Text",
      "type": "@n8n/n8n-nodes-langchain.documentPdfLoader"
    },
    {
      "name": "Claude API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "headers": {
          "x-api-key": "{{ $credentials.anthropicApiKey }}",
          "anthropic-version": "2023-06-01",
          "content-type": "application/json"
        },
        "body": {
          "model": "claude-3-5-sonnet-20241022",
          "max_tokens": 4096,
          "messages": [{
            "role": "user",
            "content": "Extract delivery items from this document:\n\n{{ $json.text }}\n\nReturn JSON with items array."
          }]
        }
      }
    },
    {
      "name": "Parse Response",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Parse Claude response and extract JSON"
      }
    },
    {
      "name": "Send to Flask",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:5000/api/webhooks/delivery-extraction",
        "method": "POST",
        "body": {
          "delivery_id": "={{ $('Webhook').item.json.delivery_id }}",
          "status": "completed",
          "data": "={{ $json }}",
          "confidence": 92.5
        }
      }
    }
  ]
}
```

---

## 📊 Sprint 2 Timeline

### Week 1
**Days 1-2:** Document Upload & Storage
- ✅ Add file upload to delivery form
- ✅ Create upload API
- ✅ Test file storage

**Days 3-4:** n8n Workflow Setup
- ✅ Create n8n workflow
- ✅ Set up Claude API
- ✅ Test with sample PDF

**Day 5:** Integration Testing
- ✅ Test end-to-end flow
- ✅ Fix any issues

### Week 2
**Days 1-3:** Flask Integration
- ✅ Create extraction endpoints
- ✅ Store extracted data
- ✅ Update delivery percentage

**Days 4-5:** Chatbot Enhancement
- ✅ Add delivery query functions
- ✅ Test chatbot responses

### Week 3
**Days 1-2:** Auto-Calculate & Polish
- ✅ Implement auto-percentage
- ✅ UI improvements
- ✅ Error handling

**Days 3-5:** Testing & Documentation
- ✅ Full system testing
- ✅ User documentation
- ✅ Deploy to production

---

## 🎯 First Task: Database Migration

Ready to start? Let's create the database migration first!

**Should I create:**
1. Database migration script for new fields?
2. File upload endpoint code?
3. Updated delivery form with upload?
4. All of the above?

Let me know and I'll generate the code! 🚀
