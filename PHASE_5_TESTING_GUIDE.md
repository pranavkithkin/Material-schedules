# Phase 5 Step 5.4: Integration & Testing Guide

## 🎯 Goal
Test the complete LPO system end-to-end with mock data

**Time**: ~30 minutes  
**Status**: Testing Phase  
**Mock Data**: Yes (AI extraction simulated)

---

## ✅ Pre-Test Checklist

Before starting tests:
- [ ] Flask server running on http://localhost:5001
- [ ] Database exists (delivery_dashboard.db)
- [ ] Browser open (Chrome/Edge recommended)
- [ ] Sample file ready (any PDF, DOCX, or XLSX)

---

## 🧪 Test Suite

### Test 1: Navigate to LPO Page ✓
**Goal**: Verify LPO page loads correctly

**Steps**:
1. Open browser: http://localhost:5001/
2. Look bottom-right corner
3. Verify you see two floating buttons:
   - Green (+) button above
   - Blue (💬) chat button below

**Expected**:
- ✅ Both buttons visible
- ✅ Green button shows "Create New LPO" tooltip on hover
- ✅ Buttons have shadows and animations

**Alternative**:
- Navigate directly to: http://localhost:5001/lpo
- Should see LPO list page

---

### Test 2: LPO Page Layout ✓
**Goal**: Verify page matches PKP branding

**Steps**:
1. Visit: http://localhost:5001/lpo
2. Check page header
3. Check filter bar
4. Check table

**Expected**:
- ✅ Header: "Local Purchase Orders (LPO)" with green icon
- ✅ Green button: "Create New LPO"
- ✅ Filter bar: Status dropdown + Search box + Refresh button
- ✅ Table with columns: LPO Number, Supplier, Project, Status, Total Amount, Date, Actions
- ✅ Initially shows: "Loading LPOs..." or "No LPOs found"

**Screenshot**: Take screenshot for documentation

---

### Test 3: Open Create LPO Modal ✓
**Goal**: Verify modal opens correctly

**Steps**:
1. On /lpo page, click "Create New LPO" button (green)
2. Modal should open

**Expected**:
- ✅ Modal appears (full screen overlay)
- ✅ Modal header: "Create New LPO" with icon
- ✅ Close button (X) in top-right
- ✅ Step 1 visible: Upload section
- ✅ Blue info box: "Upload a supplier quotation to auto-extract details"
- ✅ Drag-drop area visible
- ✅ "Browse Files" button present

---

### Test 4: File Upload Validation ✓
**Goal**: Test file type and size validation

**Test 4a - Valid File**:
1. Click "Browse Files" or drag a PDF file
2. Select any PDF file (< 20MB)

**Expected**:
- ✅ File appears in preview section
- ✅ Shows filename and size
- ✅ "Extract Data with AI" button becomes enabled (green)
- ✅ Close (X) button appears next to filename

**Test 4b - Invalid File Type**:
1. Try to upload a .txt or .jpg file
2. Should see alert: "Invalid file type..."

**Expected**:
- ✅ Alert shown
- ✅ File not accepted
- ✅ Extract button stays disabled

**Test 4c - Large File**:
1. If you have a file > 20MB, try uploading
2. Should see alert: "File size exceeds 20MB limit"

**Expected**:
- ✅ Alert shown
- ✅ File not accepted

**Test 4d - Clear File**:
1. Upload a valid file
2. Click X button to clear
3. File should be removed

**Expected**:
- ✅ File preview disappears
- ✅ Extract button becomes disabled
- ✅ Can upload again

---

### Test 5: Extract Quote Data (Mock) ✓
**Goal**: Test AI extraction with mock data

**Steps**:
1. Upload any PDF file
2. Click "Extract Data with AI" button
3. Wait for extraction

**Expected**:
- ✅ Upload section disappears
- ✅ Loading section appears with:
  - Spinning robot icon
  - "Extracting Data..." message
  - "AI is analyzing the quotation"
  - "This may take 10-30 seconds"
- ✅ After ~2 seconds, loading disappears
- ✅ Form section appears with:
  - Green success box: "Data extracted successfully!"
  - Complete form with sections

---

### Test 6: Review Extracted Data ✓
**Goal**: Verify form renders with mock data

**After extraction, check form has**:

**Supplier Information Section**:
- ✅ Supplier Name: "ABC Steel Trading LLC"
- ✅ TRN: "100123456700003"
- ✅ Address: "Industrial Area 3, Sharjah, UAE"
- ✅ Telephone: "+971-6-1234567"
- ✅ Contact Person: "Mohammed Ahmed"

**Project & Quote Details Section**:
- ✅ Project Name: "Villa Construction - Al Barsha"
- ✅ Project Location: (empty or filled)
- ✅ Quote Reference: "QT-2025-001"
- ✅ Quote Date: "2025-10-05"

**Items Table**:
- ✅ Columns: #, MAKE, CODE, DESCRIPTION, UNIT, QTY, RATE, AMOUNT, [Delete]
- ✅ 3 rows of steel items pre-filled
- ✅ Item 1: Tata Steel, TMT-16, TMT Steel Bar 16mm, Ton, 5, 2800, 14000
- ✅ Item 2: Similar format
- ✅ Item 3: Similar format
- ✅ "Add Item" button (green) visible

**Totals Section**:
- ✅ Subtotal: Should show calculated total
- ✅ VAT (5%): Should show 5% of subtotal
- ✅ Grand Total: Subtotal + VAT (in green, bold)

**Terms & Conditions Section**:
- ✅ Payment Terms: "30 days from delivery"
- ✅ Delivery Terms: "Within 7 days from PO"
- ✅ Additional Notes: (empty textarea)

**Action Buttons**:
- ✅ "Save Draft" button (gray)
- ✅ "Generate LPO PDF" button (green)

---

### Test 7: Edit Form Data ✓
**Goal**: Test form editing and calculations

**Test 7a - Edit Quantity**:
1. Click on QTY field of first item
2. Change from 5 to 10
3. Tab out or click elsewhere

**Expected**:
- ✅ Amount recalculates: 10 × 2800 = 28000
- ✅ Subtotal updates
- ✅ VAT updates (5% of new subtotal)
- ✅ Grand Total updates

**Test 7b - Edit Rate**:
1. Change RATE from 2800 to 3000
2. Tab out

**Expected**:
- ✅ Amount recalculates: 10 × 3000 = 30000
- ✅ All totals update

**Test 7c - Edit Supplier**:
1. Change Supplier Name to "Test Supplier LLC"
2. Change TRN to "999888777"

**Expected**:
- ✅ Values update in fields
- ✅ No errors

---

### Test 8: Add/Remove Items ✓
**Goal**: Test dynamic table operations

**Test 8a - Add Item**:
1. Click "Add Item" button (green)
2. New row should appear

**Expected**:
- ✅ Row 4 appears
- ✅ Number automatically set to 4
- ✅ All fields empty
- ✅ Amount shows 0.00
- ✅ Delete button present

**Test 8b - Fill New Item**:
1. Fill in: Description="Test Item", Unit="Pcs", QTY=100, RATE=50
2. Tab out

**Expected**:
- ✅ Amount calculates: 100 × 50 = 5000
- ✅ Totals update to include new item

**Test 8c - Delete Item**:
1. Click delete (trash) icon on row 4
2. Row should be removed

**Expected**:
- ✅ Row 4 disappears
- ✅ Row numbers update (1, 2, 3)
- ✅ Totals recalculate without deleted item

**Test 8d - Delete All But One**:
1. Delete items until only 1 remains
2. Should still work

**Expected**:
- ✅ Can delete
- ✅ At least 1 item must remain for generation

---

### Test 9: Form Validation ✓
**Goal**: Test required field validation

**Test 9a - Empty Supplier Name**:
1. Clear the Supplier Name field
2. Click "Generate LPO PDF"

**Expected**:
- ✅ Alert appears: "Please fix the following errors:"
- ✅ Error message: "Supplier name is required"
- ✅ PDF not generated

**Test 9b - Empty Project Name**:
1. Fill Supplier Name back
2. Clear Project Name
3. Click "Generate LPO PDF"

**Expected**:
- ✅ Alert with: "Project name is required"

**Test 9c - No Items**:
1. Delete all items
2. Click "Generate LPO PDF"

**Expected**:
- ✅ Alert with: "At least one item is required"

**Test 9d - Valid Form**:
1. Ensure all required fields filled
2. At least 1 item with description
3. Click "Generate LPO PDF"

**Expected**:
- ✅ No validation errors
- ✅ Proceeds to PDF generation

---

### Test 10: Generate LPO PDF ✓
**Goal**: Test PDF generation and download

**Steps**:
1. Ensure form is valid (from Test 9d)
2. Click "Generate LPO PDF" button
3. Wait for generation

**Expected During Generation**:
- ✅ Button disabled
- ✅ Button text changes to: "🔄 Generating..."
- ✅ Spinning icon visible

**Expected After Success**:
- ✅ Success alert appears:
  ```
  ✅ LPO Generated Successfully!
  
  LPO Number: LPO/PKP/2025/0001
  Grand Total: [amount] AED
  
  Downloading PDF...
  ```
- ✅ PDF download starts automatically
- ✅ Modal closes after 1 second
- ✅ Returns to LPO list page

**Verify PDF**:
1. Check Downloads folder
2. Open PDF file: `LPO_PKP_2025_0001.pdf`
3. Check contents

**Expected in PDF**:
- ✅ PKP Contracting LLC header
- ✅ LPO number: LPO/PKP/2025/0001
- ✅ Date: Today's date
- ✅ Supplier details (as entered)
- ✅ Project details (as entered)
- ✅ Items table with all rows
- ✅ Calculated amounts correct
- ✅ Totals section (Subtotal, VAT 5%, Grand Total)
- ✅ Terms & conditions (if entered)
- ✅ Professional formatting

---

### Test 11: LPO List View ✓
**Goal**: Verify LPO appears in list

**Steps**:
1. After PDF generation, should be on /lpo page
2. Click "Refresh" button if needed
3. Check table

**Expected**:
- ✅ Table shows 1 row
- ✅ LPO Number: LPO/PKP/2025/0001
- ✅ Supplier: Test Supplier LLC (or whatever you entered)
- ✅ Project: Your project name
- ✅ Status: Green badge "ISSUED"
- ✅ Total Amount: Correct amount (grand total)
- ✅ Date: Today's date
- ✅ Actions: Download, View, (no Edit for issued)

---

### Test 12: Download Existing LPO ✓
**Goal**: Test download from list

**Steps**:
1. In LPO list, find the LPO you just created
2. Click the download icon (blue)

**Expected**:
- ✅ PDF downloads again
- ✅ Same file as before
- ✅ Can open and view

---

### Test 13: Filter & Search ✓
**Goal**: Test list filtering

**Test 13a - Filter by Status**:
1. Click status dropdown
2. Select "Issued"

**Expected**:
- ✅ Shows only issued LPOs (should see your LPO)

**Test 13b - Search**:
1. Type supplier name in search box
2. Click refresh or wait

**Expected**:
- ✅ Shows only matching LPOs
- ✅ Filters by supplier name, project name, or LPO number

**Test 13c - Clear Filters**:
1. Select "All Status"
2. Clear search box
3. Click refresh

**Expected**:
- ✅ Shows all LPOs again

---

### Test 14: Create Second LPO ✓
**Goal**: Test LPO number auto-increment

**Steps**:
1. Click "Create New LPO" again
2. Upload file
3. Extract data
4. Edit form (change supplier/project)
5. Generate PDF

**Expected**:
- ✅ New LPO number: LPO/PKP/2025/0002
- ✅ Sequential numbering
- ✅ Both LPOs visible in list
- ✅ No conflicts

---

### Test 15: Responsive Design ✓
**Goal**: Test mobile view

**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar (mobile view)
3. Select iPhone or iPad view
4. Navigate to /lpo page

**Expected**:
- ✅ Page layout adjusts
- ✅ Table scrolls horizontally if needed
- ✅ Floating buttons visible
- ✅ Modal works on mobile
- ✅ Form is usable

---

### Test 16: Floating Buttons ✓
**Goal**: Test floating action buttons

**Test 16a - LPO Button**:
1. From Dashboard (http://localhost:5001/)
2. Look bottom-right
3. Hover over green (+) button

**Expected**:
- ✅ Tooltip shows: "Create New LPO"
- ✅ Button hover effect (gold color)
- ✅ Icon rotates 90°
- ✅ Click goes to /lpo page

**Test 16b - Chat Button**:
1. Click blue (💬) button

**Expected**:
- ✅ Chat popup opens
- ✅ AI Assistant interface visible
- ✅ Can type and interact
- ✅ Close with X or ESC
- ✅ Returns to same page

---

### Test 17: Database Verification ✓
**Goal**: Check data persisted correctly

**Steps** (Optional - for advanced users):
1. Open terminal/command prompt
2. Navigate to project folder
3. Run: `sqlite3 delivery_dashboard.db`
4. Run: `SELECT * FROM lpo;`

**Expected**:
- ✅ Shows LPO records
- ✅ Correct data stored
- ✅ LPO numbers sequential
- ✅ JSON data for items/columns

**Alternative** (Python):
```python
from app import create_app
from models.lpo import LPO

app = create_app()
with app.app_context():
    lpos = LPO.query.all()
    print(f"Total LPOs: {len(lpos)}")
    for lpo in lpos:
        print(f"{lpo.lpo_number} - {lpo.supplier_name} - {lpo.total_amount} AED")
```

---

### Test 18: Error Handling ✓
**Goal**: Test graceful error handling

**Test 18a - Network Error Simulation**:
1. Stop Flask server
2. Try to create LPO
3. Should see error

**Expected**:
- ✅ User-friendly error message
- ✅ No page crash
- ✅ Can retry after restarting server

**Test 18b - Invalid Data**:
1. Try to enter negative quantity
2. Try to enter letters in rate field

**Expected**:
- ✅ HTML5 validation prevents
- ✅ Or graceful error

---

### Test 19: Browser Compatibility ✓
**Goal**: Test in multiple browsers

**Browsers to Test**:
- [x] Chrome/Edge (Chromium)
- [ ] Firefox (if available)
- [ ] Safari (if on Mac)

**Expected**:
- ✅ Works in all browsers
- ✅ Same functionality
- ✅ Consistent appearance

---

### Test 20: Performance ✓
**Goal**: Check system performance

**Observations**:
- [ ] Page load time: < 2 seconds
- [ ] Modal open: Instant
- [ ] File upload: < 1 second
- [ ] Extraction (mock): ~2 seconds
- [ ] PDF generation: < 5 seconds
- [ ] Table render: < 1 second

**Expected**:
- ✅ Fast and responsive
- ✅ No lag or freezing
- ✅ Smooth animations

---

## 📊 Test Results Summary

### Total Tests: 20
- [ ] Test 1: Navigate to LPO Page
- [ ] Test 2: LPO Page Layout
- [ ] Test 3: Open Create LPO Modal
- [ ] Test 4: File Upload Validation
- [ ] Test 5: Extract Quote Data
- [ ] Test 6: Review Extracted Data
- [ ] Test 7: Edit Form Data
- [ ] Test 8: Add/Remove Items
- [ ] Test 9: Form Validation
- [ ] Test 10: Generate LPO PDF
- [ ] Test 11: LPO List View
- [ ] Test 12: Download Existing LPO
- [ ] Test 13: Filter & Search
- [ ] Test 14: Create Second LPO
- [ ] Test 15: Responsive Design
- [ ] Test 16: Floating Buttons
- [ ] Test 17: Database Verification
- [ ] Test 18: Error Handling
- [ ] Test 19: Browser Compatibility
- [ ] Test 20: Performance

---

## 🐛 Bug Tracking

### Issues Found:
| # | Issue | Severity | Status | Notes |
|---|-------|----------|--------|-------|
| 1 | | | | |
| 2 | | | | |

### Severity Levels:
- 🔴 **Critical**: Blocks main functionality
- 🟡 **Major**: Impacts user experience
- 🟢 **Minor**: Cosmetic or edge case

---

## ✅ Sign-Off

### Test Completion:
- **Date**: October 9, 2025
- **Tester**: 
- **Tests Passed**: ___ / 20
- **Tests Failed**: ___ / 20
- **Critical Bugs**: ___
- **Status**: ⬜ PASS / ⬜ FAIL / ⬜ WITH ISSUES

### Notes:
```
[Add any additional observations or comments here]
```

---

## 🎯 Next Steps After Testing

### If All Tests Pass ✅:
1. Mark Phase 5 as COMPLETE (100%)
2. Commit code to Git
3. Push to repository
4. Move to Phase 5B (n8n workflow) or Phase 6

### If Issues Found 🐛:
1. Document all bugs in table above
2. Prioritize by severity
3. Fix critical bugs first
4. Retest after fixes
5. Repeat until all pass

---

## 📸 Screenshots to Capture

For documentation:
1. [ ] LPO list page (empty)
2. [ ] Create LPO modal (upload section)
3. [ ] Loading section during extraction
4. [ ] Form with extracted data
5. [ ] Success message
6. [ ] Generated PDF sample
7. [ ] LPO list with data
8. [ ] Mobile responsive view
9. [ ] Floating buttons
10. [ ] Chat popup

---

**Ready to start testing!** 🚀

Run through each test systematically and check off as you go.
