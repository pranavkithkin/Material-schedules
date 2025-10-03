# Material Delivery Dashboard - Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for version control)
- n8n (for automation workflows)

## Step-by-Step Installation

### Step 1: Set Up Python Environment

1. **Open PowerShell in the project directory**
   ```powershell
   cd "C:\Users\PKP\Documents\PRANAV\Projects\With a clear picture\9. material delivery dashboard"
   ```

2. **Create a virtual environment**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Step 2: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. **Copy the example environment file**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` file** with your actual API keys:
   - Open `.env` in a text editor
   - Add your Claude API key (get from: https://console.anthropic.com/)
   - Add your OpenAI API key (get from: https://platform.openai.com/api-keys)
   - Add your n8n API key
   - Configure email settings (if using Gmail, use App Password)

   Example:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
   OPENAI_API_KEY=sk-xxxxxxxxxxxxx
   N8N_API_KEY=your-n8n-key
   ```

### Step 4: Initialize Database

1. **Create empty database**
   ```powershell
   python init_db.py
   ```

2. **Or create database with sample data** (recommended for testing)
   ```powershell
   python init_db.py --with-samples
   ```

### Step 5: Run the Application

```powershell
python app.py
```

The application will start at: **http://localhost:5000**

## Project Structure Overview

```
material-delivery-dashboard/
├── app.py                      # Main Flask application entry point
├── config.py                   # Configuration settings
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── .env.example               # Environment variables template
│
├── models/                     # Database models (SQLAlchemy)
│   ├── __init__.py
│   ├── material.py            # Material tracking model
│   ├── purchase_order.py      # PO tracking model
│   ├── payment.py             # Payment tracking model
│   ├── delivery.py            # Delivery tracking model
│   └── ai_suggestion.py       # AI suggestions model
│
├── routes/                     # API routes (Flask Blueprints)
│   ├── __init__.py
│   ├── dashboard.py           # Dashboard routes
│   ├── materials.py           # Material CRUD operations
│   ├── purchase_orders.py     # PO CRUD operations
│   ├── payments.py            # Payment CRUD operations
│   ├── deliveries.py          # Delivery CRUD operations
│   ├── ai_suggestions.py      # AI suggestion management
│   └── chat.py                # Natural language chat interface
│
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── ai_service.py          # AI extraction and processing
│   ├── chat_service.py        # Natural language query processing
│   └── notification_service.py # Email/WhatsApp/Telegram notifications
│
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html              # Base template with navigation
│   ├── dashboard.html         # Main dashboard
│   ├── materials.html         # Materials management page
│   ├── purchase_orders.html   # PO management page
│   ├── payments.html          # Payment tracking page
│   ├── deliveries.html        # Delivery tracking page
│   └── ai_suggestions.html    # AI suggestions review panel
│
├── static/                     # Static files (CSS, JS, uploads)
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   ├── main.js            # Main JavaScript
│   │   ├── chat.js            # Chat interface logic
│   │   └── ai_suggestions.js  # AI suggestions UI logic
│   └── uploads/               # Uploaded documents
│
├── n8n_workflows/             # n8n workflow templates
│   ├── email_monitor.json     # Email monitoring workflow
│   ├── pdf_processor.json     # PDF extraction workflow
│   ├── delivery_tracker.json  # Delivery status updates
│   └── report_generator.json  # Automated reporting
│
├── prompts/                    # AI prompt templates
│   ├── po_extraction.txt      # PO extraction prompts
│   ├── invoice_extraction.txt # Invoice extraction prompts
│   ├── delivery_extraction.txt# Delivery update prompts
│   └── chat_queries.txt       # Natural language query prompts
│
└── tests/                      # Test files
    ├── test_api.py            # API endpoint tests
    └── sample_data.sql        # Sample data SQL
```

## API Endpoints

### Dashboard Routes
- `GET /` - Main dashboard page
- `GET /api/dashboard/stats` - Dashboard statistics

### Material Management
- `GET /api/materials` - Get all materials
- `GET /api/materials/<id>` - Get specific material
- `POST /api/materials` - Create new material
- `PUT /api/materials/<id>` - Update material
- `DELETE /api/materials/<id>` - Delete material
- `GET /api/materials/types` - Get material types list
- `GET /api/materials/statuses` - Get approval statuses list

### Purchase Order Management
- `GET /api/purchase-orders` - Get all POs
- `GET /api/purchase-orders/<id>` - Get specific PO
- `POST /api/purchase-orders` - Create new PO
- `PUT /api/purchase-orders/<id>` - Update PO
- `DELETE /api/purchase-orders/<id>` - Delete PO

### Payment Management
- `GET /api/payments` - Get all payments
- `GET /api/payments/<id>` - Get specific payment
- `POST /api/payments` - Create new payment
- `PUT /api/payments/<id>` - Update payment
- `DELETE /api/payments/<id>` - Delete payment

### Delivery Management
- `GET /api/deliveries` - Get all deliveries
- `GET /api/deliveries/<id>` - Get specific delivery
- `GET /api/deliveries/pending` - Get pending deliveries (for n8n)
- `POST /api/deliveries` - Create new delivery
- `PUT /api/deliveries/<id>` - Update delivery
- `DELETE /api/deliveries/<id>` - Delete delivery

### AI Suggestions (n8n Integration)
- `POST /api/ai-suggestions` - Submit AI suggestion (from n8n)
- `GET /api/ai-suggestions` - Get all suggestions
- `GET /api/ai-suggestions/pending` - Get pending suggestions
- `PUT /api/ai-suggestions/<id>/approve` - Approve suggestion
- `PUT /api/ai-suggestions/<id>/reject` - Reject suggestion

### Chat Interface
- `POST /api/chat` - Send natural language query
- `GET /api/chat/history` - Get chat history

### Notifications (n8n Integration)
- `POST /api/notifications` - Send notification (from n8n)

## Database Schema

### Materials Table
- id (Primary Key)
- material_type (String)
- description (Text)
- approval_status (String)
- approval_date (DateTime)
- approval_notes (Text)
- submittal_ref (String)
- specification_ref (String)
- quantity (Float)
- unit (String)
- created_at, updated_at (DateTime)
- created_by, updated_by (String)

### PurchaseOrders Table
- id (Primary Key)
- material_id (Foreign Key → Materials)
- quote_ref, po_ref (String)
- po_date (DateTime)
- supplier_name, supplier_contact, supplier_email (String)
- total_amount (Float)
- currency (String)
- po_status (String)
- payment_terms, delivery_terms, notes (Text)
- document_path (String)
- created_at, updated_at, created_by, updated_by

### Payments Table
- id (Primary Key)
- po_id (Foreign Key → PurchaseOrders)
- payment_structure (String)
- payment_type (String)
- total_amount, paid_amount, payment_percentage (Float)
- payment_date (DateTime)
- payment_ref, invoice_ref, payment_method (String)
- currency (String)
- payment_status (String)
- notes (Text)
- invoice_path, receipt_path (String)
- created_at, updated_at, created_by, updated_by

### Deliveries Table
- id (Primary Key)
- po_id (Foreign Key → PurchaseOrders)
- expected_delivery_date, actual_delivery_date (DateTime)
- delivery_status (String)
- ordered_quantity, delivered_quantity (Float)
- unit (String)
- tracking_number, carrier (String)
- delivery_location, received_by (String)
- is_delayed (Boolean)
- delay_reason (Text)
- delay_days (Integer)
- notes (Text)
- delivery_note_path (String)
- created_at, updated_at, created_by, updated_by

### AISuggestions Table
- id (Primary Key)
- target_table (String) - materials, purchase_orders, payments, deliveries
- target_id (Integer) - ID of record to update
- action_type (String) - create, update
- ai_model (String) - claude-3, gpt-4, etc.
- confidence_score (Float) - 0-100
- extraction_source (String) - email, pdf, etc.
- source_document_path (String)
- suggested_data (JSON Text)
- current_data (JSON Text)
- ai_reasoning (Text)
- missing_fields (JSON Array)
- status (String) - pending, approved, rejected, auto_applied
- reviewed_by (String)
- reviewed_at (DateTime)
- review_notes (Text)
- created_at (DateTime)

## AI Confidence System

### Confidence Levels

1. **High Confidence (≥90%)**
   - Action: Auto-update database
   - Flag: "AI Updated" shown in UI
   - Status: `auto_applied`
   
2. **Medium Confidence (60-89%)**
   - Action: Flag for human review
   - Shows in AI Suggestions panel
   - Status: `pending`
   
3. **Low Confidence (<60%)**
   - Action: Discard or flag as low confidence
   - May show in logs only
   - Status: Not created or marked as `rejected`

### AI Suggestion Workflow

```
n8n Extracts Data
     ↓
POST /api/ai-suggestions
     ↓
Confidence >= 90%? ──Yes→ Auto-apply + Flag as "AI Updated"
     ↓ No
Confidence >= 60%? ──Yes→ Create pending suggestion
     ↓ No
Discard or log low confidence
```

## n8n Integration Setup

### 1. Install n8n

```powershell
npm install -g n8n
```

### 2. Start n8n

```powershell
n8n start
```

Access at: **http://localhost:5678**

### 3. Configure Credentials in n8n

- Add HTTP credentials with Bearer token (use N8N_API_KEY from .env)
- Add Claude/OpenAI API credentials
- Add email credentials (SMTP)
- Add WhatsApp/Telegram credentials (optional)

### 4. Import Workflows

- Go to n8n → Workflows → Import
- Import JSON files from `n8n_workflows/` folder

### 5. Configure Webhooks

Each workflow should point to:
```
http://localhost:5000/api/ai-suggestions
http://localhost:5000/api/notifications
```

## Testing the Application

### 1. Manual Testing

1. Start the application: `python app.py`
2. Open browser: http://localhost:5000
3. Test manual data entry:
   - Add a material
   - Create a PO
   - Add payment details
   - Track delivery

### 2. Test AI Suggestions

1. Make sure n8n is NOT running (to test manual mode)
2. Verify all manual operations work
3. Start n8n
4. Send test email to monitored inbox
5. Check AI Suggestions panel for extracted data
6. Approve or reject suggestions

### 3. Test Chat Interface

1. Click on Chat icon in dashboard
2. Try queries:
   - "Which materials are delayed?"
   - "Show me pending deliveries"
   - "What is the status of DB material?"
   - "List all approved materials"

## Common Issues & Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure virtual environment is activated
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: Database not found

**Solution:** Initialize database
```powershell
python init_db.py --with-samples
```

### Issue: API keys not working

**Solution:** Check .env file
- Make sure no spaces around = sign
- API keys should be on same line
- No quotes needed around values

### Issue: n8n can't connect to Flask

**Solution:** 
- Make sure Flask is running
- Check firewall settings
- Use http://localhost:5000 (not 127.0.0.1)
- Verify N8N_API_KEY matches in both .env and n8n credentials

### Issue: PowerShell execution policy error

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

1. ✅ Install Python and dependencies
2. ✅ Configure .env file
3. ✅ Initialize database
4. ✅ Run application and test manually
5. ⬜ Install and configure n8n
6. ⬜ Import n8n workflows
7. ⬜ Test AI automation
8. ⬜ Customize for your project needs

## Support

For issues or questions:
1. Check this guide
2. Review error messages in terminal
3. Check browser console (F12)
4. Review application logs

## Production Deployment

When ready for production:
1. Change `FLASK_ENV=production` in .env
2. Use PostgreSQL instead of SQLite
3. Set up proper authentication/authorization
4. Use gunicorn or similar WSGI server
5. Set up SSL/HTTPS
6. Configure firewall rules
7. Set up automated backups

---

**Important Security Notes:**
- Never commit .env file to git
- Use strong API keys
- Enable authentication before deploying
- Regularly update dependencies
- Monitor AI confidence thresholds
