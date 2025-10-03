# 🎯 PROJECT RULES & GUIDELINES
## Material Delivery Dashboard - Development Standards

---

## 📖 GOLDEN RULES

### Rule #1: Always Check Progress First
**BEFORE starting ANY work:**

1. ✅ **Read `COMPLETE_ROADMAP.md`** - Understand which phase we're in
2. ✅ **Read `IMPLEMENTATION_STATUS.md`** - Check what's completed vs pending
3. ✅ **Ask the user** - "Where are we in the roadmap? What's the next step?"
4. ✅ **Confirm understanding** - Summarize current status before proceeding

**Example Check:**
```
Current Status Check:
- Phase: 1.3 (Basic Dashboard UI)
- Completed: Database models, API endpoints, templates
- Next Step: Phase 1.4 (File Upload System)
- User Confirmed: Yes/No
```

### Rule #2: Follow the Project Structure Religiously
**ALL files must follow this structure:**

```
9. material delivery dashboard/
├── app.py                      # Main Flask app
├── config.py                   # Configuration
├── init_db.py                  # Database initialization
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (not in repo)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
│
├── models/                     # Database Models
│   ├── __init__.py
│   ├── material.py
│   ├── purchase_order.py
│   ├── payment.py
│   ├── delivery.py
│   └── ai_suggestion.py
│
├── routes/                     # API Routes
│   ├── __init__.py
│   ├── dashboard.py
│   ├── materials.py
│   ├── purchase_orders.py
│   ├── payments.py
│   ├── deliveries.py
│   ├── ai_suggestions.py
│   ├── chat.py
│   └── uploads.py             # TO BE CREATED
│
├── services/                   # Business Logic
│   ├── __init__.py
│   ├── ai_service.py
│   ├── chat_service.py
│   ├── notification_service.py
│   └── document_service.py    # TO BE CREATED
│
├── templates/                  # HTML Templates
│   ├── base.html
│   ├── dashboard.html
│   ├── materials.html
│   ├── purchase_orders.html
│   ├── payments.html
│   ├── deliveries.html
│   ├── ai_suggestions.html
│   └── uploads.html           # TO BE CREATED
│
├── static/                     # Static Files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   └── chat.js
│   └── uploads/               # User uploaded files
│
├── prompts/                    # AI Prompt Templates
│   ├── po_extraction.txt
│   ├── invoice_extraction.txt
│   ├── delivery_extraction.txt
│   └── chat_queries.txt
│
├── n8n_workflows/              # n8n Workflow JSONs
│   ├── email_monitoring.json   # TO BE CREATED
│   ├── pdf_processing.json     # TO BE CREATED
│   ├── delivery_reminders.json # TO BE CREATED
│   └── weekly_report.json      # TO BE CREATED
│
├── tests/                      # Unit Tests
│   ├── __init__.py
│   ├── test_models.py         # TO BE CREATED
│   ├── test_routes.py         # TO BE CREATED
│   └── test_services.py       # TO BE CREATED
│
└── docs/                       # Documentation
    ├── README.md
    ├── QUICK_START.md
    ├── STEP_BY_STEP_GUIDE.md
    ├── SETUP_GUIDE.md
    ├── PROJECT_REQUIREMENTS.md
    ├── PROJECT_SUMMARY.md
    ├── IMPLEMENTATION_STATUS.md
    ├── COMPLETE_ROADMAP.md
    ├── CHECKLIST.md
    ├── FILE_STRUCTURE.md
    └── PROJECT_RULES.md        # This file
```

**Rules:**
- ❌ **NEVER** create files outside this structure
- ❌ **NEVER** put Python files in root if they belong in a subfolder
- ✅ **ALWAYS** create `__init__.py` in Python package folders
- ✅ **ALWAYS** maintain folder hierarchy
- ✅ **ALWAYS** suggest structure changes if needed before creating files

---

## 📁 File Creation Rules

### Rule #3: Check Before Creating
**BEFORE creating any file:**

1. ✅ Check if file already exists using `file_search` or `list_dir`
2. ✅ Verify the correct folder location
3. ✅ Confirm file naming convention matches existing files
4. ✅ Check if related files need updating

### Rule #4: Naming Conventions
**Follow these naming patterns:**

| File Type | Convention | Example |
|-----------|-----------|---------|
| Python files | `snake_case.py` | `purchase_order.py` |
| HTML templates | `snake_case.html` | `purchase_orders.html` |
| JavaScript | `camelCase.js` | `main.js`, `chatInterface.js` |
| CSS files | `kebab-case.css` | `style.css`, `custom-theme.css` |
| Models | Singular noun | `Material`, `PurchaseOrder` |
| Routes | Plural noun | `materials.py`, `purchase_orders.py` |
| Services | Purpose + Service | `ai_service.py`, `chat_service.py` |
| Documentation | SCREAMING_SNAKE | `README.md`, `SETUP_GUIDE.md` |

### Rule #5: File Headers & Documentation
**EVERY Python file must have:**

```python
"""
Module: [module_name]
Purpose: [Brief description]
Phase: [Roadmap phase, e.g., "Phase 1.4 - File Upload System"]
Dependencies: [List key imports]
"""
```

**Example:**
```python
"""
Module: routes/uploads.py
Purpose: Handle file upload and document processing
Phase: Phase 1.4 - File Upload System
Dependencies: Flask, Werkzeug, ai_service
"""

from flask import Blueprint, request, jsonify
# ... rest of code
```

---

## 🔄 Code Modification Rules

### Rule #6: Read Before Edit
**BEFORE modifying ANY file:**

1. ✅ Read the ENTIRE file first (use `read_file`)
2. ✅ Understand current functionality
3. ✅ Check for dependencies (imports, relationships)
4. ✅ Plan the change without breaking existing code

### Rule #7: Preserve Existing Functionality
**When editing:**

- ❌ **NEVER** remove existing features without user confirmation
- ❌ **NEVER** change database models without migration plan
- ❌ **NEVER** modify API contracts without version update
- ✅ **ALWAYS** add comments for major changes
- ✅ **ALWAYS** test backward compatibility
- ✅ **ALWAYS** update related documentation

### Rule #8: Consistent Code Style
**Follow these patterns:**

```python
# Import Order
# 1. Standard library
import os
import json
from datetime import datetime

# 2. Third-party packages
from flask import Blueprint, request, jsonify
from sqlalchemy import desc

# 3. Local modules
from models.material import Material
from services.ai_service import AIService

# Function naming
def get_all_materials():  # Verb + noun, snake_case
    """Clear docstring"""
    pass

# Class naming
class MaterialService:  # PascalCase
    """Service for material operations"""
    pass

# Constants
MAX_FILE_SIZE = 20 * 1024 * 1024  # SCREAMING_SNAKE_CASE
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png'}
```

---

## 🗃️ Database Rules

### Rule #9: Database Changes Require Planning
**BEFORE modifying database models:**

1. ✅ List all changes needed
2. ✅ Check for breaking changes
3. ✅ Plan data migration if needed
4. ✅ Update `init_db.py` if needed
5. ✅ Document the change in commit message

### Rule #10: Always Use ORM
**Database access rules:**

- ❌ **NEVER** use raw SQL queries
- ✅ **ALWAYS** use SQLAlchemy ORM
- ✅ **ALWAYS** handle database sessions properly
- ✅ **ALWAYS** catch and handle database errors

```python
# GOOD
try:
    material = Material.query.filter_by(id=material_id).first()
    if material:
        material.approval_status = "Approved"
        db.session.commit()
except Exception as e:
    db.session.rollback()
    return {"error": str(e)}, 500

# BAD
db.execute("UPDATE materials SET status='Approved' WHERE id=?", [material_id])
```

---

## 🎨 Frontend Rules

### Rule #11: UI Consistency
**All UI components must:**

- ✅ Use Tailwind CSS classes (already included)
- ✅ Follow existing color scheme:
  - Blue (`blue-600`): Primary actions, materials
  - Green (`green-600`): Purchase orders, success
  - Purple (`purple-600`): Payments
  - Orange (`orange-600`): Deliveries, warnings
  - Red (`red-600`): Errors, delays
  - Gray (`gray-600`): Secondary actions
- ✅ Maintain responsive design (mobile-first)
- ✅ Use existing components (modals, tables, forms)

### Rule #12: JavaScript Patterns
**Follow existing JS patterns:**

```javascript
// Use window.dashboardUtils for common functions
window.dashboardUtils.showLoading();
window.dashboardUtils.hideLoading();
window.dashboardUtils.showToast('Message', 'success');
window.dashboardUtils.formatDate(date);
window.dashboardUtils.formatCurrency(amount);

// Use jQuery for AJAX (already included)
$.ajax({
    url: '/api/endpoint',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(data),
    success: function(response) { },
    error: function(err) { }
});
```

---

## 🤖 AI Integration Rules

### Rule #13: AI Feature Safeguards
**When implementing AI features:**

- ✅ **ALWAYS** check if API keys are configured
- ✅ **ALWAYS** have fallback for missing keys
- ✅ **ALWAYS** validate AI responses before using
- ✅ **ALWAYS** log AI interactions for debugging
- ✅ **ALWAYS** implement confidence scoring
- ✅ **NEVER** auto-apply low confidence suggestions (<60%)

### Rule #14: Confidence Thresholds
**Strictly follow these rules:**

| Confidence | Action | User Notification |
|------------|--------|-------------------|
| ≥ 90% | Auto-apply + Log | "Updated by AI" |
| 60-89% | Create suggestion for review | "Review needed" |
| < 60% | Log only, don't create suggestion | Optional: "Low confidence" |

---

## 📡 API Rules

### Rule #15: RESTful Conventions
**API endpoints must follow:**

```
GET    /api/resource        - List all
GET    /api/resource/<id>   - Get one
POST   /api/resource        - Create
PUT    /api/resource/<id>   - Update
DELETE /api/resource/<id>   - Delete
```

### Rule #16: Response Format
**All API responses must be JSON:**

```python
# Success response
{
    "success": true,
    "message": "Operation completed",
    "data": { ... }
}

# Error response
{
    "success": false,
    "error": "Error message",
    "details": "Detailed explanation"
}
```

### Rule #17: Error Handling
**Every route must handle errors:**

```python
@blueprint.route('/api/endpoint', methods=['POST'])
def endpoint():
    try:
        # Validate input
        if not request.json:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process request
        result = process_data(request.json)
        
        # Return success
        return jsonify({
            'success': True,
            'message': 'Success',
            'data': result
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
```

---

## 📝 Documentation Rules

### Rule #18: Update Documentation
**When creating/modifying features:**

1. ✅ Update `IMPLEMENTATION_STATUS.md` - Mark completed items
2. ✅ Update `COMPLETE_ROADMAP.md` - Check off completed steps
3. ✅ Update `README.md` - If adding major features
4. ✅ Update `FILE_STRUCTURE.md` - If creating new files
5. ✅ Add inline code comments for complex logic

### Rule #19: Commit Messages
**Use clear, descriptive messages:**

```bash
# GOOD
"Add file upload functionality for Phase 1.4"
"Fix: Material deletion now cascades to related records"
"Update: Increase confidence threshold to 92%"

# BAD
"updates"
"fixed bug"
"changes"
```

---

## 🧪 Testing Rules

### Rule #20: Test Before Declaring Complete
**BEFORE marking any phase complete:**

1. ✅ Test all CRUD operations
2. ✅ Test error scenarios
3. ✅ Test with sample data
4. ✅ Test API endpoints (use tools like Postman)
5. ✅ Test UI on different screen sizes
6. ✅ Check browser console for errors

### Rule #21: Sample Data
**Always provide way to test:**

- ✅ Include sample data in `init_db.py`
- ✅ Provide test files for uploads
- ✅ Include example API requests in documentation

---

## 🔒 Security Rules

### Rule #22: Never Commit Secrets
**NEVER include in code:**

- ❌ API keys
- ❌ Passwords
- ❌ Database credentials
- ❌ Secret keys

**ALWAYS use `.env` file:**
```bash
# .env (not committed)
CLAUDE_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# .env.example (committed)
CLAUDE_API_KEY=your-claude-key-here
OPENAI_API_KEY=your-openai-key-here
```

### Rule #23: Input Validation
**ALWAYS validate user input:**

```python
# File upload validation
allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'png'}
max_file_size = 20 * 1024 * 1024  # 20MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# API input validation
required_fields = ['po_number', 'material_id', 'supplier_name']
if not all(field in request.json for field in required_fields):
    return jsonify({'error': 'Missing required fields'}), 400
```

---

## 🚀 Deployment Rules

### Rule #24: Environment-Specific Config
**Support multiple environments:**

```python
# config.py
class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///material_delivery.db'
    
class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URI = os.getenv('DATABASE_URL')
```

---

## 💬 Communication Rules

### Rule #25: Always Confirm Before Big Changes
**ASK USER BEFORE:**

- 🤔 Deleting or significantly modifying existing code
- 🤔 Changing database schema
- 🤔 Modifying API contracts
- 🤔 Installing new packages
- 🤔 Changing project structure

**Example:**
```
"I need to modify the Material model to add file attachments. 
This will require:
1. Adding 'attachments' field (JSON)
2. Running database migration
3. Updating the API endpoint
4. Modifying the UI form

Should I proceed?"
```

### Rule #26: Provide Context
**Always explain:**

- 📍 What you're doing
- 📍 Why you're doing it
- 📍 What phase it belongs to
- 📍 What's next after this

---

## 🎯 Quick Reference Checklist

### Before Starting ANY Task:

- [ ] Read `COMPLETE_ROADMAP.md` - What phase are we in?
- [ ] Read `IMPLEMENTATION_STATUS.md` - What's done/pending?
- [ ] Check existing file structure
- [ ] Ask user to confirm next step
- [ ] Plan the changes needed
- [ ] List files to create/modify

### Before Creating Files:

- [ ] Verify correct folder location
- [ ] Check if file already exists
- [ ] Follow naming conventions
- [ ] Add file header documentation
- [ ] Update `FILE_STRUCTURE.md`

### Before Modifying Code:

- [ ] Read the entire file first
- [ ] Understand current functionality
- [ ] Check dependencies
- [ ] Plan backward compatibility
- [ ] Update related documentation

### After Completing Work:

- [ ] Test the functionality
- [ ] Update `IMPLEMENTATION_STATUS.md`
- [ ] Check off completed items in `COMPLETE_ROADMAP.md`
- [ ] Commit with clear message
- [ ] Inform user what's next

---

## 🎓 Key Principles

1. **Progress Tracking** - Always know where we are in the roadmap
2. **Structure Adherence** - Follow project organization religiously
3. **Documentation First** - Read before writing
4. **Consistency** - Match existing patterns
5. **Safety** - Never break working features
6. **Communication** - Confirm before big changes
7. **Testing** - Verify before declaring complete
8. **Security** - Protect sensitive data
9. **User Focus** - Build what the roadmap specifies
10. **Incremental** - One phase at a time

---

## 📌 Claude's Self-Check

**Before responding to ANY user request, ask yourself:**

1. ❓ "Have I checked the roadmap status?"
2. ❓ "Do I understand what phase we're in?"
3. ❓ "Am I following the project structure?"
4. ❓ "Am I maintaining consistency with existing code?"
5. ❓ "Have I confirmed this with the user if it's a big change?"

**If the answer to ANY is NO → STOP and check first!**

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| Oct 3, 2025 | 1.0 | Initial project rules document |

---

## 📞 When in Doubt

**If you're unsure about anything:**

1. ✅ Check `COMPLETE_ROADMAP.md` first
2. ✅ Check `IMPLEMENTATION_STATUS.md` second
3. ✅ ASK THE USER - Better to confirm than assume!

---

**Remember: These rules ensure project consistency, maintainability, and successful completion! 🎯**
