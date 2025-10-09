# Phase 5 REVISED: Integrated LPO System with n8n

## 🎯 New Approach: Dashboard Integration

Instead of standalone LPO routes, integrate LPO creation directly into the existing chat dashboard with n8n handling AI extraction.

---

## 📋 Implementation Plan

### Step 1: Add LPO Button to Chat Dashboard (30 min)
**File**: `templates/chat.html`

**Changes**:
- Add "Add New LPO" button above the chatbot section
- Position it prominently with icon (+ or document icon)
- Style consistently with existing dashboard UI

```html
<!-- Add before chat container -->
<div class="mb-4 flex justify-end">
    <button id="openLpoModal" class="bg-gradient-to-r from-green-500 to-blue-500 text-white px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-2">
        <i class="fas fa-plus-circle"></i>
        <span class="font-semibold">Add New LPO</span>
    </button>
</div>
```

---

### Step 2: Create LPO Modal/Drawer Component (1 hour)
**File**: `templates/chat.html` (add modal HTML)

**Sections**:
1. **Upload Section**
   - Drag & drop area for PDF/DOCX/XLSX
   - File type indicators
   - Upload progress bar

2. **Loading State**
   - Show spinner while n8n processes
   - "Extracting data from quotation..." message

3. **Editable Form (Pre-filled)**
   - Supplier details section
   - Quote reference & dates
   - Items table (add/remove rows)
   - Totals (auto-calculated)
   - Terms & conditions

4. **Action Buttons**
   - "Generate LPO" - sends to n8n
   - "Save Draft" - stores in database
   - "Cancel" - closes modal

**Layout Reference**: Use sample LPO from `sample documents/sample lpo/sample single page.pdf`

---

### Step 3: n8n Webhook Endpoints (30 min)
**File**: `routes/n8n_webhooks.py`

**Add Two New Endpoints**:

#### Endpoint 1: Extract Quote Data
```python
@n8n_bp.route('/lpo-extract-quote', methods=['POST'])
def lpo_extract_quote():
    """
    Receives uploaded quote file (PDF/DOCX/XLSX)
    Sends to n8n for AI extraction
    Returns structured JSON with supplier info, items, totals
    """
    # 1. Receive file upload
    # 2. Save temporarily
    # 3. Call n8n workflow for extraction
    # 4. Return JSON response
```

**Expected n8n Response**:
```json
{
    "supplier": {
        "name": "ABC Trading LLC",
        "trn": "100123456700003",
        "address": "Industrial Area, Sharjah",
        "tel": "+971-6-1234567",
        "contact_person": "Mohammed Ahmed",
        "contact_number": "+971-50-1234567"
    },
    "quote_ref": "QT-2025-001",
    "quote_date": "2025-10-05",
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
        "delivery": "Within 7 days",
        "payment": "30 days from delivery"
    },
    "confidence": 95
}
```

#### Endpoint 2: Generate LPO PDF
```python
@n8n_bp.route('/lpo-generate-pdf', methods=['POST'])
def lpo_generate_pdf():
    """
    Receives finalized LPO form data
    Sends to n8n for PDF generation
    Returns downloadable PDF file
    """
    # 1. Receive LPO data (after user edits)
    # 2. Generate LPO number (LPO/PKP/YYYY/NNNN)
    # 3. Save to database
    # 4. Call n8n for PDF generation
    # 5. Return PDF file URL
```

---

### Step 4: Frontend JavaScript Logic (1.5 hours)
**File**: `templates/chat.html` (add script section)

**Flow**:
```javascript
// 1. Open Modal
document.getElementById('openLpoModal').addEventListener('click', () => {
    showModal();
});

// 2. Handle File Upload
async function handleFileUpload(file) {
    showLoading('Extracting data from quotation...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/n8n/lpo-extract-quote', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    prefillForm(data);
    hideLoading();
}

// 3. Prefill Form with Extracted Data
function prefillForm(data) {
    // Populate supplier fields
    document.getElementById('supplierName').value = data.supplier.name;
    document.getElementById('supplierTrn').value = data.supplier.trn;
    // ... etc
    
    // Populate items table
    renderItemsTable(data.items, data.column_structure);
}

// 4. Dynamic Items Table
function renderItemsTable(items, columns) {
    // Create table with dynamic columns
    // Add/remove row buttons
    // Auto-calculate totals on change
}

// 5. Generate LPO
async function generateLPO() {
    showLoading('Generating LPO PDF...');
    
    const lpoData = collectFormData();
    
    const response = await fetch('/api/n8n/lpo-generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lpoData)
    });
    
    const blob = await response.blob();
    downloadPDF(blob, `LPO_${lpoData.lpo_number}.pdf`);
    
    hideLoading();
    showSuccessMessage('LPO generated successfully!');
}
```

---

### Step 5: Database Integration (30 min)
**Use Existing**: `models/lpo.py` (already created)

**Modifications**:
- Keep the LPO model as-is
- Add status tracking (draft, issued, acknowledged)
- Link to n8n webhook for notifications

---

### Step 6: Styling & UI Polish (30 min)

**Match Dashboard Theme**:
- Use Tailwind CSS (already in chat.html)
- Purple/blue gradient buttons (consistent with nav)
- Card-based layout with shadows
- Smooth transitions and animations
- Responsive design (mobile-friendly)

**Modal Style**:
```css
/* Backdrop blur effect */
.modal-backdrop {
    backdrop-filter: blur(5px);
    background: rgba(0, 0, 0, 0.5);
}

/* Modal content */
.modal-content {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    max-height: 90vh;
    overflow-y: auto;
}
```

---

## 🎨 Form Layout (Based on Sample LPO)

### Section 1: Header
```
┌────────────────────────────────────────┐
│ LOCAL PURCHASE ORDER                   │
│ LPO NO.: [Auto-generated]              │
│ DATE: [Today's date]                   │
│ REVISION: 00                           │
└────────────────────────────────────────┘
```

### Section 2: Supplier Details (Left) & Project Info (Right)
```
┌──────────────────────┬─────────────────────┐
│ TO:                  │ PROJECT NAME:       │
│ [Supplier Name]      │ [Project Name]      │
│ [Address]            │                     │
│ TRN: [TRN Number]    │ PROJECT LOCATION:   │
│ TEL: [Phone]         │ [Location]          │
│ CONTACT: [Person]    │                     │
└──────────────────────┴─────────────────────┘
```

### Section 3: Quote Reference
```
┌────────────────────────────────────────┐
│ QUOTATION REF.: [Quote Number]         │
│ QUOTATION DATE: [Date]                 │
└────────────────────────────────────────┘
```

### Section 4: Items Table (Dynamic Columns)
```
┌────┬──────┬──────┬────────────┬──────┬─────┬──────┬────────┐
│ ## │ MAKE │ CODE │ DESC       │ UNIT │ QTY │ RATE │ AMOUNT │
├────┼──────┼──────┼────────────┼──────┼─────┼──────┼────────┤
│ 1  │ [  ] │ [  ] │ [        ] │ [  ] │ [ ] │ [  ] │ [Auto] │
│ 2  │ [  ] │ [  ] │ [        ] │ [  ] │ [ ] │ [  ] │ [Auto] │
│ [+] Add Row                    │ [-] Remove        │        │
└────┴──────┴──────┴────────────┴──────┴─────┴──────┴────────┘
```

**Note**: Columns adapt based on `column_structure` from extraction

### Section 5: Totals
```
┌────────────────────────────────────────┐
│ SUBTOTAL:        [Auto-calculated]     │
│ VAT (5%):        [Auto-calculated]     │
│ GRAND TOTAL:     [Auto-calculated]     │
└────────────────────────────────────────┘
```

### Section 6: Terms & Conditions
```
┌────────────────────────────────────────┐
│ PAYMENT TERMS:   [Editable text]       │
│ DELIVERY TERMS:  [Editable text]       │
│ WARRANTY TERMS:  [Editable text]       │
│ OTHER TERMS:     [Editable text]       │
└────────────────────────────────────────┘
```

### Section 7: Notes
```
┌────────────────────────────────────────┐
│ NOTES:                                 │
│ [Large text area]                      │
└────────────────────────────────────────┘
```

---

## 🔄 Complete User Flow

1. **User clicks "Add New LPO"** → Modal opens
2. **User uploads quote PDF** → File sent to `/api/n8n/lpo-extract-quote`
3. **n8n processes with AI** → Extracts structured data
4. **Form auto-fills** → User reviews and edits if needed
5. **User clicks "Generate LPO"** → Data sent to `/api/n8n/lpo-generate-pdf`
6. **n8n generates PDF** → Uses template + data
7. **PDF downloads** → User receives professional LPO
8. **Database updated** → LPO saved with status "issued"

---

## 📦 Reusable Components

### 1. LPO Form Component
```javascript
class LPOForm {
    constructor(data) {
        this.data = data;
        this.items = data.items || [];
        this.columnStructure = data.column_structure || [];
    }
    
    render() { /* Render form */ }
    addItem() { /* Add row */ }
    removeItem(index) { /* Remove row */ }
    calculateTotals() { /* Auto-calculate */ }
    validate() { /* Check required fields */ }
    getData() { /* Collect all form data */ }
}
```

### 2. File Uploader Component
```javascript
class FileUploader {
    constructor(elementId, acceptedTypes) {
        this.element = document.getElementById(elementId);
        this.acceptedTypes = acceptedTypes;
        this.setupDragDrop();
    }
    
    setupDragDrop() { /* Drag & drop handling */ }
    handleUpload(file) { /* Upload to server */ }
    showProgress(percent) { /* Progress indicator */ }
}
```

### 3. Items Table Component
```javascript
class ItemsTable {
    constructor(columns, items) {
        this.columns = columns;
        this.items = items;
    }
    
    render() { /* Render dynamic table */ }
    addRow() { /* Add new item row */ }
    removeRow(index) { /* Remove item */ }
    updateCalculations() { /* Recalculate totals */ }
}
```

---

## 🧩 Modular Architecture

### Future Extensions (Easy to Add):

1. **Approval Workflow**
   - Add "Request Approval" button
   - Send to manager via n8n
   - Track approval status

2. **Email Dispatch**
   - Add "Email to Supplier" button
   - n8n sends email with PDF attachment
   - Track sent status

3. **File Storage**
   - Store PDFs in `uploads/lpos/`
   - Link to cloud storage (S3, GCS)
   - Version control

4. **Status Tracking**
   - Draft → Pending Approval → Issued → Acknowledged → Completed
   - Status badges in dashboard
   - Filter by status

5. **LPO List View**
   - Add tab in dashboard to view all LPOs
   - Search/filter functionality
   - Quick actions (view, edit, resend)

6. **Integration with POs**
   - Link LPO to Purchase Orders
   - Auto-create PO from LPO
   - Track PO vs LPO

---

## 📊 File Structure

```
templates/
  chat.html (modified)
    - Add LPO button
    - Add modal HTML
    - Add JavaScript logic

routes/
  n8n_webhooks.py (add 2 endpoints)
    - /api/n8n/lpo-extract-quote
    - /api/n8n/lpo-generate-pdf

models/
  lpo.py (keep existing)
    - LPO model
    - LPOHistory model

static/ (new)
  js/
    lpo-form.js (new)
      - LPOForm class
      - ItemsTable class
      - FileUploader class
  css/
    lpo-modal.css (new)
      - Modal styles
      - Form styles
```

---

## ✅ Implementation Checklist

### Phase 5A-Revised: UI Integration (Day 1 - 2 hours)
- [ ] Add "Add New LPO" button to chat.html
- [ ] Create modal HTML structure
- [ ] Style modal with Tailwind CSS
- [ ] Add file upload drag-drop area

### Phase 5B-Revised: n8n Integration (Day 1 - 1 hour)
- [ ] Add `/api/n8n/lpo-extract-quote` endpoint
- [ ] Add `/api/n8n/lpo-generate-pdf` endpoint
- [ ] Test with sample quote PDF
- [ ] Handle errors and edge cases

### Phase 5C-Revised: Form Logic (Day 2 - 2 hours)
- [ ] Create LPOForm JavaScript class
- [ ] Build dynamic items table
- [ ] Add add/remove row functionality
- [ ] Implement auto-calculation
- [ ] Add form validation

### Phase 5D-Revised: PDF Generation (Day 2 - 1 hour)
- [ ] Use existing lpo_template.html
- [ ] Integrate with n8n PDF service
- [ ] Test download functionality
- [ ] Add success/error messages

### Phase 5E-Revised: Testing & Polish (Day 3 - 1 hour)
- [ ] Test full workflow end-to-end
- [ ] Test with different quote formats
- [ ] Mobile responsive testing
- [ ] Cross-browser testing
- [ ] Add loading states and animations

---

## 🎯 Benefits of This Approach

1. **✅ Consistent UX**: Integrated into existing dashboard
2. **✅ n8n Power**: Leverages existing n8n AI workflows
3. **✅ Modular**: Easy to extend with approvals, email, etc.
4. **✅ Clean Code**: Reusable components
5. **✅ Fast**: Only 5-6 hours total implementation
6. **✅ Scalable**: Can handle 1000s of LPOs
7. **✅ Maintainable**: Clear separation of concerns

---

## 🚀 Let's Start!

**Next Action**: Modify `templates/chat.html` to add the LPO button and modal structure.

Ready to begin? 🎨
