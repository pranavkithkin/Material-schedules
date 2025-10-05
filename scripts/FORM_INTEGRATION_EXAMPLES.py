"""
FORM INTEGRATION GUIDE - Data Processing Agent
Examples of how to integrate validation into existing forms

This shows how to add real-time validation to LPO, Invoice, Submittal, and Delivery forms
"""


# ============================================================================
# FRONTEND JAVASCRIPT INTEGRATION
# ============================================================================

"""
Add this to your form templates (e.g., templates/lpo_form.html)

<script>
// Validation function - call before form submission
async function validateBeforeSave() {
    const formData = {
        record_type: 'lpo_release',  // or 'invoice', 'submittal', 'delivery'
        data: {
            lpo_number: document.getElementById('lpo_number').value,
            material_name: document.getElementById('material_name').value,
            quantity: parseFloat(document.getElementById('quantity').value),
            unit: document.getElementById('unit').value,
            unit_rate: parseFloat(document.getElementById('unit_rate').value),
            total_amount: parseFloat(document.getElementById('total_amount').value),
            supplier_name: document.getElementById('supplier_name').value,
            expected_delivery_date: document.getElementById('expected_delivery_date').value,
            contact_person: document.getElementById('contact_person').value,
            contact_phone: document.getElementById('contact_phone').value,
            contact_email: document.getElementById('contact_email').value
        },
        check_duplicates: true
    };
    
    try {
        const response = await fetch('/api/agents/validate-and-check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': '{{ api_key }}'  // Get from session/config
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (!result.success) {
            showError('Validation failed: ' + result.message);
            return false;
        }
        
        // Clear previous errors
        clearValidationMessages();
        
        // Show errors
        if (result.errors.length > 0) {
            showErrors(result.errors);
            return false;
        }
        
        // Show warnings (but allow save)
        if (result.warnings.length > 0) {
            const proceed = confirm(
                'Warnings found:\\n' + result.warnings.join('\\n') + 
                '\\n\\nDo you want to continue?'
            );
            if (!proceed) return false;
        }
        
        // Show duplicates (but allow save)
        if (result.duplicates.length > 0) {
            const proceed = confirm(
                'Potential duplicates found:\\n' + 
                result.duplicates.map(d => 
                    `${d.record_type}: ${d.identifier} (${Math.round(d.similarity * 100)}% match)`
                ).join('\\n') +
                '\\n\\nDo you want to continue?'
            );
            if (!proceed) return false;
        }
        
        // All checks passed!
        return true;
        
    } catch (error) {
        console.error('Validation error:', error);
        showError('Validation failed. Please try again.');
        return false;
    }
}

// Helper functions
function showErrors(errors) {
    const errorDiv = document.getElementById('validation-errors');
    errorDiv.innerHTML = '<div class="alert alert-danger">' +
        '<strong>Please fix the following errors:</strong><ul>' +
        errors.map(err => `<li>${err}</li>`).join('') +
        '</ul></div>';
    errorDiv.style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('validation-errors');
    errorDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    errorDiv.style.display = 'block';
}

function clearValidationMessages() {
    document.getElementById('validation-errors').style.display = 'none';
}

// Attach to form submit
document.getElementById('lpo-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const isValid = await validateBeforeSave();
    if (isValid) {
        // Proceed with actual form submission
        this.submit();
    }
});

// Optional: Real-time validation as user types
document.getElementById('lpo_number').addEventListener('blur', async function() {
    // Quick validation of just this field
    const result = await validateBeforeSave();
    // Show inline error if any
});
</script>

<!-- Add this HTML to your form -->
<div id="validation-errors" style="display: none;"></div>
"""


# ============================================================================
# BACKEND PYTHON INTEGRATION
# ============================================================================

"""
Example: Update routes/purchase_orders.py to use validation before saving
"""

def example_lpo_create_route():
    """
    Example: Add validation to LPO creation route
    """
    from flask import Blueprint, request, jsonify
    from models import db, LPORelease
    from services.data_processing_agent import DataProcessingAgent
    
    @purchase_orders_bp.route('/lpo/create', methods=['POST'])
    def create_lpo():
        """Create new LPO with validation"""
        data = request.get_json()
        
        # Initialize agent
        agent = DataProcessingAgent(db.session)
        
        # Validate before saving
        validation_result = agent.process_data(
            record_type='lpo_release',
            data=data,
            check_duplicates=True
        )
        
        # Check if valid
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_result['errors'],
                'warnings': validation_result['warnings']
            }), 400
        
        # Check for duplicates (warn but allow)
        if validation_result['duplicates']:
            # Log warning but proceed
            print(f"Warning: Potential duplicates found for LPO {data['lpo_number']}")
        
        # All good - save to database
        try:
            new_lpo = LPORelease(
                lpo_number=data['lpo_number'],
                material_name=data['material_name'],
                quantity=data['quantity'],
                unit=data['unit'],
                unit_rate=data['unit_rate'],
                total_amount=data['total_amount'],
                supplier_name=data['supplier_name'],
                expected_delivery_date=data['expected_delivery_date'],
                contact_person=data['contact_person'],
                contact_phone=data['contact_phone'],
                contact_email=data['contact_email']
            )
            
            db.session.add(new_lpo)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'LPO created successfully',
                'lpo_id': new_lpo.id,
                'validation_result': validation_result
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}'
            }), 500


def example_invoice_create_with_lpo_matching():
    """
    Example: Create invoice with automatic LPO matching
    """
    from flask import Blueprint, request, jsonify
    from models import db, Invoice
    from services.data_processing_agent import DataProcessingAgent
    
    @payments_bp.route('/invoice/create', methods=['POST'])
    def create_invoice():
        """Create invoice with LPO matching"""
        data = request.get_json()
        
        # Initialize agent
        agent = DataProcessingAgent(db.session)
        
        # Validate + match to LPO
        validation_result = agent.process_data(
            record_type='invoice',
            data=data,
            check_duplicates=True,
            match_invoice_to_lpo=True  # Enable LPO matching
        )
        
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_result['errors']
            }), 400
        
        # Check if LPO was matched
        matched_lpo_id = validation_result.get('matched_lpo_id')
        if matched_lpo_id:
            confidence = validation_result.get('confidence_score', 0)
            print(f"Matched invoice to LPO ID {matched_lpo_id} (confidence: {confidence:.0%})")
        
        # Save invoice
        try:
            new_invoice = Invoice(
                invoice_number=data['invoice_number'],
                invoice_date=data['invoice_date'],
                material_name=data['material_name'],
                quantity=data['quantity'],
                unit=data['unit'],
                unit_rate=data['unit_rate'],
                total_amount=data['total_amount'],
                supplier_name=data['supplier_name'],
                payment_terms=data['payment_terms'],
                due_date=data['due_date'],
                lpo_id=matched_lpo_id  # Auto-link to LPO!
            )
            
            db.session.add(new_invoice)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Invoice created successfully',
                'invoice_id': new_invoice.id,
                'matched_lpo_id': matched_lpo_id,
                'validation_result': validation_result
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}'
            }), 500


# ============================================================================
# n8n WEBHOOK INTEGRATION
# ============================================================================

"""
Example: n8n workflow calls validation after AI extraction

n8n Workflow:
1. User uploads PDF invoice
2. Claude API extracts data
3. Call Flask validation endpoint
4. If valid -> auto-save, if invalid -> prompt user for review

n8n HTTP Request Node:
URL: http://localhost:5000/api/agents/validate-and-check
Method: POST
Headers:
  - Content-Type: application/json
  - X-API-Key: {{ $env.FLASK_API_KEY }}
Body:
{
  "record_type": "invoice",
  "data": {{ $json.extracted_data }},
  "check_duplicates": true,
  "match_invoice_to_lpo": true
}

n8n IF Node (check result):
Condition: {{ $json.is_valid }} === true

Branch A (Valid):
  -> HTTP Request to save invoice
  -> Send success notification

Branch B (Invalid):
  -> Create AI suggestion for user review
  -> Send notification "Please review AI-extracted invoice"
"""


# ============================================================================
# BATCH VALIDATION EXAMPLE
# ============================================================================

def example_bulk_import_with_validation():
    """
    Example: Validate multiple records before bulk import
    """
    import requests
    
    def bulk_import_lpos(lpo_list):
        """Import multiple LPOs with validation"""
        
        # Prepare batch request
        batch_data = {
            'records': [
                {
                    'record_type': 'lpo_release',
                    'data': lpo
                }
                for lpo in lpo_list
            ],
            'check_duplicates': True,
            'stop_on_error': False  # Validate all, don't stop on first error
        }
        
        # Call batch validation endpoint
        response = requests.post(
            'http://localhost:5000/api/agents/validate-and-check/batch',
            json=batch_data,
            headers={'X-API-Key': 'your-api-key'}
        )
        
        result = response.json()
        
        print(f"Batch validation complete:")
        print(f"  Total: {result['summary']['total']}")
        print(f"  Valid: {result['summary']['valid']}")
        print(f"  Invalid: {result['summary']['invalid']}")
        print(f"  Duplicates found: {result['summary']['duplicates_found']}")
        
        # Process results
        valid_lpos = []
        invalid_lpos = []
        
        for idx, validation_result in enumerate(result['results']):
            if validation_result['is_valid']:
                valid_lpos.append((lpo_list[idx], validation_result))
            else:
                invalid_lpos.append((lpo_list[idx], validation_result))
        
        # Save valid LPOs
        for lpo_data, validation in valid_lpos:
            # Save to database
            pass
        
        # Report invalid LPOs
        for lpo_data, validation in invalid_lpos:
            print(f"Invalid LPO {lpo_data['lpo_number']}:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        return valid_lpos, invalid_lpos


# ============================================================================
# TESTING THE API
# ============================================================================

def example_manual_test():
    """
    Manual test script - run this to test the API
    """
    import requests
    from datetime import datetime, timedelta
    
    # Test data
    test_lpo = {
        'record_type': 'lpo_release',
        'data': {
            'lpo_number': 'TEST-LPO-001',
            'material_name': 'Test Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 5000.0,
            'supplier_name': 'Test Supplier',
            'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'contact_person': 'John Doe',
            'contact_phone': '+971501234567',
            'contact_email': 'john@test.com'
        },
        'check_duplicates': True
    }
    
    # Call API
    response = requests.post(
        'http://localhost:5000/api/agents/validate-and-check',
        json=test_lpo,
        headers={'X-API-Key': 'your-api-key-here'}
    )
    
    result = response.json()
    
    print("Validation Result:")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Warnings: {result['warnings']}")
    print(f"  Duplicates: {len(result['duplicates'])}")
    print(f"  Processing time: {result['processing_time_ms']}ms")
    print(f"  Ready to save: {result['ready_to_save']}")


# ============================================================================
# RECOMMENDED USAGE PATTERNS
# ============================================================================

"""
PATTERN 1: Frontend Real-time Validation
- User types in form
- On blur/change events, call validation API
- Show inline errors immediately
- Prevent form submission if invalid

PATTERN 2: Backend Pre-save Validation
- User submits form
- Backend calls validation before INSERT
- Return errors if invalid
- Save if valid

PATTERN 3: AI-Assisted Validation
- n8n extracts data from document
- n8n calls validation API
- If valid -> auto-save
- If invalid -> create suggestion for human review

PATTERN 4: Batch Import Validation
- User uploads CSV/Excel
- Parse all records
- Call batch validation endpoint
- Show validation report
- Import only valid records

RECOMMENDED: Use PATTERN 1 + PATTERN 2 together!
- Pattern 1 gives instant feedback to user
- Pattern 2 ensures data integrity at database level
"""


if __name__ == '__main__':
    print(__doc__)
    print("\n" + "="*70)
    print("This is a reference guide - see examples above for integration!")
    print("="*70)
