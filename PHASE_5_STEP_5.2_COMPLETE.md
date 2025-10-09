# Phase 5 Step 5.2: n8n Webhook Endpoints - COMPLETE ✓

## 🎉 What We Just Built

### 3 New Endpoints Added to `routes/n8n_webhooks.py`

#### 1. POST `/api/n8n/lpo-extract-quote`
**Purpose**: Extract data from uploaded supplier quotation

**Input**: 
- multipart/form-data with 'file' field
- Accepts: PDF, DOCX, XLSX files
- Max size: 20MB (validated in frontend)

**Process**:
1. Receives uploaded quote file
2. Validates file type and size
3. Saves to `uploads/temp/lpo_quotes/`
4. (Production) Calls n8n workflow with AI extraction
5. (Current) Returns mock extracted data

**Output**:
```json
{
  "success": true,
  "data": {
    "supplier": {
      "name": "ABC Steel Trading LLC",
      "trn": "100123456700003",
      "address": "Industrial Area 3, Sharjah, UAE",
      "tel": "+971-6-1234567",
      "contact_person": "Mohammed Ahmed"
    },
    "quote_ref": "QT-2025-001",
    "quote_date": "2025-10-05",
    "project_name": "Villa Construction - Al Barsha",
    "column_structure": ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
    "items": [
      {
        "number": 1,
        "make": "Tata Steel",
        "code": "TMT-16",
        "description": "TMT Steel Bar 16mm",
        "unit": "Ton",
        "quantity": 5.0,
        "rate": 2800.00
      }
    ],
    "terms": {
      "payment": "30 days from delivery",
      "delivery": "Within 7 days from PO"
    },
    "confidence": 95
  }
}
```

**Features**:
- ✅ File validation (type and size)
- ✅ Secure file storage with timestamps
- ✅ Mock data for testing (3 steel items)
- ✅ 2-second simulated processing delay
- ✅ Error handling with detailed messages

---

#### 2. POST `/api/n8n/lpo-generate-pdf`
**Purpose**: Generate LPO PDF from finalized form data

**Input**:
```json
{
  "supplier": {...},
  "project_name": "Villa Construction",
  "project_location": "Dubai",
  "quote_ref": "QT-2025-001",
  "quote_date": "2025-10-05",
  "column_structure": ["MAKE", "CODE", "DESCRIPTION", ...],
  "items": [...],
  "terms": {
    "payment": "30 days",
    "delivery": "7 days"
  }
}
```

**Process**:
1. Validates required fields (supplier, items)
2. Generates LPO number: `LPO/PKP/YYYY/NNNN`
3. Calculates totals (subtotal, VAT 5%, grand total)
4. Saves LPO to database
5. Generates PDF using WeasyPrint
6. Saves PDF to `uploads/lpos/`
7. Returns download URL

**Output**:
```json
{
  "success": true,
  "lpo_number": "LPO/PKP/2025/0001",
  "lpo_id": 1,
  "pdf_url": "/api/n8n/lpo-download/1",
  "pdf_path": "uploads/lpos/LPO_PKP_2025_0001.pdf",
  "totals": {
    "subtotal": 25050.00,
    "vat_amount": 1252.50,
    "grand_total": 26302.50
  },
  "message": "LPO generated successfully"
}
```

**Features**:
- ✅ Auto LPO number generation
- ✅ Auto-calculate item amounts
- ✅ VAT calculation (5%)
- ✅ Database persistence
- ✅ PDF generation with WeasyPrint
- ✅ Error handling with traceback

---

#### 3. GET `/api/n8n/lpo-download/<lpo_id>`
**Purpose**: Download generated LPO PDF

**Input**: 
- URL parameter: `lpo_id` (integer)

**Process**:
1. Fetches LPO from database
2. Validates PDF file exists
3. Returns PDF file for download

**Output**:
- PDF file with proper headers
- Filename: `LPO_PKP_2025_0001.pdf`
- Content-Type: `application/pdf`
- As attachment (triggers download)

**Features**:
- ✅ Database lookup
- ✅ File existence validation
- ✅ Proper download headers
- ✅ Error handling (404 if not found)

---

## 🔄 Integration with Existing System

### Uses Existing Components:
1. **models/lpo.py** - LPO database model
2. **services/lpo_service.py** - Business logic
   - `generate_lpo_number()` - Auto-incrementing
   - `create_lpo(data)` - Database save
3. **services/lpo_pdf_generator.py** - PDF generation
   - `generate_pdf(lpo, path)` - WeasyPrint rendering

### Database Flow:
```
Upload Quote
    ↓
Extract Data (n8n endpoint)
    ↓
User Reviews/Edits Form
    ↓
Generate PDF (n8n endpoint)
    ↓
LPOService.generate_lpo_number()
    ↓
LPOService.create_lpo() → Database
    ↓
LPOPDFGenerator.generate_pdf() → File
    ↓
Return PDF URL to frontend
```

---

## 🧪 How to Test

### Test 1: Extract Quote Data
```bash
# Upload a quote file
curl -X POST http://localhost:5001/api/n8n/lpo-extract-quote \
  -F "file=@sample_quote.pdf"
```

**Expected**:
- Status: 200 OK
- JSON with extracted supplier, items, terms
- File saved in `uploads/temp/lpo_quotes/`

### Test 2: Generate LPO PDF
```bash
# Send extracted data
curl -X POST http://localhost:5001/api/n8n/lpo-generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "supplier": {
      "name": "Test Supplier",
      "trn": "123456789"
    },
    "items": [
      {
        "description": "Test Item",
        "quantity": 1,
        "rate": 100
      }
    ]
  }'
```

**Expected**:
- Status: 200 OK
- LPO number generated
- PDF saved in `uploads/lpos/`
- Download URL returned

### Test 3: Download PDF
```bash
# Download generated PDF
curl -O http://localhost:5001/api/n8n/lpo-download/1
```

**Expected**:
- PDF file downloaded
- Filename: `LPO_PKP_2025_0001.pdf`

---

## 🔧 Frontend Integration

### Updated JavaScript in `chat.html`

The `extractQuoteData()` function now calls:
```javascript
const response = await fetch('/api/n8n/lpo-extract-quote', {
    method: 'POST',
    body: formData  // Contains uploaded file
});
```

The `generateLPOPDF()` function will call:
```javascript
const response = await fetch('/api/n8n/lpo-generate-pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(lpoData)  // Finalized form data
});
```

---

## 🎯 Current vs Production

### Current Implementation (Mock):
```python
# Mock extracted data for testing
extracted_data = {
    "supplier": {...},
    "items": [...]  # 3 steel items
}
```

### Production Implementation (TODO):
```python
# Call actual n8n workflow
response = requests.post(
    'https://your-n8n-instance.com/webhook/lpo-extract',
    files={'file': open(file_path, 'rb')}
)
extracted_data = response.json()
```

**Benefits of n8n approach**:
- Separate AI processing from Flask app
- Can use different AI models (GPT-4, Claude, etc.)
- Easy to add pre/post processing steps
- Workflow versioning and monitoring
- Can handle long-running extractions

---

## 📊 Error Handling

### Handled Scenarios:

1. **No file uploaded**
   - Status: 400
   - Message: "No file uploaded"

2. **Invalid file type**
   - Status: 400
   - Message: "Invalid file type. Allowed: .pdf, .docx, .xlsx"

3. **Missing required fields**
   - Status: 400
   - Message: "Missing required field: supplier"

4. **Database errors**
   - Status: 500
   - Includes traceback for debugging

5. **File not found**
   - Status: 404
   - Message: "PDF file not found"

---

## 📁 Files Modified

### `routes/n8n_webhooks.py`
**Lines added**: ~300 lines

**Changes**:
1. Added `/lpo-extract-quote` endpoint
2. Added `/lpo-generate-pdf` endpoint
3. Added `/lpo-download/<id>` endpoint
4. Integrated with existing LPO services
5. Added comprehensive error handling

---

## ✅ Step 5.2 Complete!

### What Works:
- ✅ File upload handling
- ✅ File validation (type, size)
- ✅ Mock data extraction (3 items)
- ✅ LPO number generation
- ✅ Database persistence
- ✅ PDF generation
- ✅ PDF download
- ✅ Error handling

### What's Next (Step 5.3):
- [ ] Render dynamic LPO form
- [ ] Populate form with extracted data
- [ ] Items table with add/remove rows
- [ ] Auto-calculate totals
- [ ] Form validation
- [ ] Save draft functionality
- [ ] Generate LPO button integration

---

## 🚀 Test the Flow Now

1. **Start Flask server**:
   ```bash
   python app.py
   ```

2. **Visit chat page**:
   ```
   http://localhost:5001/chat
   ```

3. **Click "Add New LPO"**

4. **Upload any file (PDF recommended)**
   - Wait 2 seconds for "extraction"
   - Should see extracted data in console

5. **Check database**:
   ```python
   # Python shell
   from app import create_app
   from models.lpo import LPO
   
   app = create_app()
   with app.app_context():
       lpos = LPO.query.all()
       print(f"LPOs in database: {len(lpos)}")
   ```

---

**Time Spent**: ~45 minutes  
**Progress**: Step 5.2 Complete ✓ (50% of Phase 5)  
**Next**: Step 5.3 (Dynamic Form Logic - 2 hours)

**Ready for Step 5.3?** 🎨
