# Field Structure Update - October 4, 2025

## Overview
This document outlines the field structure changes made to simplify tracking and align with real-world PO management where one PO contains multiple items with different units.

## Problem Statement
- **PO Reality**: One PO can contain 50+ different items (e.g., sanitary wares: shower heads, mixers, WCs, shattafs)
- **Unit Complexity**: Each item may have different units (pieces, sets, meters, etc.)
- **Tracking Level**: We track at PO level (outer envelope), not individual item level
- **Document Proof**: Actual delivery proof comes from uploaded Delivery Order documents

## Changes Made

### 1. Payment Model (`models/payment.py`)

**Fields ADDED:**
```python
payment_terms = db.Column(db.Text)  # Copied from PO for reference and reminders
```

**Fields REMOVED:**
- `quantity` - Not applicable to payments
- `unit` - Not applicable to payments

**Status Values Updated:**
- Old: Pending, Completed, Partial
- New: Pending, Full, Partial

**Tracking Logic:**
- Payment status: Full (100% paid) or Partial (< 100% paid)
- Payment reminder: If partial payment + balance due before delivery date → remind user
- Payment terms: Fetched from PO.payment_terms field
- Over-limit validation: Already implemented (prevents paying more than PO amount)

**Use Case:**
```
PO-2025-001: AED 15,000
Payment Terms: "30% advance, 70% before delivery"
Delivery Date: Nov 15, 2025

Payment 1: AED 4,500 (30%) - Status: Partial
→ System reminds: "Balance AED 10,500 due before Nov 15"

Payment 2: AED 10,500 (70%) - Status: Full
→ System confirms: "PO fully paid"
```

---

### 2. Material Model (`models/material.py`)

**Fields ADDED:**
```python
revision_number = db.Column(db.Integer, default=0)  # Track submittal revisions
previous_submittal_id = db.Column(db.Integer, db.ForeignKey('materials.id'))  # Link to previous revision
document_path = db.Column(db.String(500))  # Submittal document upload
```

**Fields REMOVED:**
- `quantity` - Tracked at PO level, not material type level
- `unit` - Tracked at PO level, not material type level

**Relationships ADDED:**
```python
revisions = db.relationship('Material', backref=db.backref('previous_submittal', remote_side=[id]))
```

**Revision Tracking:**
Most materials have single submittal, some have multiple revisions. The system keeps complete revision history:

```
Material: "Kohler Shower Mixer - Model XYZ"

Submittal Rev 0 (Initial)
├─ Status: Revise & Resubmit
├─ Document: submittal_shower_mixer_rev0.pdf
└─ Date: Oct 1, 2025

Submittal Rev 1 (Revised)
├─ Status: Approved as Noted
├─ Document: submittal_shower_mixer_rev1.pdf
├─ Previous: Rev 0
└─ Date: Oct 10, 2025

Submittal Rev 2 (Final)
├─ Status: Approved
├─ Document: submittal_shower_mixer_rev2.pdf
├─ Previous: Rev 1
└─ Date: Oct 15, 2025
```

**Use Case:**
- User submits material approval for "Sanitary Wares" (covers 50+ items)
- If rejected: Create new record with revision_number = 1, link to previous
- Keep full history of all revisions
- Final approved submittal covers all materials in that category

---

### 3. Delivery Model (`models/delivery.py`)

**Fields ADDED:**
```python
delivery_percentage = db.Column(db.Float, default=0)  # For partial deliveries (e.g., 65%)
```

**Fields REMOVED:**
- `ordered_quantity` - Not tracked (PO has multiple items)
- `delivered_quantity` - Not tracked (proof is in Delivery Order document)
- `unit` - Not tracked (multiple units per PO)

**Status Values Updated:**
- Old: Pending, In Transit, Partial Delivery, Completed, Delayed
- New: **Pending**, **Partial**, **Delivered**, **Rejected/Returned**

**Status Definitions:**
1. **Pending**: No delivery yet
2. **Partial**: Partial delivery with percentage (e.g., 65%) + Delivery Order document for delivered items
3. **Delivered**: Fully delivered + Complete Delivery Order document
4. **Rejected/Returned**: Delivery rejected or materials returned

**Document-Based Verification:**
The uploaded Delivery Order document contains:
- List of delivered items
- Quantities for each item
- Units for each item
- Signatures and dates

Future chatbot (Sprint 2+) will read these documents to answer questions like:
- "Is the Kohler shower mixer delivered?"
- "What quantity of WCs were delivered?"

**Use Case:**
```
PO-2025-001: Sanitary Wares (50 items)

Delivery 1:
├─ Status: Partial
├─ Percentage: 40%
├─ Document: delivery_order_001_batch1.pdf
│   └─ Contains: 20 items delivered (shower heads, mixers, etc.)
└─ Date: Nov 1, 2025

Delivery 2:
├─ Status: Delivered
├─ Percentage: 100%
├─ Document: delivery_order_001_final.pdf
│   └─ Contains: Remaining 30 items + summary
└─ Date: Nov 15, 2025

User asks chatbot: "Is Kohler shower mixer delivered?"
→ Chatbot reads delivery_order_001_final.pdf
→ Confirms: "Yes, delivered on Nov 15, 2025, Qty: 5 pieces"
```

---

## Database Migration

**File:** `migrations/field_structure_update_20251004.py`

**What it does:**
1. Backs up existing data
2. Warns about quantity/unit data that will be lost
3. Adds new columns to tables
4. Notes removed columns (SQLite limitation - can't drop columns easily)

**To run:**
```bash
python migrations/field_structure_update_20251004.py
```

**Data Impact:**
- ⚠️ Material quantity/unit data will be lost (moved to PO level tracking)
- ⚠️ Delivery quantity data will be lost (moved to document-based tracking)
- ✓ All other data preserved
- ✓ New fields added with defaults

---

## Updated Form Structure

### Payment Form
**Fields:**
- PO Reference (dropdown)
- Payment Amount
- Payment Date
- Payment Reference
- Invoice Reference
- Payment Status (Full/Partial) - auto-calculated
- Payment Terms (read-only, from PO)
- Document Upload (invoice, receipt)

**Removed:**
- Quantity
- Unit

**New Features:**
- Shows payment terms from PO
- Reminds user if partial payment + balance due before delivery
- Example: "⚠️ Balance AED 10,500 due before Nov 15 (delivery date)"

---

### Material Form
**Fields:**
- Material Type
- Description
- Approval Status (Pending, Under Review, Approved, Approved as Noted, Revise & Resubmit)
- Approval Date
- Revision Number (auto-incremented)
- Previous Submittal (dropdown, if this is a revision)
- Submittal Reference
- Specification Reference
- Approval Notes
- Document Upload (submittal document)

**Removed:**
- Quantity
- Unit

**New Features:**
- Revision tracking with full history
- Link to previous submittal for revisions
- Document upload for each submittal version

---

### Delivery Form
**Fields:**
- PO Reference (dropdown)
- Expected Delivery Date
- Actual Delivery Date
- Delivery Status (Pending, Partial, Delivered, Rejected/Returned)
- Delivery Percentage (if Partial)
- Tracking Number
- Carrier
- Delivery Location
- Received By
- Notes
- Document Upload (Delivery Order)

**Removed:**
- Ordered Quantity
- Delivered Quantity
- Unit

**New Features:**
- Percentage tracking for partial deliveries
- Mandatory document upload (Delivery Order)
- Document contains all item-level details
- Future: Chatbot reads documents to answer specific item questions

---

## Validation Updates Needed

The Data Processing Agent (`services/data_processing_agent.py`) needs updates for:

1. **Payment Validation:**
   - Check payment terms from PO
   - Calculate balance remaining
   - Compare against delivery date
   - Generate reminder if needed

2. **Material Validation:**
   - Check for existing revisions
   - Validate revision number sequence
   - Ensure previous_submittal_id exists if revision > 0
   - Check document upload

3. **Delivery Validation:**
   - Require delivery_percentage if status = Partial
   - Require document_path (Delivery Order)
   - Validate percentage (0-100)
   - Check against expected delivery date

---

## Next Steps

1. ✅ Models updated
2. ✅ Migration script created
3. ⏳ Run migration: `python migrations/field_structure_update_20251004.py`
4. ⏳ Update HTML forms to remove quantity/unit fields
5. ⏳ Update HTML forms to add new fields
6. ⏳ Update route handlers (payments.py, materials.py, deliveries.py)
7. ⏳ Update validation logic in data_processing_agent.py
8. ⏳ Test all forms with new structure
9. ⏳ Update documentation

---

## Benefits

✅ **Simpler Tracking**: No need to track individual item quantities across multiple forms
✅ **Realistic**: Aligns with actual PO structure (one PO, many items)
✅ **Document-Based Proof**: Delivery Orders provide authoritative record
✅ **Revision History**: Complete audit trail for material submittals
✅ **Payment Reminders**: Automated reminders based on payment terms and delivery dates
✅ **Future-Ready**: Document intelligence (Sprint 2) will extract item details from uploaded documents

---

## Examples

### Example 1: Sanitary Wares PO

```
PO-2025-001: Sanitary Wares - AED 45,000
Supplier: Kohler Middle East
Payment Terms: 30% advance, 70% before delivery
Delivery Terms: 45 days from PO date

Materials Covered:
- Shower mixers (various models) - 15 pieces
- Shower heads - 20 pieces
- WCs (wall-hung) - 8 pieces
- WCs (floor-mounted) - 12 pieces
- Shattafs - 25 pieces
- Accessories - 50+ pieces

Material Submittal:
└─ Material Type: "Sanitary Wares - Kohler"
    ├─ Rev 0: Submitted Oct 1 → Revise & Resubmit
    ├─ Rev 1: Submitted Oct 10 → Approved as Noted
    └─ Rev 2: Submitted Oct 15 → Approved ✓

Payments:
├─ Payment 1: AED 13,500 (30% advance) - Oct 5
│   └─ Status: Partial
│   └─ Reminder: "Balance AED 31,500 due before Nov 20"
└─ Payment 2: AED 31,500 (70% balance) - Nov 18
    └─ Status: Full ✓

Deliveries:
├─ Delivery 1: Nov 22 - Partial (60%)
│   └─ Document: delivery_order_001_batch1.pdf
│       (Contains: Shower items, WCs - 40 pieces total)
└─ Delivery 2: Nov 30 - Delivered (100%)
    └─ Document: delivery_order_001_final.pdf
        (Contains: Remaining items + complete summary)

Chatbot Query: "Are all Kohler WCs delivered?"
→ Reads delivery_order_001_final.pdf
→ Response: "Yes, all 20 WCs delivered:
   - 8 wall-hung WCs (Nov 22)
   - 12 floor-mounted WCs (Nov 30)"
```

---

## Technical Notes

### SQLite Limitations
- SQLite doesn't support DROP COLUMN easily
- Old columns (quantity, unit) remain in database but are ignored
- Models don't expose these fields anymore
- Run VACUUM to reclaim space (optional)

### Foreign Key Constraints
- Material.previous_submittal_id → Material.id (self-referencing)
- Allows building revision tree
- Cascade delete handled carefully to preserve history

### Document Storage
- All documents stored in `uploads/` directory
- Path stored in database (document_path, delivery_note_path, invoice_path)
- Future: Document intelligence extracts data from PDFs/images

---

## Conclusion

These changes simplify the system while making it more realistic and maintainable:
- **Outer envelope tracking** (PO level) instead of micro-managing individual items
- **Document-based proof** for deliveries
- **Revision history** for material approvals
- **Payment reminders** based on terms and deadlines
- **Ready for AI** - Document intelligence in Sprint 2 will handle item-level details

The system now matches real-world construction project management workflows! 🎉
