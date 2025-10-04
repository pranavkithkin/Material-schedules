# Sprint 2 Quick Reference Card

## 🎯 Current Status
**Phase 1: COMPLETE ✅**  
**Next: Phase 2 - n8n Setup**

---

## 📁 Important Files

### Documentation
```
SPRINT_2_PLAN.md              # Overall 3-week plan
SPRINT_2_PROGRESS.md          # Detailed progress tracking
N8N_SETUP_GUIDE.md            # Step-by-step n8n setup
SPRINT_2_PHASE_1_COMPLETE.md  # This phase summary
```

### Code Files Changed
```
models/delivery.py            # Added 5 new fields
templates/deliveries.html     # Added upload UI
routes/deliveries.py          # Updated create/update
routes/uploads.py             # Added upload endpoint
routes/n8n_webhooks.py        # Added webhook receiver
migrations/sprint2_*.py       # Database migration
```

---

## 🗄️ Database Changes

### New Fields in `deliveries` table:
```sql
extracted_data          JSON          -- Full extraction results
extraction_status       VARCHAR(50)   -- pending/processing/completed/failed
extraction_date         DATETIME      -- Completion timestamp
extraction_confidence   FLOAT         -- AI confidence 0-100%
extracted_item_count    INTEGER       -- Number of items found
```

### Migration Command:
```bash
python migrations/sprint2_document_intelligence.py
# Status: ✅ Already executed
```

---

## 🔌 API Endpoints

### 1. Upload Document
```http
POST /api/deliveries/<delivery_id>/upload-document
Content-Type: multipart/form-data

file: delivery_order.pdf
uploaded_by: "User Name"
```

**Response:**
```json
{
  "success": true,
  "delivery_id": 1,
  "file_id": 5,
  "extraction_status": "pending"
}
```

### 2. Receive Extraction (from n8n)
```http
POST /api/n8n/delivery-extraction
X-API-Key: your_api_key
Content-Type: application/json

{
  "delivery_id": 1,
  "extraction_status": "completed",
  "extraction_confidence": 92.5,
  "extracted_data": {
    "items": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "extraction_status": "completed",
  "delivery_percentage": 100.0,
  "delivery_status": "Delivered"
}
```

---

## 🚀 Next Steps (Phase 2)

### 1. Install n8n
```bash
# Docker (Recommended)
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# Or npm
npm install n8n -g
n8n start
```

### 2. Get Claude API Key
1. Go to https://console.anthropic.com/
2. Create account / Sign in
3. Go to API Keys
4. Create new key
5. Copy key (starts with `sk-ant-...`)

### 3. Create n8n Workflow
**Follow:** `N8N_SETUP_GUIDE.md` (detailed guide)

**Nodes Required:**
1. Webhook Trigger (receives from Flask)
2. Read Binary File (loads PDF)
3. Convert to Base64 (prepares for Claude)
4. HTTP Request (calls Claude API)
5. Parse Response (extracts JSON)
6. HTTP Request (sends to Flask webhook)
7. Log Results (optional)

**Workflow URL:** `http://localhost:5678/webhook/extract-delivery`

### 4. Update Flask Configuration

**Edit `.env`:**
```bash
# Add this line
N8N_WEBHOOK_URL=http://localhost:5678/webhook/extract-delivery
```

**Edit `routes/uploads.py` (line 353):**
```python
# Uncomment this section:
import requests
import os

n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL')
response = requests.post(n8n_webhook_url, json={
    'delivery_id': delivery_id,
    'file_id': file_record.id,
    'file_path': os.path.abspath(file_path),
    'po_ref': delivery.purchase_order.po_ref if delivery.purchase_order else None
})
```

### 5. Test End-to-End

```bash
# Start n8n (Terminal 1)
docker run -p 5678:5678 n8nio/n8n

# Start Flask (Terminal 2)
python app.py

# Open browser
http://localhost:5000/deliveries

# Upload test PDF
1. Click "Add Delivery"
2. Fill form
3. Upload PDF
4. Click "Save"
5. Watch extraction status update
```

---

## 🔍 Troubleshooting

### Upload Not Working
```bash
# Check file size
ls -lh static/uploads/

# Check permissions
chmod 755 static/uploads/

# Check Flask logs
tail -f app.log
```

### n8n Not Receiving Webhook
```bash
# Test manually
curl -X POST http://localhost:5678/webhook/extract-delivery \
  -H "Content-Type: application/json" \
  -d '{"delivery_id":1,"file_path":"/path/to/file.pdf"}'

# Check n8n logs
docker logs n8n
```

### Flask Not Receiving Result
```bash
# Test webhook manually
curl -X POST http://localhost:5000/api/n8n/delivery-extraction \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"delivery_id":1,"extraction_status":"completed"}'

# Check API key
echo $API_KEY  # from .env
```

---

## 📊 Auto-Calculation Logic

**How it works:**
1. n8n sends extracted items with `delivered: true/false`
2. Flask webhook counts delivered vs total
3. Calculates percentage: `(delivered / total) × 100`
4. Updates status:
   - 100% → "Delivered"
   - 1-99% → "Partial"
   - 0% → "Pending"

**Example:**
```json
"items": [
  {"item": "Mixer", "delivered": true},   // Delivered
  {"item": "Basin", "delivered": true},   // Delivered
  {"item": "Faucet", "delivered": false}  // Not delivered
]

// Result:
// 2 delivered / 3 total = 66.67%
// Status: "Partial"
```

---

## 🎨 UI Elements Added

### File Upload Section
```html
📄 Upload Delivery Order (PDF)
[Choose File] delivery_order.pdf
✨ AI will automatically extract items and quantities
```

### Extraction Status Display
```
🔄 Processing document...           Confidence: 92%

Extracted Items: ▼
• Shower Mixer - Model SM-500 - 20 pcs ✓
• Basin Mixer - Model BM-300 - 15 pcs ✓
```

---

## ⚙️ Configuration Files

### `.env` (Add These)
```bash
N8N_WEBHOOK_URL=http://localhost:5678/webhook/extract-delivery
CLAUDE_API_KEY=sk-ant-xxxxx  # For n8n
API_KEY=your_flask_api_key    # Existing
```

### n8n Credentials
```
1. Claude API Key
   Type: Header Auth
   Name: x-api-key
   Value: sk-ant-xxxxx

2. Flask API Key
   Type: Header Auth
   Name: X-API-Key
   Value: your_flask_api_key
```

---

## 💰 Costs (Estimated)

### Claude API (Sonnet)
- **Per extraction:** ~$0.013
- **100 deliveries/month:** $1.30
- **1,000 deliveries/month:** $13.00

### n8n
- **Self-hosted:** Free
- **n8n Cloud:** $20/month (includes 2,500 workflows)

### Total Monthly Cost
- **Small usage (100 docs):** ~$1-21
- **Medium usage (1,000 docs):** ~$13-33
- **Large usage (5,000 docs):** ~$65-85

---

## 📞 Support Resources

### Documentation
- **Claude API:** https://docs.anthropic.com/
- **n8n:** https://docs.n8n.io/
- **Flask Upload:** https://flask.palletsprojects.com/patterns/fileuploads/

### Internal Docs
- **Setup:** `N8N_SETUP_GUIDE.md`
- **Progress:** `SPRINT_2_PROGRESS.md`
- **Completed:** `SPRINT_2_PHASE_1_COMPLETE.md`

---

## ✅ Phase 1 Checklist

- [x] Database migration executed
- [x] Delivery model updated
- [x] File upload UI added
- [x] Upload API endpoint created
- [x] Webhook receiver created
- [x] Auto-calculation logic implemented
- [x] Documentation completed

**Status: 100% COMPLETE ✅**

---

## 📅 Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Foundation | 3 days | ✅ Complete |
| Phase 2: n8n Setup | 2 days | ⏳ Next |
| Phase 3: Frontend | 3 days | ⏳ Pending |
| Phase 4: Chatbot | 2 days | ⏳ Pending |
| Phase 5: Testing | 1 day | ⏳ Pending |
| **Total** | **11 days** | **27% done** |

---

## 🎯 Success Metrics

### Phase 1 (Current)
- [x] All database fields added
- [x] API endpoints functional
- [x] UI components rendered
- [x] Code documented

### Phase 2 (Next)
- [ ] n8n workflow created
- [ ] Claude API integrated
- [ ] End-to-end test passes
- [ ] Extraction accuracy >80%

---

**Last Updated:** January 15, 2025  
**Current Phase:** 1 of 5 (COMPLETE)  
**Next Milestone:** n8n workflow setup  
**ETA:** 2 days
