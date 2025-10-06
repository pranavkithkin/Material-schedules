# 🚀 Phase 3: Automation Workflows - Setup Guide

**Goal:** Automated delivery reminders, weekly reports, and notifications

**Date:** October 6, 2025

---

## ✅ What We've Completed

### **Backend API Endpoints (Flask)**
Added 3 new endpoints to `routes/n8n_webhooks.py`:

1. **`GET /api/n8n/pending-deliveries?days=7`**
   - Returns deliveries due within X days
   - Includes urgency levels (high/medium/low)
   - Full PO and material details included
   
2. **`GET /api/n8n/weekly-report-data`**
   - Comprehensive statistics for reports
   - Materials, POs, Payments, Deliveries summaries
   - Delayed deliveries list
   - Upcoming deliveries (next 7 days)
   - Recent activity tracking
   
3. **`POST /api/n8n/log-notification`**
   - Logs all notifications sent by n8n
   - Tracks delivery reminders, reports, alerts
   - Future: Create Notification model for full tracking

### **n8n Workflows Created**
Created 2 workflow JSON files in `/n8n-workflows/`:

1. **`1_daily_delivery_reminder.json`** - Daily at 8 AM
2. **`2_weekly_report_generator.json`** - Friday at 5 PM

---

## 📋 Setup Instructions

### **Step 1: Test the New API Endpoints**

Start your Flask server and test the endpoints:

```bash
# Start Flask
python app.py

# Test in another terminal:

# 1. Get pending deliveries
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:5001/api/n8n/pending-deliveries?days=7"

# 2. Get weekly report data
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:5001/api/n8n/weekly-report-data"

# 3. Test notification logging
curl -X POST \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"notification_type":"test","recipient":"test@example.com","status":"sent"}' \
  "http://localhost:5001/api/n8n/log-notification"
```

**Expected Results:**
- ✅ Pending deliveries: JSON with list of deliveries + urgency levels
- ✅ Weekly report: JSON with comprehensive statistics
- ✅ Log notification: Success message with notification ID

---

### **Step 2: Configure n8n Environment Variables**

In your n8n instance, add these environment variables:

```bash
# Flask API
FLASK_API_URL=https://your-flask-domain.com  # or http://localhost:5001 for dev

# Email Configuration (Gmail example)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password

# Notification Recipients
NOTIFICATION_EMAIL=team@pkpeng.com  # Where to send reports/alerts
```

**Getting Gmail App Password:**
1. Go to Google Account → Security → 2-Step Verification
2. Scroll to "App passwords"
3. Generate new app password for "Mail"
4. Use that password in `SMTP_PASSWORD`

---

### **Step 3: Import Workflows into n8n**

1. **Open n8n:** Go to `https://n8n1.trart.uk`

2. **Import Workflow #1 - Daily Delivery Reminder:**
   - Click "+" → "Import from File"
   - Select: `/n8n-workflows/1_daily_delivery_reminder.json`
   - Click "Import"

3. **Import Workflow #2 - Weekly Report Generator:**
   - Click "+" → "Import from File"
   - Select: `/n8n-workflows/2_weekly_report_generator.json`
   - Click "Import"

---

### **Step 4: Configure n8n Credentials**

Both workflows need 2 credentials:

#### **Credential 1: Flask API Key (HTTP Header Auth)**
- **Name:** "Flask API Key"
- **Type:** "Header Auth (API Key)"
- **Header Name:** `X-API-Key`
- **Header Value:** Your Flask API key (from `.env` file)

**How to get your API key:**
```bash
# In your project directory:
cat .env | grep API_KEY
# OR generate new one:
python scripts/generate_api_key.py
```

#### **Credential 2: Gmail SMTP**
- **Name:** "Gmail SMTP"
- **Type:** "SMTP"
- **Host:** `smtp.gmail.com`
- **Port:** `587`
- **Security:** `STARTTLS`
- **User:** Your Gmail address
- **Password:** Your Gmail App Password

---

### **Step 5: Activate the Workflows**

For each workflow:

1. **Open the workflow** in n8n
2. **Click "Execute Workflow"** to test manually first
3. **Check for errors** - fix any credential issues
4. **Click "Active"** toggle in top-right to enable scheduled execution

**Schedules:**
- ⏰ **Daily Delivery Reminder:** Every day at 8:00 AM
- ⏰ **Weekly Report:** Every Friday at 5:00 PM

---

## 🧪 Testing the Workflows

### **Test 1: Delivery Reminder (Manual Trigger)**

1. Make sure you have some deliveries with `expected_delivery_date` in the next 7 days
2. Open "Daily Delivery Reminder" workflow in n8n
3. Click "Execute Workflow" button
4. Check your email for delivery reminder

**Expected Email:**
```
Subject: 📅 Delivery Reminder: PKP-LPO-6001-2025-51 - 3 days

Hello Team,

This is a reminder about an upcoming delivery:

📦 Delivery Details:
- PO Reference: PKP-LPO-6001-2025-51
- Material: Fire Fighting
- Supplier: Universal Firefighting systems & services
- Expected Date: 2025-10-09
- Days Until Delivery: 3
- Status: Pending
- Urgency: MEDIUM

💰 Order Amount: 31,500.00 AED
📞 Supplier Contact: +971-XX-XXXXXXX

---
View full details: http://localhost:5001/deliveries
```

### **Test 2: Weekly Report (Manual Trigger)**

1. Open "Weekly Report Generator" workflow in n8n
2. Click "Execute Workflow" button
3. Check your email for weekly report

**Expected Email:**
- Beautiful HTML formatted report
- Overview statistics (materials, POs, payments, deliveries)
- Alerts for delayed deliveries and pending POs
- Upcoming deliveries table
- Payment summary with outstanding amounts
- Activity this week (new POs, completed deliveries)

---

## 📊 Workflow Details

### **Workflow 1: Daily Delivery Reminder**

**Trigger:** Schedule - Every day at 8 AM  
**Purpose:** Send reminders for deliveries due within 7 days

**Flow:**
1. ⏰ Schedule Trigger (8 AM daily)
2. 📡 GET `/api/n8n/pending-deliveries?days=7`
3. ❓ Check if deliveries exist
4. 🔀 Split into individual deliveries
5. ✍️ Format email with delivery details
6. 📧 Send email notification
7. 📝 Log notification to database

**Urgency Levels:**
- 🚨 **High:** 0-2 days until delivery
- ⚠️ **Medium:** 3-5 days until delivery
- 📅 **Low:** 6-7 days until delivery

---

### **Workflow 2: Weekly Report Generator**

**Trigger:** Schedule - Every Friday at 5 PM  
**Purpose:** Send comprehensive weekly summary report

**Flow:**
1. ⏰ Schedule Trigger (Friday 5 PM)
2. 📡 GET `/api/n8n/weekly-report-data`
3. ✍️ Format beautiful HTML report
4. 📧 Send email report (HTML + plain text fallback)
5. 📝 Log notification to database

**Report Includes:**
- 📈 Overview statistics (materials, POs, payments, deliveries)
- 🚨 Alerts (delayed deliveries, pending POs)
- 📦 Upcoming deliveries table (next 7 days)
- 💰 Payment summary (total, paid, outstanding, completion %)
- 📊 Activity this week (new POs, completed deliveries)

---

## 🎯 Next Steps (Future Enhancements)

### **Workflow 3: Payment Reconciliation (Optional)**
When invoice is uploaded:
- Extract invoice amount and PO reference
- Compare to existing PO
- Flag discrepancies
- Auto-create payment record if amounts match

### **Workflow 4: Delay Prediction (Advanced)**
- Analyze supplier history
- Predict delivery delays
- Send proactive alerts

### **Workflow 5: WhatsApp Notifications (Optional)**
- Integrate Twilio API
- Send urgent reminders via WhatsApp
- Two-way communication for confirmations

---

## 🐛 Troubleshooting

### **Issue: API returns 401 Unauthorized**
**Solution:** Check API key is correct in n8n credentials
```bash
# Verify API key:
cat .env | grep API_KEY
```

### **Issue: Email not sending**
**Solution:** 
1. Check Gmail App Password (not regular password)
2. Enable "Less secure app access" in Gmail settings
3. Check SMTP credentials in n8n

### **Issue: No deliveries in reminder**
**Solution:** Add test deliveries with upcoming dates
```bash
# Check deliveries in database:
sqlite3 instance/delivery_dashboard.db "SELECT * FROM delivery WHERE expected_delivery_date > date('now');"
```

### **Issue: Workflow not running on schedule**
**Solution:**
1. Make sure workflow is "Active" (toggle in top-right)
2. Check n8n is running continuously
3. Check server timezone matches expected schedule

---

## 📈 Monitoring & Metrics

### **Check Notification Logs**
Future: Create a Notifications page to view all sent emails

For now, check Flask console:
```bash
# Look for log messages:
📧 Notification logged: delivery_reminder to team@pkpeng.com
📧 Notification logged: weekly_report to team@pkpeng.com
```

### **API Usage Stats**
Check n8n stats endpoint:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:5001/api/n8n/stats"
```

---

## ✅ Success Criteria

Phase 3 is complete when:

- ✅ All 3 API endpoints working and tested
- ✅ Both n8n workflows imported and activated
- ✅ Daily delivery reminders being sent at 8 AM
- ✅ Weekly reports being sent on Friday at 5 PM
- ✅ Emails are formatted beautifully (HTML)
- ✅ Urgency levels working correctly
- ✅ Notifications logged to database

---

## 🎉 What You'll Have After Phase 3

**Automated Notifications:**
- 📧 Daily delivery reminders (8 AM) for upcoming deliveries
- 📊 Weekly summary reports (Friday 5 PM) with full statistics
- 🚨 Urgency-based alerts (high/medium/low priority)
- 📝 Full notification logging and tracking

**Business Value:**
- ⏰ Never miss a delivery deadline
- 📈 Weekly visibility into project status
- 🔔 Proactive alerts for delayed deliveries
- 📊 Data-driven decision making

---

**Phase 3 Progress: API Complete (100%) | Workflows Created (100%) | Testing Required**

**Next:** Phase 4 - Enhanced Chat Interface (Conversational data entry)
