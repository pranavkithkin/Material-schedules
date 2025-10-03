# 🧪 SYSTEM TESTING CHECKLIST
## Material Delivery Dashboard - October 3, 2025

---

## ✅ PRE-TESTING SETUP

- [x] Database initialized with sample data
- [x] Flask server running on http://127.0.0.1:5000
- [x] Browser opened to dashboard

---

## 📊 DASHBOARD PAGE (Home)

**URL:** http://127.0.0.1:5000

### Visual Checks:
- [ ] PKP green navigation bar (#006837)
- [ ] Gold accents on navigation hover
- [ ] Company branding visible
- [ ] Statistics cards display correctly
- [ ] Quick Actions buttons visible (green with gold hover)

### Functional Tests:
- [ ] Statistics show correct counts:
  - Total Materials
  - Pending Approvals
  - Active Purchase Orders
  - Pending AI Suggestions
- [ ] Material Status Distribution chart displays
- [ ] Recent Activities table shows data
- [ ] Quick Action buttons link to correct pages

### Expected Sample Data:
- **Total Materials:** 5
- **Purchase Orders:** 2
- **Payments:** 2
- **Deliveries:** 2
- **AI Suggestions:** 1

---

## 🔨 MATERIALS PAGE

**URL:** http://127.0.0.1:5000/materials

### Visual Checks:
- [ ] Page header is PKP green with gold icon
- [ ] Add Material button is green (hover turns gold)
- [ ] Filter card has gold left border
- [ ] Table displays properly
- [ ] Status badges are color-coded

### Functional Tests:

#### 1. View Materials
- [ ] See 5 sample materials in table
- [ ] Search box works (type "PVC" or "Steel")
- [ ] Filter by status works
- [ ] Pagination works (if applicable)

#### 2. Add New Material
- [ ] Click "Add Material" button
- [ ] Modal opens
- [ ] Fill in details:
  - Material Type: (select from dropdown - 35 options)
  - Description: "Test material for demo"
  - Quantity: 100
  - Unit: pieces
  - Approval Status: Pending
- [ ] Click Save
- [ ] Success notification appears
- [ ] New material appears in table

#### 3. Edit Material
- [ ] Click edit icon on any material
- [ ] Modal opens with prefilled data
- [ ] Change description
- [ ] Click Save
- [ ] Changes reflect in table

#### 4. Delete Material
- [ ] Click delete icon
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] Material removed from table

#### 5. View Material Details
- [ ] Click on material name/row
- [ ] Detail view shows complete information
- [ ] Related POs displayed (if any)

---

## 📝 PURCHASE ORDERS PAGE

**URL:** http://127.0.0.1:5000/purchase_orders

### Visual Checks:
- [ ] PKP branding applied
- [ ] Add PO button visible
- [ ] Filter card with gold border
- [ ] Table displays 2 sample POs

### Functional Tests:

#### 1. View Purchase Orders
- [ ] See 2 sample POs
- [ ] PO numbers visible
- [ ] Supplier names shown
- [ ] Amounts displayed correctly
- [ ] Status badges color-coded

#### 2. Add New Purchase Order
- [ ] Click "Add Purchase Order"
- [ ] Modal opens
- [ ] Fill in:
  - PO Number: PO-TEST-001
  - Material: (select from dropdown)
  - Supplier Name: Test Supplier LLC
  - Supplier Contact: test@supplier.com
  - Total Amount: 25000
  - Expected Delivery: (pick future date)
  - PO Date: (today's date)
  - Status: Released
- [ ] Click Save
- [ ] PO appears in table

#### 3. Edit Purchase Order
- [ ] Click edit on existing PO
- [ ] Change status to "Delivered"
- [ ] Update amount
- [ ] Save changes
- [ ] Verify updates

#### 4. Link to Material
- [ ] PO should show linked material
- [ ] Click material link
- [ ] Should navigate to material details

---

## 💰 PAYMENTS PAGE

**URL:** http://127.0.0.1:5000/payments

### Visual Checks:
- [ ] PKP green header with gold credit card icon
- [ ] Summary cards show payment stats
- [ ] Gold left border on summary cards
- [ ] Payment structure badges visible

### Functional Tests:

#### 1. View Payments
- [ ] See 2 sample payments
- [ ] Payment types shown (Single/Advance/Balance)
- [ ] Percentages calculated correctly
- [ ] Amounts displayed

#### 2. Add Single Payment
- [ ] Click "Add Payment"
- [ ] Select Payment Structure: Single Payment
- [ ] Fill in:
  - Purchase Order: (select from dropdown)
  - Amount: 50000
  - Payment Date: (today)
  - Payment Method: Bank Transfer
  - Reference: TEST-REF-001
- [ ] Click Save
- [ ] Payment appears

#### 3. Add Advance Payment
- [ ] Click "Add Payment"
- [ ] Select: Advance Payment
- [ ] Amount: 20000
- [ ] Percentage: 40%
- [ ] Save and verify

#### 4. Add Balance Payment
- [ ] Must have existing advance payment
- [ ] Select: Balance Payment
- [ ] Link to advance payment
- [ ] Enter remaining amount
- [ ] Save and verify

#### 5. Payment Summary Cards
- [ ] Total Payments card shows sum
- [ ] Percentage calculations correct
- [ ] Status indicators accurate

---

## 🚚 DELIVERIES PAGE

**URL:** http://127.0.0.1:5000/deliveries

### Visual Checks:
- [ ] PKP green header with gold truck icon
- [ ] Filter card with gold border
- [ ] Delay indicators visible (red for delayed)
- [ ] Status badges color-coded

### Functional Tests:

#### 1. View Deliveries
- [ ] See 2 sample deliveries
- [ ] Expected dates shown
- [ ] Actual dates shown (if delivered)
- [ ] Delay calculation correct

#### 2. Add New Delivery
- [ ] Click "Add Delivery"
- [ ] Fill in:
  - Purchase Order: (select)
  - Delivery Note Number: DN-TEST-001
  - Expected Date: (pick date)
  - Delivery Status: In Transit
  - Quantity Delivered: 50
- [ ] Click Save
- [ ] Delivery appears

#### 3. Mark as Delivered
- [ ] Edit existing delivery
- [ ] Change status to "Delivered"
- [ ] Set Actual Delivery Date: (today)
- [ ] Save
- [ ] Verify status updated

#### 4. Check Delay Detection
- [ ] Find delivery with expected date in past
- [ ] Should show "Delayed" indicator
- [ ] Days delayed calculated correctly
- [ ] Red color indicator visible

---

## 🤖 AI SUGGESTIONS PAGE

**URL:** http://127.0.0.1:5000/ai_suggestions

### Visual Checks:
- [ ] PKP green header with gold robot icon
- [ ] Info banner with green border
- [ ] Refresh button (green → gold on hover)
- [ ] Suggestion cards visible

### Functional Tests:

#### 1. View AI Suggestions
- [ ] See 1 sample AI suggestion
- [ ] Confidence score displayed (0-100%)
- [ ] Suggested data shown
- [ ] AI reasoning visible
- [ ] Source indicated

#### 2. Approve Suggestion
- [ ] Click "Approve" on suggestion
- [ ] Confirmation dialog appears
- [ ] Confirm approval
- [ ] Suggestion marked as approved
- [ ] Data auto-applied to system

#### 3. Reject Suggestion
- [ ] Create another AI suggestion (if needed)
- [ ] Click "Reject"
- [ ] Confirmation dialog
- [ ] Confirm rejection
- [ ] Suggestion marked as rejected

#### 4. Confidence Level Filtering
- [ ] Should show confidence badge
- [ ] High (≥90%): Green badge
- [ ] Medium (60-89%): Yellow badge
- [ ] Low (<60%): Red badge

---

## 💬 CHAT INTERFACE

**Located:** Floating button on all pages (bottom-right corner)

### Visual Checks:
- [ ] Chat button visible (PKP green)
- [ ] Hover turns button gold
- [ ] AI badge shows "AI"

### Functional Tests:

**Note:** Chat requires API keys to work. If not configured, you'll see an error message.

#### If API Keys Configured:
- [ ] Click chat button
- [ ] Chat panel slides up
- [ ] Type: "Show me all materials"
- [ ] AI responds with material list
- [ ] Type: "What's the status of PO-12345?"
- [ ] AI provides PO details
- [ ] Type: "Which deliveries are delayed?"
- [ ] AI lists delayed deliveries

#### If API Keys NOT Configured:
- [ ] Click chat button
- [ ] See message: "AI features require API keys"
- [ ] Instructions shown for setup

---

## 🔍 API ENDPOINTS TEST

### Using Browser or Postman

#### 1. Get All Materials
```
GET http://127.0.0.1:5000/api/materials
Expected: JSON array of 5 materials
```

#### 2. Get Dashboard Stats
```
GET http://127.0.0.1:5000/api/dashboard/stats
Expected: JSON with counts and statistics
```

#### 3. Get Single Purchase Order
```
GET http://127.0.0.1:5000/api/purchase_orders/1
Expected: JSON object with PO details
```

#### 4. Get Material Types
```
GET http://127.0.0.1:5000/api/materials/types
Expected: JSON array of 35 material types
```

---

## 🎨 PKP BRANDING VERIFICATION

### Color Checks:
- [ ] Navigation bar: #006837 (PKP green)
- [ ] Hover effects: #D4AF37 (PKP gold)
- [ ] Background: #E5E5E5 (PKP gray)
- [ ] Consistent across all pages

### Design Elements:
- [ ] All page headers use PKP green
- [ ] All icons use PKP gold
- [ ] All primary buttons: green → gold on hover
- [ ] Border accents use gold (left border on cards)
- [ ] Status badges include border colors
- [ ] Loading spinner uses PKP green

---

## ⚡ PERFORMANCE TESTS

### Page Load Times:
- [ ] Dashboard loads in < 2 seconds
- [ ] All pages load quickly
- [ ] No JavaScript errors in console (F12)
- [ ] Images/icons load properly

### Responsiveness:
- [ ] Test on different window sizes
- [ ] Mobile view works (resize browser)
- [ ] Tables scroll on small screens
- [ ] Modals display correctly

---

## 🐛 ERROR HANDLING

### Test Invalid Operations:
- [ ] Try to delete material with linked POs (should warn)
- [ ] Submit form with missing required fields (should validate)
- [ ] Enter invalid date (should reject)
- [ ] Enter negative numbers (should reject)

---

## 📱 CROSS-BROWSER TEST (Optional)

If time permits, test in:
- [ ] Chrome/Edge (primary)
- [ ] Firefox
- [ ] Safari (if on Mac)

---

## ✅ FINAL CHECKS

### Data Integrity:
- [ ] All sample data displays correctly
- [ ] Relationships work (PO → Material → Payment → Delivery)
- [ ] Counts match (5 materials, 2 POs, etc.)

### Navigation:
- [ ] All menu links work
- [ ] Breadcrumbs/back buttons functional
- [ ] Quick actions navigate correctly

### User Experience:
- [ ] Forms are intuitive
- [ ] Success/error messages clear
- [ ] Loading indicators show during operations
- [ ] Modal close buttons work

---

## 📝 ISSUES FOUND

### Critical Issues:
```
(List any broken features or errors)
Example: "Chat button not working without API keys"
```

### Minor Issues:
```
(List UI glitches or improvements needed)
Example: "Table sort not working on Deliveries page"
```

### Enhancement Ideas:
```
(List ideas for improvements)
Example: "Add export to Excel button"
```

---

## 🎯 TEST SUMMARY

**Date Tested:** October 3, 2025  
**Tested By:** _______________  
**Overall Status:** ⬜ Pass / ⬜ Pass with Issues / ⬜ Fail

**Total Tests:** 100+  
**Passed:** _____  
**Failed:** _____  
**Skipped:** _____  

**Ready for AI Agent Development?** ⬜ Yes / ⬜ No (fix issues first)

---

## 🚀 NEXT STEPS AFTER TESTING

If all tests pass:
1. ✅ Mark this testing as complete
2. ✅ Commit any bug fixes to Git
3. ✅ Proceed with Phase 1B: AI Agent System
4. ✅ Start implementing:
   - `services/ai_agent.py`
   - `models/conversation.py`
   - `routes/ai_agent.py`
   - `templates/document_upload.html`

**Ready to build the AI Agent!** 🤖
