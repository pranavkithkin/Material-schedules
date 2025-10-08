# 📄 PHASE 5: Automated LPO Generation System

**Feature Name:** Automated Local Purchase Order (LPO) Generation  
**Priority:** HIGH  
**Status:** 📋 Planning  
**Estimated Effort:** 2-3 days  
**Target Completion:** TBD

---

## 🎯 FEATURE OVERVIEW

### **Objective**
Streamline LPO creation by:
1. Extracting data from supplier quotations (PDF/Email)
2. Auto-populating LPO template with extracted data
3. Allowing user to review/edit before generation
4. Generating professional PDF LPO documents
5. Auto-linking LPO to material tracking system

### **Business Value**
- ⏱️ **Time Savings:** Reduce LPO creation from 15 minutes to 2 minutes
- ✅ **Accuracy:** Eliminate manual data entry errors
- 📊 **Tracking:** Automatic integration with delivery dashboard
- 🤖 **Automation:** AI-powered quote extraction
- 📄 **Professional:** Consistent, branded LPO documents

---

## 📋 LPO DOCUMENT ATTRIBUTES

### **Required Fields (All marked ✓)**

| Field | Source | Type | Example | AI Extractable |
|-------|--------|------|---------|----------------|
| **LPO No** | Auto-generated | String | PKP-LPO-6001-2025-101 | ✅ No (system) |
| **LPO Date** | System date | Date | 2025-10-08 | ✅ No (system) |
| **Project** | User/Database | String | Villa 6001 | ⚠️ May need prompt |
| **Supplier** | Quote/Database | String | ABC Trading LLC | ✅ Yes |
| **Quotation Ref** | Quote | String | QT-2025-1234 | ✅ Yes |
| **Quotation Date** | Quote | Date | 2025-10-01 | ✅ Yes |
| **Address** | Quote/Database | Text | P.O. Box 12345, Dubai | ✅ Yes |
| **TRN** | Quote/Database | String | 123456789012345 | ✅ Yes |
| **Contact Person** | Quote/Database | String | John Smith | ✅ Yes |
| **Contact** | Quote/Database | String | +971 50 123 4567 | ✅ Yes |
| **Items Table** | Quote | Array | See below | ✅ Yes |
| **Payment Terms** | Quote/Standard | Text | 30% advance, 70% on delivery | ✅ Yes |
| **Delivery Date** | User/Quote | Date | 2025-10-20 | ✅ Yes |

### **Items Table Structure**

| Field | Type | Required | Example |
|-------|------|----------|---------|
| Item No | Integer | ✅ | 1 |
| Description | Text | ✅ | VRF System - 10 TR |
| Quantity | Number | ✅ | 5 |
| Unit | String | ✅ | Set |
| Unit Price | Decimal | ✅ | 25,000.00 |
| Total Price | Decimal | ✅ | 125,000.00 |

### **Calculated Fields**

| Field | Calculation | Example |
|-------|-------------|---------|
| Subtotal | Sum of all item totals | AED 125,000.00 |
| VAT (5%) | Subtotal × 0.05 | AED 6,250.00 |
| **Grand Total** | Subtotal + VAT | **AED 131,250.00** |

---

## 🔄 WORKFLOW

### **Step 1: Upload Quote** 📤
```
User → Upload supplier quotation (PDF/Image/Email)
     → System extracts text using OCR/PDF parser
     → AI (GPT-4) identifies and extracts LPO fields
```

### **Step 2: Review & Edit** ✏️
```
System → Shows extracted data in form
User → Reviews fields (green = high confidence, yellow = needs review)
     → Edits/confirms missing fields
     → Selects project from dropdown
     → Confirms delivery date
```

### **Step 3: Generate LPO** 🎨
```
System → Generates LPO number (PKP-LPO-6001-2025-XXX)
       → Populates professional PDF template
       → Applies company branding (logo, colors)
       → Adds terms & conditions
       → Calculates totals, VAT, grand total
```

### **Step 4: Save & Track** 💾
```
System → Saves LPO PDF to database
       → Creates PurchaseOrder record
       → Links to Material record
       → Sets up delivery tracking
       → Sends notification (optional)
```

### **Step 5: Distribution** 📧
```
User → Reviews final PDF
     → Downloads/prints LPO
     → (Optional) Emails to supplier directly from system
     → (Optional) Uploads signed copy back
```

---

## 🏗️ TECHNICAL ARCHITECTURE

### **Frontend Components**

1. **LPO Creation Page** (`templates/lpo_create.html`)
   - Upload zone for quotation
   - Extraction progress indicator
   - Editable form with validation
   - Live PDF preview
   - Generate button

2. **LPO List Page** (`templates/lpo_list.html`)
   - Table of all generated LPOs
   - Filters (by supplier, date, project, status)
   - Search functionality
   - Quick actions (view, download, email, void)

3. **LPO View Page** (`templates/lpo_view.html`)
   - Display LPO details
   - Embedded PDF viewer
   - Status tracking (Draft → Issued → Acknowledged → Completed)
   - Linked deliveries and payments

### **Backend Components**

1. **Model** (`models/lpo.py`)
```python
class LPO(db.Model):
    id = Integer (PK)
    lpo_number = String(50) unique, indexed
    lpo_date = Date
    project_name = String(200)
    supplier_id = Integer (FK to Supplier)
    quotation_ref = String(100)
    quotation_date = Date
    supplier_address = Text
    supplier_trn = String(20)
    contact_person = String(100)
    contact_number = String(50)
    items = JSON  # Array of items
    subtotal = Decimal
    vat_amount = Decimal
    grand_total = Decimal
    payment_terms = Text
    delivery_date = Date
    status = String(20)  # Draft, Issued, Acknowledged, Completed, Void
    pdf_path = String(500)
    created_by = String(100)
    created_at = DateTime
    issued_at = DateTime
    acknowledged_at = DateTime
```

2. **Service** (`services/lpo_service.py`)
```python
class LPOService:
    def extract_from_quote(file_path):
        # AI extraction using GPT-4
        # Returns extracted fields with confidence scores
    
    def generate_lpo_number():
        # Auto-increment: PKP-LPO-6001-2025-XXX
    
    def create_lpo(data):
        # Validate and create LPO record
    
    def generate_pdf(lpo_id):
        # Generate PDF from template
        # Uses ReportLab or WeasyPrint
    
    def send_to_supplier(lpo_id, email):
        # Email LPO to supplier
```

3. **Routes** (`routes/lpo.py`)
```python
POST /api/lpo/extract          # Extract from quotation
POST /api/lpo/create           # Create LPO
GET  /api/lpo/<id>             # Get LPO details
GET  /api/lpo/<id>/pdf         # Download PDF
PUT  /api/lpo/<id>             # Update LPO
DELETE /api/lpo/<id>           # Void LPO
POST /api/lpo/<id>/issue       # Change status to Issued
POST /api/lpo/<id>/email       # Email to supplier
GET  /api/lpo/list             # List all LPOs
```

4. **AI Extraction Service** (`services/lpo_extraction.py`)
```python
class LPOExtractionService:
    def __init__(self):
        self.openai_client = openai  # GPT-4 for extraction
        self.ocr_engine = tesseract  # OCR for images
    
    def extract_from_pdf(file_path):
        # Extract text from PDF
        # Use GPT-4 to identify fields
        # Return structured data + confidence
    
    def extract_items_table(text):
        # Parse items table from quote
        # Handle various formats
    
    def validate_extraction(data):
        # Validate required fields
        # Flag low-confidence fields
```

5. **PDF Generator** (`services/pdf_generator.py`)
```python
class LPOPDFGenerator:
    def generate(lpo_data, template='default'):
        # Use HTML template + WeasyPrint
        # Or use ReportLab for more control
        # Apply branding
        # Return PDF bytes
    
    def get_template(template_name):
        # Load LPO template (HTML/CSS)
```

---

## 🎨 LPO PDF TEMPLATE DESIGN

### **Layout Structure**

```
┌─────────────────────────────────────────────┐
│  [COMPANY LOGO]           LOCAL PURCHASE    │
│  PKP Contracting LLC      ORDER             │
│  P.O. Box 6001, Dubai                       │
│  TRN: 123456789012345     LPO No: XXX       │
│                           Date: YYYY-MM-DD  │
├─────────────────────────────────────────────┤
│  PROJECT: Villa 6001                        │
├─────────────────────────────────────────────┤
│  SUPPLIER DETAILS:                          │
│  Name: ABC Trading LLC                      │
│  Address: P.O. Box 12345, Dubai, UAE        │
│  TRN: 987654321098765                       │
│  Contact: John Smith (+971 50 123 4567)     │
│  Quotation Ref: QT-2025-1234                │
│  Quotation Date: 2025-10-01                 │
├─────────────────────────────────────────────┤
│  ITEMS:                                     │
│  ┌──┬────────────┬────┬────┬───────┬──────┐│
│  │No│Description │Qty │Unit│ Rate  │Amount││
│  ├──┼────────────┼────┼────┼───────┼──────┤│
│  │1 │VRF System  │5   │Set │25,000 │125,000│
│  │2 │Installation│5   │Set │5,000  │25,000 │
│  └──┴────────────┴────┴────┴───────┴──────┘│
│                                             │
│                           Subtotal: 150,000 │
│                           VAT (5%): 7,500   │
│                           TOTAL:    157,500 │
├─────────────────────────────────────────────┤
│  PAYMENT TERMS:                             │
│  30% advance payment                        │
│  70% upon delivery                          │
│                                             │
│  DELIVERY DATE: 2025-10-20                  │
├─────────────────────────────────────────────┤
│  TERMS & CONDITIONS:                        │
│  1. Supplier must deliver as per schedule  │
│  2. All materials must meet specifications │
│  3. Invoice to be raised upon delivery     │
│  ...                                        │
├─────────────────────────────────────────────┤
│  AUTHORIZED SIGNATURE:                      │
│                                             │
│  ____________________                       │
│  Name: [Authorizer]                         │
│  Date: 2025-10-08                           │
└─────────────────────────────────────────────┘
```

---

## 🤖 AI EXTRACTION PROMPT

### **GPT-4 Prompt for Quote Extraction**

```python
SYSTEM_PROMPT = """
You are an expert at extracting structured data from supplier quotations 
for construction materials. Extract the following fields from the quotation 
document and return them in JSON format.

Required Fields:
- supplier_name: Company name
- supplier_address: Full address
- supplier_trn: Tax Registration Number (15 digits)
- contact_person: Name of contact person
- contact_number: Phone/mobile number
- quotation_ref: Quote reference number
- quotation_date: Date of quotation (YYYY-MM-DD)
- items: Array of items with:
  * description: Item description
  * quantity: Numeric quantity
  * unit: Unit of measurement (e.g., Set, Piece, Meter)
  * unit_price: Price per unit (numeric)
  * total_price: Total for this item (numeric)
- payment_terms: Payment terms text
- delivery_days: Delivery time (extract number of days)
- validity_days: Quote validity (extract number of days)

For each field, also provide a confidence score (0-100).

Return ONLY valid JSON. If a field is not found, use null.
"""

USER_PROMPT = """
Extract data from this quotation:

{extracted_text}

Return JSON with all fields and confidence scores.
"""
```

### **Sample Response**

```json
{
  "supplier_name": {
    "value": "ABC Trading LLC",
    "confidence": 95
  },
  "supplier_address": {
    "value": "P.O. Box 12345, Dubai, UAE",
    "confidence": 90
  },
  "supplier_trn": {
    "value": "123456789012345",
    "confidence": 100
  },
  "quotation_ref": {
    "value": "QT-2025-1234",
    "confidence": 98
  },
  "items": [
    {
      "description": "VRF Air Conditioning System - 10 TR",
      "quantity": 5,
      "unit": "Set",
      "unit_price": 25000.00,
      "total_price": 125000.00,
      "confidence": 95
    }
  ],
  "payment_terms": {
    "value": "30% advance, 70% on delivery",
    "confidence": 85
  }
}
```

---

## 📊 DATABASE SCHEMA

### **New Table: `lpo`**

```sql
CREATE TABLE lpo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lpo_number VARCHAR(50) UNIQUE NOT NULL,
    lpo_date DATE NOT NULL,
    project_name VARCHAR(200),
    supplier_id INTEGER,
    supplier_name VARCHAR(200),
    supplier_address TEXT,
    supplier_trn VARCHAR(20),
    contact_person VARCHAR(100),
    contact_number VARCHAR(50),
    quotation_ref VARCHAR(100),
    quotation_date DATE,
    items JSON,
    subtotal DECIMAL(12, 2),
    vat_percentage DECIMAL(5, 2) DEFAULT 5.0,
    vat_amount DECIMAL(12, 2),
    grand_total DECIMAL(12, 2),
    payment_terms TEXT,
    delivery_date DATE,
    status VARCHAR(20) DEFAULT 'Draft',
    pdf_path VARCHAR(500),
    quote_file_path VARCHAR(500),
    notes TEXT,
    created_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    issued_at DATETIME,
    acknowledged_at DATETIME,
    voided_at DATETIME,
    voided_reason TEXT,
    INDEX idx_lpo_number (lpo_number),
    INDEX idx_supplier (supplier_name),
    INDEX idx_status (status),
    INDEX idx_date (lpo_date)
);
```

### **Update Existing Table: `purchase_order`**

Add field to link LPO:
```sql
ALTER TABLE purchase_order ADD COLUMN lpo_id INTEGER;
ALTER TABLE purchase_order ADD FOREIGN KEY (lpo_id) REFERENCES lpo(id);
```

---

## 🎨 UI MOCKUPS

### **1. LPO Creation Page**

```
┌─────────────────────────────────────────────┐
│  📄 Create New LPO                          │
├─────────────────────────────────────────────┤
│                                             │
│  Step 1: Upload Supplier Quotation         │
│  ┌─────────────────────────────────────┐   │
│  │  📤 Drag & drop quote here          │   │
│  │     or click to browse               │   │
│  │                                      │   │
│  │  Supported: PDF, JPG, PNG            │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Recent Quotes:                             │
│  • QT-2025-1234 - ABC Trading (Yesterday)  │
│  • QT-2025-1233 - XYZ Suppliers (2 days)   │
│                                             │
│  Or: [Manual Entry] [From Template]        │
└─────────────────────────────────────────────┘
```

### **2. Review Extracted Data**

```
┌─────────────────────────────────────────────┐
│  ✨ Review Extracted Data                   │
├─────────────────────────────────────────────┤
│  LPO Details:                               │
│  LPO No:    PKP-LPO-6001-2025-101 (auto)   │
│  LPO Date:  2025-10-08 (today)             │
│  Project:   [Villa 6001 ▼] ⚠️              │
│                                             │
│  Supplier Details:                          │
│  Name:      ABC Trading LLC ✅ 95%         │
│  Address:   P.O. Box 12345, Dubai ✅ 90%   │
│  TRN:       123456789012345 ✅ 100%        │
│  Contact:   John Smith ✅ 95%              │
│  Phone:     +971 50 123 4567 ✅ 98%        │
│                                             │
│  Quote Details:                             │
│  Quote Ref: QT-2025-1234 ✅ 98%            │
│  Date:      2025-10-01 ✅ 100%             │
│                                             │
│  Items: (2 items extracted)                │
│  ┌────────────────────────────────────┐    │
│  │ 1. VRF System - 10 TR              │    │
│  │    Qty: 5 Set × AED 25,000         │    │
│  │    Total: AED 125,000 ✅           │    │
│  └────────────────────────────────────┘    │
│  [Add Item] [Edit] [Remove]                │
│                                             │
│  Payment Terms:                             │
│  30% advance, 70% on delivery ✅ 85%       │
│                                             │
│  Delivery Date: [2025-10-20] ⚠️            │
│                                             │
│  ✅ = High confidence (>90%)                │
│  ⚠️ = Needs review (<90% or missing)        │
│                                             │
│  [← Back] [Save Draft] [Generate LPO →]    │
└─────────────────────────────────────────────┘
```

### **3. Generated LPO Preview**

```
┌─────────────────────────────────────────────┐
│  ✅ LPO Generated Successfully!             │
├─────────────────────────────────────────────┤
│  LPO Number: PKP-LPO-6001-2025-101         │
│  Status: Draft                              │
│                                             │
│  ┌───────────────────────────────────┐     │
│  │ [PDF Preview]                     │     │
│  │                                   │     │
│  │ (Embedded PDF viewer)             │     │
│  │                                   │     │
│  └───────────────────────────────────┘     │
│                                             │
│  Actions:                                   │
│  [📥 Download PDF]                          │
│  [📧 Email to Supplier]                     │
│  [✅ Mark as Issued]                        │
│  [✏️ Edit LPO]                              │
│  [🗑️ Void LPO]                              │
│                                             │
│  [← Back to List] [Create Another]         │
└─────────────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTATION PHASES

### **Phase 5A: Core LPO System** (Day 1-2)

**Tasks:**
1. ✅ Create database model (`models/lpo.py`)
2. ✅ Create routes (`routes/lpo.py`)
3. ✅ Create basic service (`services/lpo_service.py`)
4. ✅ Create LPO creation page (`templates/lpo_create.html`)
5. ✅ Create LPO list page (`templates/lpo_list.html`)
6. ✅ Implement manual entry workflow
7. ✅ Generate LPO number logic
8. ✅ Basic PDF generation (simple template)

**Deliverables:**
- Manual LPO creation working
- LPO number auto-generated
- Basic PDF output
- LPO list and view pages

---

### **Phase 5B: AI Extraction** (Day 2-3)

**Tasks:**
1. ✅ Create extraction service (`services/lpo_extraction.py`)
2. ✅ Implement PDF text extraction
3. ✅ Integrate GPT-4 for field extraction
4. ✅ Add confidence scoring
5. ✅ Create review/edit interface
6. ✅ Handle items table extraction
7. ✅ Add validation logic

**Deliverables:**
- Upload quotation → Extract fields
- Review extracted data UI
- Confidence indicators
- Edit/correct functionality

---

### **Phase 5C: Professional PDF** (Day 3)

**Tasks:**
1. ✅ Design professional LPO template (HTML/CSS)
2. ✅ Add company branding (logo, colors)
3. ✅ Implement WeasyPrint or ReportLab
4. ✅ Add terms & conditions
5. ✅ Add signature section
6. ✅ Handle multi-page LPOs

**Deliverables:**
- Professional PDF output
- Branded template
- Print-ready format
- Multiple template options

---

### **Phase 5D: Integration & Polish** (Day 3-4)

**Tasks:**
1. ✅ Link LPO to PurchaseOrder
2. ✅ Auto-create PurchaseOrder from LPO
3. ✅ Add status workflow (Draft → Issued → Acknowledged)
4. ✅ Email LPO to supplier
5. ✅ Add search/filter on LPO list
6. ✅ Add LPO analytics to dashboard
7. ✅ Write tests

**Deliverables:**
- Full integration with existing system
- Email functionality
- Status tracking
- Analytics

---

## 📚 DEPENDENCIES

### **Python Libraries**

```txt
# PDF Generation
weasyprint==61.2         # HTML to PDF
reportlab==4.0.7         # Alternative PDF library

# PDF Reading
PyPDF2==3.0.1           # PDF text extraction
pdfplumber==0.10.3      # Better PDF parsing

# OCR (for scanned quotes)
pytesseract==0.3.10     # OCR engine
Pillow==10.1.0          # Image processing

# AI
openai==1.3.0           # GPT-4 API
anthropic==0.7.0        # Claude (alternative)

# Email
Flask-Mail==0.9.1       # Email sending
```

### **System Dependencies**

```bash
# For WeasyPrint
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# For OCR
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

---

## 🧪 TESTING STRATEGY

### **Unit Tests**

```python
# tests/test_lpo_service.py
def test_generate_lpo_number()
def test_create_lpo()
def test_calculate_totals()
def test_validate_lpo_data()

# tests/test_lpo_extraction.py
def test_extract_supplier_from_quote()
def test_extract_items_table()
def test_confidence_scoring()

# tests/test_pdf_generator.py
def test_generate_pdf()
def test_pdf_has_all_fields()
def test_multi_page_pdf()
```

### **Integration Tests**

```python
# tests/test_lpo_workflow.py
def test_full_lpo_creation_workflow()
def test_quote_upload_to_pdf_generation()
def test_lpo_to_purchase_order_link()
def test_email_lpo_to_supplier()
```

### **Manual Testing Checklist**

- [ ] Upload PDF quote → Extraction works
- [ ] Upload image quote → OCR + extraction works
- [ ] Review extracted data → All fields shown
- [ ] Edit low-confidence fields → Saves correctly
- [ ] Generate PDF → Professional output
- [ ] Download PDF → Opens correctly
- [ ] Email LPO → Supplier receives
- [ ] Change status → Workflow works
- [ ] Link to PO → Creates PO record
- [ ] Search LPOs → Finds correctly
- [ ] Filter LPOs → Filters work

---

## 📊 SUCCESS METRICS

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Time Savings** | 85% reduction | Manual (15 min) vs Automated (2 min) |
| **Accuracy** | 95%+ | Extracted fields vs manual verification |
| **Adoption** | 80%+ | LPOs generated via system vs manual |
| **User Satisfaction** | 4.5/5 | User feedback survey |
| **Error Rate** | <2% | Incorrect LPOs / Total LPOs |

---

## 🎯 USER STORIES

### **Story 1: Procurement Officer - Quick LPO Creation**
> "As a procurement officer, I want to upload a supplier quote and have the system automatically extract all details so that I can generate an LPO in under 2 minutes."

**Acceptance Criteria:**
- Upload quote (PDF/image)
- System extracts 90%+ fields correctly
- Review/edit extracted data
- Generate professional PDF
- Total time: <2 minutes

---

### **Story 2: Project Manager - Track LPOs**
> "As a project manager, I want to see all LPOs for my project with their status so that I can track procurement progress."

**Acceptance Criteria:**
- View LPO list filtered by project
- See status (Draft/Issued/Acknowledged)
- See linked deliveries and payments
- Export LPO report

---

### **Story 3: Accounts Team - Link LPO to PO**
> "As an accounts person, I want each LPO to automatically create a PurchaseOrder record so that I can track payments against approved LPOs."

**Acceptance Criteria:**
- LPO generates PO record automatically
- PO linked to LPO
- Payment tracking works
- Reports show LPO ↔ PO ↔ Payment flow

---

## 🚀 FUTURE ENHANCEMENTS

### **Phase 5+: Advanced Features**

1. **Multi-Currency Support**
   - Handle quotes in USD, EUR, AED
   - Auto currency conversion
   - Display both currencies on LPO

2. **E-Signature Integration**
   - Digital signature on LPO
   - Supplier acknowledgment via portal
   - Audit trail

3. **Supplier Portal**
   - Suppliers receive LPO notification
   - Accept/reject LPO online
   - Upload signed copy
   - Track delivery against LPO

4. **Approval Workflow**
   - Route LPO for approval based on amount
   - Multi-level approvals (Manager → Director → Finance)
   - Email notifications
   - Approval history

5. **Template Management**
   - Multiple LPO templates
   - Project-specific templates
   - Custom branding per project

6. **Bulk LPO Generation**
   - Upload multiple quotes
   - Generate LPOs in batch
   - Export all PDFs as ZIP

7. **Mobile App**
   - Take photo of quote → Generate LPO
   - Approve LPOs on mobile
   - Digital signature on mobile

---

## 📄 SAMPLE LPO TEMPLATES

### **Template Options**

1. **Standard Template**
   - Default PKP branding
   - Clean, professional layout
   - Suitable for most projects

2. **Detailed Template**
   - Additional fields (warranty, installation)
   - Detailed terms & conditions
   - Technical specifications section

3. **Minimal Template**
   - Compact layout
   - For simple orders
   - Quick print format

4. **Multi-Project Template**
   - Show multiple projects on one LPO
   - Consolidated orders
   - For regular suppliers

---

## 📋 NEXT STEPS

### **Immediate Actions:**

1. ✅ **Create sample LPO PDFs** (You mentioned doing this)
   - Create 1-2 actual LPO examples
   - Share with development team
   - Identify exact format requirements

2. ✅ **Review & approve this plan**
   - Confirm all fields are correct
   - Add any missing requirements
   - Prioritize features

3. ⏳ **Start Phase 5A implementation**
   - Create database model
   - Setup basic routes
   - Build creation UI

4. ⏳ **Test with real quotes**
   - Use actual supplier quotes
   - Validate extraction accuracy
   - Refine AI prompts

---

## 💬 QUESTIONS TO CLARIFY

1. **LPO Number Format:**
   - Confirm: `PKP-LPO-6001-2025-XXX` ?
   - What's the starting number?
   - Reset annually or continuous?

2. **VAT Calculation:**
   - Always 5%?
   - VAT inclusive or exclusive quotes?
   - Show VAT breakdown?

3. **Approval Required:**
   - Do LPOs need approval before issuing?
   - Who approves? (Manager/Finance)
   - Amount thresholds?

4. **Email Integration:**
   - Send LPO directly from system?
   - Email template required?
   - Track email opens?

5. **Supplier Database:**
   - Do we have existing supplier records?
   - Should we create Supplier model?
   - Link to existing data?

---

## 📊 ESTIMATED TIMELINE

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| 5A: Core System | 2 days | TBD | TBD |
| 5B: AI Extraction | 1 day | TBD | TBD |
| 5C: Professional PDF | 1 day | TBD | TBD |
| 5D: Integration | 1 day | TBD | TBD |
| Testing & Polish | 1 day | TBD | TBD |
| **Total** | **6 days** | **TBD** | **TBD** |

---

## 🎯 READY TO START?

This plan is ready for implementation! Next steps:

1. ✅ **You:** Create 1-2 sample LPO PDFs
2. ✅ **Review:** Confirm all requirements are captured
3. ✅ **Approve:** Give green light to start
4. 🚀 **Build:** Begin Phase 5A implementation

---

**Status:** 📋 **PLANNING COMPLETE - AWAITING SAMPLE LPOs**  
**Priority:** 🔴 **HIGH**  
**Estimated ROI:** ⏱️ **85% time savings, 95% accuracy improvement**

Let me know when you have the sample LPO PDFs ready, and we can start building! 🚀
