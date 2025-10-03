# AI-Powered Delivery Schedule Tracking Dashboard - Project Requirements

## PROJECT CONTEXT

### Material Types to Track (35 items)
1. PVC Conduits & Accessories
2. Light Fittings (Internal & External)
3. Light Fittings (Decorative Light fittings)
4. Cable Gland & Accessories
5. Earthing & LPS System
6. GI Conduit & Accessories
7. Cables & Wires
8. Wiring Accessories
9. DB
10. GRMS
11. Fire Alarm system
12. Emergency Lighting system
13. Structured Cabling System & cctv -low current system
14. Isolator
15. VRF System
16. ERV Unit
17. GI Duct
18. Duct Heater
19. Dampers
20. Air Outlets
21. Duct Insulation (Thermal)
22. Duct Insulation (Thermal)(Alternative)
23. Duct Insulation (Acoustic)
24. Sealent. Adhesives,Coating & Vapour Barrier
25. Flexible Duct
26. Aluminum Tape
27. Flexible Duct Connector
28. Fire Fighting system
29. Fire Extinguisher
30. PPR pipe and fittings
31. Condensation drainpipe
32. PEX pipe and fittings
33. Valves
34. Sanitary wares
35. Solar Water heater system

## SYSTEM ARCHITECTURE

- **Primary**: Flask web dashboard for manual data entry and viewing
- **Secondary**: n8n workflows (runs intermittently on office PC) for AI automation
- **Database**: Shared between Dashboard and n8n
- **AI Models**: Claude API and OpenAI API for data extraction

## KEY REQUIREMENTS

### 1. DUAL-MODE OPERATION
- **Manual Mode**: Always available - users can add/edit all data manually
- **AI Mode**: When n8n is running - AI suggests updates, human approves/rejects
- AI only updates automatically if confidence > 90%, otherwise flags for review

### 2. DASHBOARD FEATURES

#### Material Tracking Fields
- Approved
- Approved as Noted
- Pending
- Under Review
- Revise & Resubmit

#### PO Tracking Fields
- Quote Ref
- PO Ref
- PO Date
- Supplier Name
- Total Amount
- etc.

#### PO Status Options
- Not Released
- Released
- Cancelled

#### Payment Tracking Fields
- Total Amount
- Paid Amount
- Payment Percentage
- Payment Date

#### Payment Structure
- Single Payment
- Advance + Balance

#### Currency
- AED

#### Delivery Tracking Fields
- Expected Delivery Date
- Actual Delivery Date
- Delivery Status

#### Delivery Status Options
- Pending
- In Transit
- Partial Delivery
- Completed
- Delayed

#### Additional Features
- AI Suggestions review panel
- Natural language chat interface for queries
- AI must ask if some data is missing with buttons and text fields as suitable (human can skip also)

### 3. N8N AUTOMATION WORKFLOWS
- Email monitoring (extract PO details from supplier emails)
- PDF document processing (extract data from submittals, invoices)
- Delivery status updates (with confidence scoring)
- Payment validation (cross-check invoices vs PO)
- Delay predictions and alerts
- Weekly/monthly report generation
- Notification system (email/WhatsApp/telegram when n8n is on)

### 4. AI CONFIDENCE SYSTEM
- Extract data with confidence score (0-100%)
- **If confidence >= 90%**: Auto-update with "AI Updated" flag
- **If confidence 60-89%**: Flag for human review with AI suggestion
- **If confidence < 60%**: Discard or flag as low confidence
- Always show AI reasoning for transparency

### 5. NATURAL LANGUAGE INTERFACE
- Chat box on dashboard
- Example queries:
  - "Which materials are delayed?"
  - "When is DB arriving?"
  - "Show payment status"
- AI queries database and responds in natural language
- Show data sources in response

### 6. DATABASE DESIGN

#### Main Tables
- Materials
- PurchaseOrders
- Payments
- Deliveries

#### AI Tracking
- AI Suggestions table (stores pending/approved/rejected updates)

#### Audit Trail
- Track who updated (Human/AI) and when
- Confidence scores stored with AI updates

### 7. API ENDPOINTS FOR N8N
- `POST /api/suggestion` - n8n submits AI-extracted data
- `GET /api/materials` - n8n fetches current data
- `POST /api/notification` - n8n sends alerts
- `GET /api/pending-deliveries` - n8n gets upcoming deliveries for reminders

### 8. TECHNICAL SETUP
- Flask backend with RESTful API
- SQLite or PostgreSQL database
- JWT or API key authentication for n8n
- File upload/download for documents
- Responsive UI with Tailwind CSS
- Chat interface using Claude/OpenAI API

## DELIVERABLES NEEDED

1. Complete project structure with all files
2. Database schema with all tables
3. Flask app with routes and API endpoints
4. Dashboard HTML templates
5. n8n workflow JSON files (examples)
6. AI prompt templates for extraction tasks
7. Setup documentation
8. Sample data for testing

## IMPORTANT CONSTRAINTS

- n8n runs intermittently (not 24/7)
- Manual entry must always work independently
- High confidence threshold before auto-updates
- All AI actions must be auditable
- System should gracefully handle n8n being offline

## PROJECT DEVELOPMENT RULES

### Environment & Execution
1. **ALWAYS use WSL terminal** for all Python/Git commands
   - Use `wsl` command before running any Python scripts
   - Activate venv in WSL: `source venv/bin/activate`
   - Run all Flask/Python commands in WSL environment
   - Execute Git commands through WSL (not PowerShell)

### File Management
2. **NEVER create "updated", "renewed", or versioned documentation files**
   - Update existing files in-place (e.g., `COMPLETE_ROADMAP.md`)
   - Do NOT create: `UPDATED_ROADMAP_N8N.md`, `COMPLETE_ROADMAP_V2.md`, etc.
   - Keep ONE authoritative version of each document
   - Use Git for version history, not multiple files

3. **Consolidate documentation**
   - One roadmap file: `COMPLETE_ROADMAP.md`
   - One architecture file: `PROJECT_REQUIREMENTS.md` (this file)
   - Delete redundant or duplicate documentation
   - Update sections within existing files rather than creating new ones

### Code Changes
4. **Update, don't duplicate**
   - Modify existing functions/classes in-place
   - Don't create `function_v2()` or `new_function()` alongside old ones
   - Replace old code, don't append alternatives
   - Keep codebase clean and maintainable

### Communication
5. **Clear and concise**
   - Provide direct answers without excessive explanations
   - Show actual code/terminal output when relevant
   - Summarize changes made rather than showing full file contents
   - Focus on what matters to the user

---

**Project Start Date**: October 3, 2025
