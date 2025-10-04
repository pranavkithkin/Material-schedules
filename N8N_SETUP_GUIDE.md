# n8n Workflow Setup Guide - Delivery Document Extraction

## Overview
This guide will help you set up the n8n workflow for extracting delivery order data using Claude API.

---

## Prerequisites

1. **n8n Installation**
   - Option A: Local (Docker)
   - Option B: n8n Cloud (https://n8n.cloud)

2. **API Keys Required**
   - Anthropic Claude API Key (get from: https://console.anthropic.com/)
   - Flask API Key (from your `.env` file: `API_KEY` value)

3. **URLs to Configure**
   - Flask App URL: `http://localhost:5000` (or your production URL)
   - n8n Webhook URL: `http://localhost:5678` (or your n8n instance URL)

---

## Step 1: Install n8n (Choose One Method)

### Method A: Docker (Recommended for Local Development)

```bash
# Pull n8n Docker image
docker pull n8nio/n8n

# Run n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Access n8n at: http://localhost:5678
```

### Method B: npm (Global Installation)

```bash
# Install n8n globally
npm install n8n -g

# Run n8n
n8n start

# Access n8n at: http://localhost:5678
```

### Method C: n8n Cloud (Production)

1. Go to https://n8n.cloud
2. Sign up for free account
3. Create new workflow
4. Note your instance URL (e.g., `https://your-org.app.n8n.cloud`)

---

## Step 2: Create Workflow in n8n

### A. Create New Workflow

1. Click **"New Workflow"** in n8n dashboard
2. Name it: **"Delivery Document Extraction"**
3. Save workflow

### B. Add Nodes (In Order)

---

### Node 1: Webhook Trigger

**Node Type:** `Webhook`  
**Configuration:**

- **HTTP Method:** POST
- **Path:** `extract-delivery`
- **Authentication:** None (internal call)
- **Response Mode:** Respond Immediately
- **Response Data:** JSON
- **Response Body:**
  ```json
  {
    "success": true,
    "message": "Extraction started"
  }
  ```

**Test URL:** `http://localhost:5678/webhook/extract-delivery`

**Expected Input from Flask:**
```json
{
  "delivery_id": 1,
  "file_id": 5,
  "file_path": "/full/path/to/delivery_order.pdf",
  "po_ref": "PO-2025-001"
}
```

---

### Node 2: Read Binary File

**Node Type:** `Read Binary File`  
**Configuration:**

- **File Path:** `{{ $json.body.file_path }}`
- **Property Name:** `data`

**Note:** This reads the PDF file and converts it to binary format.

---

### Node 3: Convert to Base64

**Node Type:** `Code` (JavaScript)  
**Configuration:**

```javascript
// Get binary data
const binaryData = items[0].binary.data;

// Convert to base64
const base64 = binaryData.toString('base64');

// Return as JSON
return [
  {
    json: {
      delivery_id: items[0].json.body.delivery_id,
      file_id: items[0].json.body.file_id,
      po_ref: items[0].json.body.po_ref,
      base64_pdf: base64,
      file_size: binaryData.length
    }
  }
];
```

---

### Node 4: Call Claude API

**Node Type:** `HTTP Request`  
**Configuration:**

- **Method:** POST
- **URL:** `https://api.anthropic.com/v1/messages`
- **Authentication:** Generic Credential Type
- **Generic Auth Type:** Header Auth
- **Credentials:**
  - Name: `x-api-key`
  - Value: `{{ $credentials.CLAUDE_API_KEY }}`

**Headers:**
```json
{
  "anthropic-version": "2023-06-01",
  "content-type": "application/json"
}
```

**Request Body:**
```json
{
  "model": "claude-3-sonnet-20240229",
  "max_tokens": 4096,
  "temperature": 0.1,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": "={{ $json.base64_pdf }}"
          }
        },
        {
          "type": "text",
          "text": "You are a document extraction specialist. Extract ALL information from this delivery order PDF and return it as JSON.\n\nExtract:\n1. Delivery order number\n2. Delivery date\n3. Supplier name\n4. Complete list of items with:\n   - Item description (exact text)\n   - Quantity delivered\n   - Unit of measurement\n   - Whether item was delivered (true/false)\n5. Any notes or remarks\n\nReturn ONLY valid JSON in this exact format:\n{\n  \"delivery_order_number\": \"DO-XXX\",\n  \"delivery_date\": \"YYYY-MM-DD\",\n  \"supplier\": \"Supplier Name\",\n  \"items\": [\n    {\n      \"item_description\": \"Item Name/Model\",\n      \"quantity\": 10,\n      \"unit\": \"pcs\",\n      \"delivered\": true\n    }\n  ],\n  \"total_items\": 2,\n  \"notes\": \"Any additional notes\"\n}\n\nBe thorough and extract ALL items listed in the document."
        }
      ]
    }
  ]
}
```

**Response Options:**
- **Response Format:** JSON
- **Extract:** Body

---

### Node 5: Parse Claude Response

**Node Type:** `Code` (JavaScript)  
**Configuration:**

```javascript
// Get Claude's response
const claudeResponse = items[0].json;

// Extract the JSON from Claude's response
let extractedData;
try {
  // Claude returns in content[0].text
  const contentText = claudeResponse.content[0].text;
  
  // Parse the JSON string
  extractedData = JSON.parse(contentText);
  
  // Calculate confidence based on Claude's model
  // Sonnet is high accuracy, so we start at 85%
  let confidence = 85;
  
  // Boost confidence if key fields are present
  if (extractedData.delivery_order_number) confidence += 5;
  if (extractedData.items && extractedData.items.length > 0) confidence += 5;
  if (extractedData.delivery_date) confidence += 5;
  
  // Return formatted data
  return [
    {
      json: {
        delivery_id: items[0].json.delivery_id || items[0].json.body.delivery_id,
        file_id: items[0].json.file_id || items[0].json.body.file_id,
        extraction_status: 'completed',
        extraction_confidence: Math.min(confidence, 100),
        extracted_data: extractedData,
        error_message: null,
        processed_at: new Date().toISOString()
      }
    }
  ];
  
} catch (error) {
  // Extraction failed
  return [
    {
      json: {
        delivery_id: items[0].json.delivery_id || items[0].json.body.delivery_id,
        file_id: items[0].json.file_id || items[0].json.body.file_id,
        extraction_status: 'failed',
        extraction_confidence: 0,
        extracted_data: null,
        error_message: error.message,
        processed_at: new Date().toISOString()
      }
    }
  ];
}
```

---

### Node 6: Send to Flask Webhook

**Node Type:** `HTTP Request`  
**Configuration:**

- **Method:** POST
- **URL:** `http://localhost:5000/api/n8n/delivery-extraction`
- **Authentication:** Generic Credential Type
- **Generic Auth Type:** Header Auth
- **Credentials:**
  - Name: `X-API-Key`
  - Value: `{{ $credentials.FLASK_API_KEY }}`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body:** Use Expression
```
={{ $json }}
```

**Response Options:**
- **Response Format:** JSON
- **Extract:** Body

---

### Node 7: Log Results (Optional)

**Node Type:** `Code` (JavaScript)  
**Configuration:**

```javascript
// Log the final result
console.log('Extraction completed for delivery:', items[0].json.delivery_id);
console.log('Status:', items[0].json.extraction_status);
console.log('Confidence:', items[0].json.extraction_confidence);
console.log('Items extracted:', items[0].json.extracted_data?.items?.length || 0);

return items;
```

---

## Step 3: Configure Credentials

### A. Add Claude API Credential

1. Go to **Settings** → **Credentials**
2. Click **"Add Credential"**
3. Select **"Header Auth"**
4. Name: `Claude API Key`
5. Add Header:
   - Name: `x-api-key`
   - Value: `your_anthropic_api_key_here`
6. Save

### B. Add Flask API Credential

1. Go to **Settings** → **Credentials**
2. Click **"Add Credential"**
3. Select **"Header Auth"**
4. Name: `Flask API Key`
5. Add Header:
   - Name: `X-API-Key`
   - Value: `your_flask_api_key_here` (from your `.env`)
6. Save

---

## Step 4: Connect Nodes

Connect nodes in this order:
```
Webhook → Read File → Convert Base64 → Claude API → Parse Response → Flask Webhook → Log
```

**Workflow Visual:**
```
┌──────────────┐
│   Webhook    │ (Receives file path from Flask)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Read File   │ (Loads PDF binary)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Convert Base64│ (Converts to base64 string)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Claude API  │ (Extracts data from PDF)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Parse Response│ (Formats extraction result)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Flask Webhook │ (Sends result back to Flask)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Log Results  │ (Logs to n8n console)
└──────────────┘
```

---

## Step 5: Test Workflow

### A. Get Webhook URL

1. Activate workflow (toggle switch in top-right)
2. Click on **Webhook node**
3. Copy the **Test URL** (e.g., `http://localhost:5678/webhook-test/extract-delivery`)
4. Copy the **Production URL** (e.g., `http://localhost:5678/webhook/extract-delivery`)

### B. Test with cURL

```bash
# Test webhook with sample data
curl -X POST http://localhost:5678/webhook-test/extract-delivery \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_id": 999,
    "file_id": 999,
    "file_path": "/full/path/to/test_delivery.pdf",
    "po_ref": "TEST-001"
  }'
```

### C. Check Execution

1. Go to **Executions** tab in n8n
2. View latest execution
3. Check each node's output
4. Verify data flows correctly

---

## Step 6: Update Flask Configuration

### A. Add Environment Variables

Edit your `.env` file:

```bash
# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/extract-delivery

# For production, use your n8n cloud URL:
# N8N_WEBHOOK_URL=https://your-org.app.n8n.cloud/webhook/extract-delivery
```

### B. Update Upload Route

Edit `routes/uploads.py` (around line 353):

**Find this commented code:**
```python
# TODO: Trigger n8n workflow here
# n8n_webhook_url = 'https://your-n8n-instance.com/webhook/extract-delivery'
```

**Replace with:**
```python
# Trigger n8n workflow for document extraction
import requests
import os

n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/extract-delivery')

try:
    response = requests.post(n8n_webhook_url, json={
        'delivery_id': delivery_id,
        'file_id': file_record.id,
        'file_path': os.path.abspath(file_path),
        'po_ref': delivery.purchase_order.po_ref if delivery.purchase_order else None
    }, timeout=5)
    
    if response.status_code != 200:
        print(f"Warning: n8n webhook returned status {response.status_code}")
except Exception as e:
    print(f"Warning: Failed to trigger n8n workflow: {str(e)}")
    # Don't fail the upload if n8n is unavailable
```

---

## Step 7: End-to-End Test

### A. Start All Services

```bash
# Terminal 1: Start n8n
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# Terminal 2: Start Flask
cd "9. material delivery dashboard"
python app.py
```

### B. Test Upload via UI

1. Open browser: `http://localhost:5000/deliveries`
2. Click **"Add Delivery"**
3. Fill in required fields
4. Upload a PDF delivery order
5. Click **"Validate & Save"**

### C. Monitor Extraction

**In n8n:**
- Watch **Executions** tab
- See workflow run in real-time
- Check each node's output

**In Flask Terminal:**
- See webhook trigger log
- See webhook receive log

**In Browser:**
- Extraction status updates to "Processing"
- After 10-20 seconds, updates to "Completed"
- Extracted items appear in list
- Delivery percentage auto-calculates

---

## Troubleshooting

### Issue 1: n8n Webhook Not Triggering

**Symptoms:** Upload succeeds but n8n never receives webhook

**Solutions:**
1. Check n8n is running: `curl http://localhost:5678`
2. Verify webhook URL in `.env` matches n8n URL
3. Check Flask terminal for error messages
4. Try manual trigger:
   ```bash
   curl -X POST http://localhost:5678/webhook/extract-delivery \
     -H "Content-Type: application/json" \
     -d '{"delivery_id":1,"file_id":1,"file_path":"/path/to/file.pdf"}'
   ```

---

### Issue 2: Claude API Returns Error

**Symptoms:** n8n execution fails at Claude API node

**Solutions:**
1. Verify API key in n8n credentials
2. Check Claude API quota: https://console.anthropic.com/
3. Verify PDF is valid and not corrupted
4. Check PDF size (max 10MB for Claude)
5. View Claude API error in n8n execution log

---

### Issue 3: Flask Webhook Not Receiving Data

**Symptoms:** n8n completes but Flask doesn't update delivery

**Solutions:**
1. Check Flask API key matches n8n credential
2. Verify Flask URL in n8n node (http://localhost:5000)
3. Check Flask terminal for webhook receive log
4. Test webhook manually:
   ```bash
   curl -X POST http://localhost:5000/api/n8n/delivery-extraction \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"delivery_id":1,"extraction_status":"completed",...}'
   ```

---

### Issue 4: Extraction Always Returns Low Confidence

**Symptoms:** Confidence scores always below 70%

**Solutions:**
1. Check PDF quality (scanned vs digital)
2. Improve Claude prompt with examples
3. Add OCR preprocessing if PDFs are scanned images
4. Adjust confidence calculation in Parse Response node

---

## Production Deployment

### For n8n Cloud:

1. **Export Workflow:**
   - Click **"..."** → **"Export Workflow"**
   - Save JSON file

2. **Import to Cloud:**
   - Go to n8n Cloud dashboard
   - Click **"Import Workflow"**
   - Upload JSON file

3. **Update URLs:**
   - Change Flask URL to production: `https://yourdomain.com`
   - Update credentials with production API keys

4. **Update Flask .env:**
   ```bash
   N8N_WEBHOOK_URL=https://your-org.app.n8n.cloud/webhook/extract-delivery
   ```

---

## Monitoring & Logs

### n8n Execution History

- View in **Executions** tab
- Filter by status (success/error)
- Download execution data for debugging

### Flask Logs

Add logging to track extractions:

```python
import logging

logger = logging.getLogger(__name__)

# In webhook endpoint:
logger.info(f"Received extraction for delivery {delivery_id}: {extraction_status}")
logger.info(f"Confidence: {extraction_confidence}%, Items: {extracted_item_count}")
```

---

## Cost Estimation

### Claude API Pricing (as of Jan 2025)

- **Model:** Claude 3 Sonnet
- **Input:** $3 per 1M tokens
- **Output:** $15 per 1M tokens

**Average per Extraction:**
- Input tokens: ~2,000 (PDF content)
- Output tokens: ~500 (JSON response)
- Cost: **~$0.013 per extraction**

**Monthly Estimates:**
- 100 deliveries: $1.30
- 500 deliveries: $6.50
- 1,000 deliveries: $13.00
- 5,000 deliveries: $65.00

---

## Next Steps

After setup is complete:

1. ✅ Test with 5-10 sample delivery orders
2. ✅ Fine-tune Claude prompt for better accuracy
3. ✅ Implement frontend polling (Phase 3)
4. ✅ Enhance chatbot with extracted data (Phase 4)
5. ✅ Monitor extraction accuracy and adjust

---

**Setup Time:** 1-2 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Basic API knowledge, n8n familiarity

**Support:** See SPRINT_2_PROGRESS.md for detailed implementation guide
