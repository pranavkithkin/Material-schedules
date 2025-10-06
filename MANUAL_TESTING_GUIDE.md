# Manual Testing Guide - Basic CRUD Operations

## 🎯 Purpose

This guide helps you test all basic features of the Material Delivery Dashboard **without AI features**. Everything will be entered manually to verify the core functionality works perfectly.

---

## ✅ Pre-Testing Checklist

Before starting manual testing:

- [ ] Database is initialized (`python init_db.py`)
- [ ] Flask app starts without errors
- [ ] All migrations are applied
- [ ] No console errors in browser
- [ ] Forms load correctly

---

## 🧪 Automated Test Suite

### Run All Basic CRUD Tests

**In WSL:**
```bash
cd "/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard"
source venv/bin/activate
pytest tests/test_basic_crud_manual.py -v
```

**Or use the test runner:**
```bash
wsl bash tests/run_basic_tests.sh
```

### Test Coverage

The automated tests verify:
- ✅ All CRUD operations (Create, Read, Update, Delete)
- ✅ Data relationships between models
- ✅ Attribute consistency
- ✅ Status transitions
- ✅ Validation rules
- ✅ Complete workflow integration

---

## 📝 Manual Testing Procedures

### Test 1: Material Management

#### 1.1 Create New Material
1. Go to **Materials** page
2. Click **"Add Material"**
3. Fill in the form:
   - Material Type: `PVC Conduits & Accessories`
   - Description: `20mm PVC conduit pipes - standard grade`
   - Approval Status: `Pending`
   - Submittal Ref: `SUB-PVC-001`
   - Specification Ref: `SPEC-001`
   - Revision Number: `0` (auto-filled)
4. Click **"Save"**

**Expected Result:**
- ✅ Material appears in table
- ✅ All fields display correctly
- ✅ Status shows "Pending"
- ✅ Created by shows "Manual"

#### 1.2 Update Material Status
1. Click **Edit** on the material
2. Change Approval Status to: `Approved`
3. Add Approval Notes: `Approved for construction`
4. Set Approval Date: Today's date
5. Click **"Save"**

**Expected Result:**
- ✅ Status updates to "Approved"
- ✅ Approval date is recorded
- ✅ Notes are saved

#### 1.3 Create Material Revision
1. Click **"Add Material"**
2. Fill in same material type
3. Set Revision Number: `1`
4. Select Previous Submittal: Previous material (SUB-PVC-001)
5. Change Submittal Ref to: `SUB-PVC-001-R1`
6. Update Description: `20mm PVC conduit pipes - improved specs`
7. Click **"Save"**

**Expected Result:**
- ✅ New revision created
- ✅ Linked to previous submittal
- ✅ Revision number shows as 1

---

### Test 2: Purchase Order Management

#### 2.1 Create Purchase Order
1. Go to **Purchase Orders** page
2. Click **"Add Purchase Order"**
3. Fill in the form:
   - Material: Select `PVC Conduits & Accessories`
   - Quote Ref: `QUO-2025-001`
   - PO Ref: `PO-2025-001`
   - PO Date: Today's date
   - Expected Delivery Date: 30 days from today
   - Supplier Name: `ABC Trading LLC`
   - Supplier Contact: `+971-4-1234567`
   - Supplier Email: `supplier@abc.ae`
   - Total Amount: `50,000.00`
   - Currency: `AED`
   - PO Status: `Not Released`
   - Payment Terms: `50% advance, 50% on delivery`
   - Delivery Terms: `DDP Dubai`
   - Notes: `Urgent requirement for Phase 1`
4. Click **"Save"**

**Expected Result:**
- ✅ PO appears in table
- ✅ PO Reference is unique (error if duplicate)
- ✅ Amount displays correctly formatted
- ✅ Status shows "Not Released"
- ✅ Material name displays in table

#### 2.2 Release Purchase Order
1. Click **Edit** on the PO
2. Change PO Status to: `Released`
3. Add note: `PO released on [today's date]`
4. Click **"Save"**

**Expected Result:**
- ✅ Status updates to "Released"
- ✅ Status badge changes color
- ✅ Update timestamp is recorded

---

### Test 3: Payment Management

#### 3.1 Create Advance Payment (50%)
1. Go to **Payments** page
2. Click **"Add Payment"**
3. Fill in the form:
   - Purchase Order: Select `PO-2025-001`
   - Payment Structure: `Advance + Balance`
   - Payment Type: `Advance`
   - Total Amount: `50,000.00` (auto-filled from PO)
   - Paid Amount: `25,000.00`
   - Payment Percentage: `50` (auto-calculated)
   - Payment Date: Today's date
   - Payment Ref: `PAY-001-ADV`
   - Invoice Ref: `INV-001`
   - Payment Method: `Bank Transfer`
   - Currency: `AED`
   - Payment Status: `Completed`
   - Payment Terms: Auto-filled from PO
4. Click **"Save"**

**Expected Result:**
- ✅ Payment appears in table
- ✅ Percentage shows as 50%
- ✅ Payment terms copied from PO
- ✅ Status shows "Completed"

#### 3.2 Create Balance Payment (50%)
1. Click **"Add Payment"**
2. Fill in:
   - Purchase Order: Select `PO-2025-001`
   - Payment Structure: `Advance + Balance`
   - Payment Type: `Balance`
   - Total Amount: `50,000.00`
   - Paid Amount: `25,000.00`
   - Payment Percentage: `50`
   - Payment Date: Today's date
   - Payment Ref: `PAY-001-BAL`
   - Invoice Ref: `INV-002`
   - Payment Status: `Completed`
3. Click **"Save"**

**Expected Result:**
- ✅ Second payment created
- ✅ Total payments for PO = 100%
- ✅ Both payments visible in table

#### 3.3 Test Payment Over-Limit Warning
1. Create another payment
2. Set Paid Amount: `10,000.00` (total now exceeds PO amount)
3. Click **"Save"**

**Expected Result:**
- ✅ Payment saves successfully
- ✅ Warning message appears (if implemented)
- ⚠️ Total paid > PO amount is flagged

---

### Test 4: Delivery Management

#### 4.1 Create Pending Delivery
1. Go to **Deliveries** page
2. Click **"Add Delivery"**
3. Fill in the form:
   - Purchase Order: Select `PO-2025-001`
   - Expected Delivery Date: 30 days from today
   - Delivery Status: `Pending`
   - Delivery Percentage: `0`
   - Tracking Number: `TRK-2025-001`
   - Carrier: `Aramex`
   - Delivery Location: `Project Site - Dubai`
   - Notes: `Awaiting dispatch confirmation`
4. Click **"Save"**

**Expected Result:**
- ✅ Delivery appears in table
- ✅ Status shows "Pending"
- ✅ Progress bar shows 0%
- ✅ PO details display correctly

#### 4.2 Update to Partial Delivery (65%)
1. Click **Edit** on the delivery
2. Update fields:
   - Delivery Status: `Partial`
   - Delivery Percentage: `65`
   - Actual Delivery Date: Today's date
   - Received By: `Site Manager`
   - Notes: `65% of items received and inspected`
3. Click **"Save"**

**Expected Result:**
- ✅ Status updates to "Partial"
- ✅ Progress bar shows 65%
- ✅ Actual delivery date is recorded
- ✅ Badge color changes

#### 4.3 Complete Delivery (100%)
1. Click **Edit** on the delivery
2. Update fields:
   - Delivery Status: `Delivered`
   - Delivery Percentage: `100`
   - Actual Delivery Date: Today's date
   - Received By: `Site Manager`
   - Notes: `All items received, inspected and accepted`
3. Click **"Save"**

**Expected Result:**
- ✅ Status updates to "Delivered"
- ✅ Progress bar shows 100% (green)
- ✅ Completion date recorded

#### 4.4 Test Delayed Delivery Detection
1. Create new delivery
2. Set Expected Delivery Date: 10 days ago
3. Keep status as "Pending"
4. Click **"Save"**
5. View delivery details

**Expected Result:**
- ✅ Delivery marked as delayed
- ✅ Delay days calculated correctly
- ⚠️ Warning icon appears
- ✅ Delay reason can be added

---

## 🔄 Complete Workflow Test

### End-to-End Scenario

**Scenario:** Electrical cables project from approval to delivery

#### Step 1: Material Approval
1. Create material: `Cables & Wires - 6mm2 power cables`
2. Set status: `Approved`
3. Add submittal ref: `SUB-CABLE-001`

#### Step 2: Purchase Order
1. Create PO for the cable material
2. PO Ref: `PO-CABLE-001`
3. Supplier: `Cable Supplier LLC`
4. Amount: `100,000 AED`
5. Payment terms: `50% advance, 50% on delivery`
6. Expected delivery: 60 days
7. Release PO

#### Step 3: Advance Payment
1. Create payment: Advance 50% = 50,000 AED
2. Payment ref: `PAY-CABLE-001-ADV`
3. Status: Completed

#### Step 4: Delivery Tracking
1. Create delivery: Status = Pending
2. Update after 30 days: Partial 70%
3. Create balance payment: 50% = 50,000 AED
4. Final update: Delivered 100%

#### Verification Checklist:
- [ ] Material links to PO
- [ ] PO shows 2 payments (total 100%)
- [ ] PO shows 1 delivery (100% complete)
- [ ] All dates are logical and sequential
- [ ] All amounts add up correctly
- [ ] No orphaned records
- [ ] All relationships intact

---

## 🐛 Common Issues to Check

### Database Issues
- [ ] No foreign key constraint errors
- [ ] Relationships load correctly
- [ ] Cascade deletes work properly
- [ ] Unique constraints enforced (PO ref, etc.)

### Form Issues
- [ ] All form fields match model attributes
- [ ] Dropdown values populate correctly
- [ ] Date pickers work properly
- [ ] Required fields are validated
- [ ] Error messages display clearly

### Display Issues
- [ ] Tables show all columns correctly
- [ ] Nested data displays (PO info in delivery table)
- [ ] Progress bars render correctly
- [ ] Status badges show correct colors
- [ ] Dates format properly

### Calculation Issues
- [ ] Payment percentages calculate correctly
- [ ] Delivery percentages display accurately
- [ ] Delay days compute properly
- [ ] Over-limit payments are flagged
- [ ] Totals add up correctly

---

## ✅ Acceptance Criteria

**All tests must pass before implementing AI features:**

### Materials
- [x] Create, read, update, delete works
- [x] Approval workflow functions
- [x] Revision tracking works
- [x] All attributes display correctly

### Purchase Orders
- [x] Create with all fields works
- [x] PO reference uniqueness enforced
- [x] Status transitions work
- [x] Material relationship intact
- [x] Release workflow functions

### Payments
- [x] Single payment creation works
- [x] Advance + Balance structure works
- [x] Percentages calculate correctly
- [x] Payment terms copy from PO
- [x] Over-limit detection works

### Deliveries
- [x] Pending → Partial → Delivered workflow
- [x] Percentage tracking works
- [x] Delay detection accurate
- [x] Progress bars display correctly
- [x] PO relationship intact

### Integration
- [x] Complete workflow works end-to-end
- [x] All relationships maintain integrity
- [x] No orphaned records
- [x] Cascade operations work
- [x] Data consistency maintained

---

## 📊 Test Results Template

```
Date: __________
Tester: __________

MATERIALS:
  Create:     [ ] Pass  [ ] Fail  Notes: __________
  Read:       [ ] Pass  [ ] Fail  Notes: __________
  Update:     [ ] Pass  [ ] Fail  Notes: __________
  Delete:     [ ] Pass  [ ] Fail  Notes: __________
  Revisions:  [ ] Pass  [ ] Fail  Notes: __________

PURCHASE ORDERS:
  Create:     [ ] Pass  [ ] Fail  Notes: __________
  Read:       [ ] Pass  [ ] Fail  Notes: __________
  Update:     [ ] Pass  [ ] Fail  Notes: __________
  Release:    [ ] Pass  [ ] Fail  Notes: __________
  Uniqueness: [ ] Pass  [ ] Fail  Notes: __________

PAYMENTS:
  Single:     [ ] Pass  [ ] Fail  Notes: __________
  Advance:    [ ] Pass  [ ] Fail  Notes: __________
  Balance:    [ ] Pass  [ ] Fail  Notes: __________
  Over-limit: [ ] Pass  [ ] Fail  Notes: __________
  
DELIVERIES:
  Pending:    [ ] Pass  [ ] Fail  Notes: __________
  Partial:    [ ] Pass  [ ] Fail  Notes: __________
  Delivered:  [ ] Pass  [ ] Fail  Notes: __________
  Delays:     [ ] Pass  [ ] Fail  Notes: __________

INTEGRATION:
  Workflow:   [ ] Pass  [ ] Fail  Notes: __________
  Relations:  [ ] Pass  [ ] Fail  Notes: __________

OVERALL STATUS: [ ] APPROVED  [ ] NEEDS FIXES
```

---

## 🚀 Next Steps

**After all tests pass:**

1. Document any issues found
2. Fix all bugs and errors
3. Re-run automated tests
4. Perform manual re-verification
5. Get approval for production use
6. Then implement AI features (Phase 3+)

---

**Remember:** Manual entry MUST be 100% reliable before adding AI automation!
