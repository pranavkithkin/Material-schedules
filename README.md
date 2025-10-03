# Material Delivery Dashboard

AI-powered delivery schedule tracking system for construction projects with n8n automation integration.

## Features

- **Dual-Mode Operation**: Manual data entry + AI-powered automation
- **Material Tracking**: Track 35+ material types with approval status
- **PO Management**: Complete purchase order lifecycle tracking
- **Payment Tracking**: Multi-structure payment monitoring (Single/Advance+Balance)
- **Delivery Status**: Real-time delivery tracking with AI predictions
- **AI Confidence System**: Smart auto-updates based on confidence scores
- **Natural Language Chat**: Query your data using plain English
- **n8n Integration**: Automated workflows for email/PDF processing
- **Audit Trail**: Complete tracking of all human and AI updates

## Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Up Environment Variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Initialize Database**
```bash
python init_db.py
```

4. **Run the Application**
```bash
python app.py
```

5. **Access Dashboard**
```
http://localhost:5000
```

## Project Structure

```
material-delivery-dashboard/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── init_db.py                 # Database initialization script
├── models/                    # Database models
│   ├── __init__.py
│   ├── material.py
│   ├── purchase_order.py
│   ├── payment.py
│   ├── delivery.py
│   └── ai_suggestion.py
├── routes/                    # API routes
│   ├── __init__.py
│   ├── dashboard.py
│   ├── materials.py
│   ├── purchase_orders.py
│   ├── payments.py
│   ├── deliveries.py
│   ├── ai_suggestions.py
│   └── chat.py
├── services/                  # Business logic
│   ├── __init__.py
│   ├── ai_service.py
│   ├── chat_service.py
│   └── notification_service.py
├── templates/                 # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── materials.html
│   ├── purchase_orders.html
│   ├── payments.html
│   ├── deliveries.html
│   └── ai_suggestions.html
├── static/                    # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── chat.js
│   │   └── ai_suggestions.js
│   └── uploads/              # Document uploads
├── n8n_workflows/            # n8n workflow examples
│   ├── email_monitor.json
│   ├── pdf_processor.json
│   ├── delivery_tracker.json
│   └── report_generator.json
├── prompts/                  # AI prompt templates
│   ├── po_extraction.txt
│   ├── invoice_extraction.txt
│   ├── delivery_extraction.txt
│   └── chat_queries.txt
└── tests/                    # Test files
    ├── test_api.py
    └── sample_data.sql
```

## API Endpoints

### For Dashboard
- `GET /` - Main dashboard
- `GET /materials` - Materials view
- `GET /purchase-orders` - PO view
- `GET /payments` - Payments view
- `GET /deliveries` - Deliveries view
- `GET /ai-suggestions` - AI suggestions review panel

### For n8n Integration
- `POST /api/suggestion` - Submit AI-extracted data
- `GET /api/materials` - Fetch current materials data
- `POST /api/notification` - Send alerts
- `GET /api/pending-deliveries` - Get upcoming deliveries
- `POST /api/chat` - Natural language queries

## Environment Variables

```
FLASK_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///delivery_dashboard.db
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key
N8N_API_KEY=your-n8n-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password
```

## AI Confidence Levels

- **≥90%**: Auto-update with "AI Updated" flag
- **60-89%**: Flag for human review
- **<60%**: Discard or flag as low confidence

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (can switch to PostgreSQL)
- **AI**: Claude API + OpenAI API
- **Automation**: n8n
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Authentication**: JWT tokens

## License

Proprietary - Internal Project Use Only
