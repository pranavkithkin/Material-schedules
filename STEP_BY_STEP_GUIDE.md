# Material Delivery Dashboard - Step-by-Step Implementation Guide

## 📋 Table of Contents
1. [Initial Setup](#initial-setup)
2. [Running the Application](#running-the-application)
3. [Testing Manual Mode](#testing-manual-mode)
4. [Setting Up AI Integration](#setting-up-ai-integration)
5. [Configuring n8n Workflows](#configuring-n8n-workflows)
6. [Testing AI Features](#testing-ai-features)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Initial Setup

### Step 1: Verify Python Installation

Open PowerShell and check Python version:

```powershell
python --version
```

You should see Python 3.9 or higher. If not installed, download from: https://www.python.org/downloads/

### Step 2: Navigate to Project Directory

```powershell
cd "C:\Users\PKP\Documents\PRANAV\Projects\With a clear picture\9. material delivery dashboard"
```

### Step 3: Create Virtual Environment

```powershell
python -m venv venv
```

### Step 4: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an error**, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Your prompt should now show `(venv)` at the beginning.

### Step 5: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This will take a few minutes. Wait for all packages to install.

### Step 6: Configure Environment Variables

```powershell
Copy-Item .env.example .env
notepad .env
```

In the opened file, update these values:

```
FLASK_SECRET_KEY=your-secret-key-here-make-it-long-and-random

# Leave these empty for now (we'll add them later)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# For email notifications (optional for now)
SMTP_USER=
SMTP_PASSWORD=
```

**Save and close the file.**

---

## 🏃 Running the Application

### Step 1: Initialize Database

**Option A - Empty Database:**
```powershell
python init_db.py
```

Type `yes` when prompted.

**Option B - With Sample Data (Recommended for testing):**
```powershell
python init_db.py --with-samples
```

Type `yes` when prompted.

### Step 2: Start the Application

```powershell
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Debug mode: on
```

### Step 3: Open Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

You should see the dashboard!

---

## ✅ Testing Manual Mode

The manual mode should work immediately without any AI APIs configured.

### Test 1: View Dashboard

- Navigate to http://localhost:5000
- You should see statistics cards with numbers
- Check for any error messages

### Test 2: Add a Material

1. Click on **Materials** in the navigation
2. Click **Add Material** button
3. Fill in the form:
   - Material Type: Select from dropdown (e.g., "DB")
   - Description: "24-way Distribution Board"
   - Approval Status: "Pending"
   - Quantity: 5
   - Unit: "units"
4. Click **Save**
5. Verify the material appears in the list

### Test 3: Create a Purchase Order

1. Go to **Purchase Orders**
2. Click **New PO**
3. Fill in:
   - Material: Select the material you just created
   - PO Ref: "PO-2025-TEST-001"
   - Supplier Name: "Test Supplier Ltd"
   - Total Amount: 10000
   - PO Status: "Released"
4. Click **Save**

### Test 4: Track Delivery

1. Go to **Deliveries**
2. Click **New Delivery**
3. Fill in:
   - Purchase Order: Select the PO you created
   - Expected Delivery Date: Pick a future date
   - Delivery Status: "Pending"
   - Ordered Quantity: 5
   - Unit: "units"
4. Click **Save**

### Test 5: Try the Chat

1. Click the blue **chat button** in the bottom-right corner
2. Type: "Show me all materials"
3. Wait for response
4. Try: "Which deliveries are pending?"

**If all these work, your manual mode is ready!** ✅

---

## 🤖 Setting Up AI Integration

### Step 1: Get Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to **API Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-...`)

### Step 2: Get OpenAI API Key (Optional)

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click **Create new secret key**
4. Copy the key (starts with `sk-...`)

### Step 3: Update .env File

```powershell
notepad .env
```

Add your keys:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
OPENAI_API_KEY=sk-your-actual-key-here
```

**Save and close.**

### Step 4: Restart the Application

In PowerShell where app is running:
1. Press `Ctrl+C` to stop
2. Run again: `python app.py`

### Step 5: Test AI Chat

1. Open chat
2. Ask a complex question: "What is the total value of all purchase orders?"
3. The AI should now provide better answers

---

## 🔄 Configuring n8n Workflows

### Step 1: Install n8n

**If you have Node.js installed:**
```powershell
npm install -g n8n
```

**If not, download Node.js first:** https://nodejs.org/

### Step 2: Start n8n

```powershell
n8n start
```

n8n will open in your browser at: http://localhost:5678

### Step 3: Create Credentials

1. In n8n, go to **Credentials**
2. Add **HTTP Header Auth** credential:
   - Name: "Material Dashboard API"
   - Name: "Authorization"
   - Value: `Bearer your-n8n-api-key` (use the key from .env)

3. Add **Claude API** credential (if using):
   - Select Anthropic
   - Enter your API key

### Step 4: Import Workflows

The workflow JSON files are ready in the `n8n_workflows/` folder, but you'll need to create them. Here's a simple starter workflow:

**Email Monitor Workflow (Basic):**

1. In n8n, click **New Workflow**
2. Add **Email Trigger** node:
   - Configure your email account
   - Set to check for new emails
3. Add **HTTP Request** node:
   - Method: POST
   - URL: `http://localhost:5000/api/ai-suggestions`
   - Body: JSON with extracted data
4. **Save** the workflow
5. **Activate** it

### Step 5: Test n8n Integration

1. Send a test email to your monitored inbox
2. Check if n8n processes it
3. Go to **AI Suggestions** in the dashboard
4. You should see a new suggestion!

---

## 🧪 Testing AI Features

### Test 1: AI Suggestions

**Manual Test:**
1. Go to **AI Suggestions** page
2. Check if there are any pending suggestions
3. Try approving or rejecting one

### Test 2: Confidence System

**High Confidence (Auto-Apply):**
- Suggestions with 90%+ confidence should auto-apply
- Look for records marked "AI Updated"

**Medium Confidence (Review):**
- Suggestions with 60-89% confidence should appear in review panel
- You can approve or reject them

### Test 3: Chat with AI

Try these queries:
- "Which materials are approved?"
- "Show me delayed deliveries"
- "What's the total PO value?"
- "When is the VRF System arriving?"

---

## 🔍 Troubleshooting

### Problem: "Module not found" errors

**Solution:**
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt
```

### Problem: Database errors

**Solution:**
```powershell
# Re-initialize database
python init_db.py --with-samples
```

### Problem: Port 5000 already in use

**Solution:**
```powershell
# Use a different port
# Edit app.py, change the last line to:
# app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
```

### Problem: AI not responding

**Check:**
1. API keys are correct in .env
2. You have internet connection
3. API keys have credit/quota
4. Restart the application

**Test API keys:**
```powershell
# Create a test script
notepad test_api.py
```

Add this code:
```python
import anthropic
client = anthropic.Anthropic(api_key="your-key-here")
message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print(message.content)
```

Run:
```powershell
python test_api.py
```

### Problem: n8n can't connect to Flask

**Solutions:**
1. Make sure Flask is running on port 5000
2. Use `http://localhost:5000` not `http://127.0.0.1:5000`
3. Check Windows Firewall settings
4. Verify N8N_API_KEY matches in both .env and n8n

### Problem: Chat window not appearing

**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Clear browser cache
4. Try a different browser

---

## 📊 Usage Tips

### For Daily Use:

1. **Start Application:**
   ```powershell
   cd "C:\Users\PKP\Documents\PRANAV\Projects\With a clear picture\9. material delivery dashboard"
   .\venv\Scripts\Activate.ps1
   python app.py
   ```

2. **Start n8n (if needed):**
   ```powershell
   # In a separate PowerShell window
   n8n start
   ```

3. **Access Dashboard:**
   - Open browser: http://localhost:5000

### For Data Entry:

- Always use the web interface for manual entry
- AI suggestions are just that - suggestions
- You have final approval on all AI updates
- Check the audit trail (created_by/updated_by fields)

### For AI Automation:

- n8n only needs to run when you want automation
- Manual mode always works independently
- High confidence suggestions auto-apply
- Review medium confidence suggestions daily

---

## 🎯 Next Steps

Now that everything is working:

1. **Customize Material Types** - Edit `config.py` to match your exact materials
2. **Import Real Data** - Add your actual POs and materials
3. **Set Up Email Notifications** - Configure SMTP settings in .env
4. **Create n8n Workflows** - Build workflows for your specific needs
5. **Train Your Team** - Show them how to use the dashboard

---

## 📞 Quick Reference

### Important URLs:
- Dashboard: http://localhost:5000
- n8n: http://localhost:5678

### Important Files:
- Main app: `app.py`
- Configuration: `config.py`, `.env`
- Database: `delivery_dashboard.db`

### Common Commands:
```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Start app
python app.py

# Reset database
python init_db.py --with-samples

# Install new package
pip install package-name
pip freeze > requirements.txt
```

---

**You're all set!** 🎉

If you need help, check the error messages carefully - they usually tell you exactly what's wrong.
