# 🔐 API Security & n8n Integration Guide

## Overview
This document explains how to authenticate with the Material Delivery Dashboard API for n8n integration.

---

## 🔑 Authentication

All n8n webhook endpoints (except `/health`) require API key authentication.

### Setup API Key

1. **Generate a secure API key:**
   ```bash
   python scripts/generate_api_key.py
   ```

2. **Add to your `.env` file:**
   ```bash
   N8N_API_KEY=your-generated-key-here
   ```

3. **Restart Flask application:**
   ```bash
   python app.py
   ```

### Using the API Key

Include the API key in request headers:

```http
X-API-Key: your-generated-key-here
```

**Example with curl:**
```bash
curl -X GET http://localhost:5000/api/n8n/stats \
  -H "X-API-Key: your-api-key-here"
```

**Example with Python:**
```python
import requests

headers = {"X-API-Key": "your-api-key-here"}
response = requests.get(
    "http://localhost:5000/api/n8n/stats",
    headers=headers
)
```

---

## 📡 API Endpoints

### Health Check
**No authentication required**

```http
GET /api/n8n/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Material Delivery Dashboard API",
  "timestamp": "2025-10-04T10:30:00"
}
```

---

### Create AI Suggestion
**Authentication required**

```http
POST /api/n8n/ai-suggestion
Content-Type: application/json
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
  "material_id": 1,
  "source": "email",
  "suggestion_type": "purchase_order",
  "extracted_data": {
    "po_number": "PO-2024-001",
    "supplier": "ABC Materials",
    "amount": 50000.00,
    "currency": "AED"
  },
  "confidence_score": 85.5,
  "ai_reasoning": "Extracted from email attachment...",
  "metadata": {
    "email_from": "supplier@example.com",
    "email_subject": "PO Confirmation",
    "file_name": "PO-2024-001.pdf"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "AI suggestion created successfully",
  "suggestion_id": 123,
  "action": "manual_review",
  "confidence_score": 85.5,
  "requires_review": true
}
```

**Actions:**
- `auto_approve`: Confidence ≥ 90%, can be auto-approved
- `manual_review`: Confidence < 90%, requires human review

---

### Store Conversation
**Authentication required**

```http
POST /api/n8n/conversation
Content-Type: application/json
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
  "conversation_id": "conv-123",
  "user_message": "When is cement delivery?",
  "ai_response": "The cement delivery is scheduled for Oct 5, 2025",
  "context": {
    "material_id": 5,
    "query_type": "delivery_status"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Conversation stored",
  "conversation_id": "conv-123"
}
```

---

### Handle Clarification
**Authentication required**

```http
POST /api/n8n/clarification
Content-Type: application/json
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
  "suggestion_id": 123,
  "clarifications": {
    "supplier_email": "supplier@example.com",
    "delivery_date": "2025-10-15"
  },
  "ready_to_create": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Clarifications applied",
  "suggestion_id": 123,
  "updated_data": {
    "po_number": "PO-2024-001",
    "supplier": "ABC Materials",
    "supplier_email": "supplier@example.com",
    "delivery_date": "2025-10-15",
    "amount": 50000.00
  },
  "ready_to_create": true
}
```

---

### File Processing Notification
**Authentication required**

```http
POST /api/n8n/file-processed
Content-Type: application/json
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
  "file_id": 123,
  "status": "completed",
  "processing_result": {
    "suggestions_created": 2,
    "confidence_avg": 87.5
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "File processing notification received",
  "file_id": 123
}
```

---

### Get Pending Reviews
**Authentication required**

```http
GET /api/n8n/pending-reviews?confidence_max=90&limit=50
X-API-Key: your-api-key-here
```

**Query Parameters:**
- `confidence_max` (optional): Maximum confidence score, default: 90
- `limit` (optional): Number of results, default: 50

**Response (200 OK):**
```json
{
  "success": true,
  "count": 5,
  "pending_reviews": [
    {
      "id": 123,
      "material_id": 1,
      "source": "email",
      "suggestion_type": "purchase_order",
      "confidence_score": 85.5,
      "status": "pending",
      "created_date": "2025-10-04T10:00:00"
    }
  ]
}
```

---

### Get Statistics
**Authentication required**

```http
GET /api/n8n/stats
X-API-Key: your-api-key-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "statistics": {
    "total_suggestions": 150,
    "pending_review": 12,
    "approved": 125,
    "average_confidence": 87.35,
    "last_24h": 8
  },
  "timestamp": "2025-10-04T10:30:00"
}
```

---

## 🔄 n8n Integration

### Setting up n8n HTTP Request Node

1. **Add HTTP Request node** in your n8n workflow

2. **Configure authentication:**
   - Method: GET/POST (depends on endpoint)
   - URL: `http://your-server:5000/api/n8n/endpoint`
   - Authentication: None (use headers instead)
   
3. **Add header:**
   - **Name:** `X-API-Key`
   - **Value:** `{{$env.N8N_API_KEY}}` (or paste your key)

4. **Set content type** (for POST requests):
   - **Name:** `Content-Type`
   - **Value:** `application/json`

### Example n8n Workflow: Email Monitor

```
[Email Trigger] → [Extract Attachment] → [HTTP Request]
                                           ↓
                                    POST /api/n8n/ai-suggestion
                                    Headers:
                                      X-API-Key: your-key
                                      Content-Type: application/json
                                    Body:
                                      {extracted_data}
```

---

## 🔒 Error Responses

### 401 Unauthorized
Missing API key:
```json
{
  "error": "Missing API key",
  "message": "API key must be provided in X-API-Key header"
}
```

### 403 Forbidden
Invalid API key:
```json
{
  "error": "Invalid API key",
  "message": "The provided API key is invalid"
}
```

### 400 Bad Request
Invalid request data:
```json
{
  "error": "Missing required fields",
  "missing_fields": ["source", "extracted_data"]
}
```

### 500 Internal Server Error
Server error:
```json
{
  "error": "Failed to create AI suggestion",
  "message": "Database connection error"
}
```

---

## ✅ Testing

### Quick Test

1. **Generate API key:**
   ```bash
   python scripts/generate_api_key.py
   ```

2. **Add to `.env` file**

3. **Start Flask:**
   ```bash
   ### Step 1: Generate API Key

**Option A - Quick:**
```bash
wsl bash -c "cd '/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard' && source venv/bin/activate && python scripts/quick_keygen.py"
```

**Option B - Detailed:**
```bash
wsl bash -c "cd '/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard' && source venv/bin/activate && python scripts/generate_api_key.py"
```
   ```

4. **Run test suite:**
   ```bash
   python tests/test_api_auth.py
   ```

### Manual Testing with curl

**Health check (no auth):**
```bash
curl http://localhost:5000/api/n8n/health
```

**Stats with auth:**
```bash
curl -H "X-API-Key: your-key-here" http://localhost:5000/api/n8n/stats
```

**Create suggestion:**
```bash
curl -X POST http://localhost:5000/api/n8n/ai-suggestion \
  -H "X-API-Key: your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "suggestion_type": "purchase_order",
    "extracted_data": {"test": "data"},
    "confidence_score": 85
  }'
```

---

## 🔐 Security Best Practices

1. **Keep API keys secret**
   - Never commit API keys to Git
   - Use environment variables
   - Rotate keys periodically

2. **Use HTTPS in production**
   - Render automatically provides HTTPS
   - Never send API keys over HTTP

3. **Monitor API usage**
   - Check `/api/n8n/stats` regularly
   - Set up alerts for unauthorized attempts

4. **Rate limiting** (TODO)
   - Consider adding rate limiting for production
   - Use Flask-Limiter package

---

## 📝 Next Steps

After setting up authentication:

1. ✅ **Phase 2.1 Complete** - API Security
2. ⏳ **Phase 2.2** - Build n8n Email Monitor workflow
3. ⏳ **Phase 2.3** - AI Agent for document processing
4. ⏳ **Phase 2.4** - Automated reminders and reports

---

## 🆘 Troubleshooting

**Problem:** "Missing API key" error
- **Solution:** Ensure `X-API-Key` header is included in request

**Problem:** "Invalid API key" error
- **Solution:** Verify API key in `.env` matches the one you're using

**Problem:** "API key not configured on server"
- **Solution:** Check `.env` file has `N8N_API_KEY=...` and restart Flask

**Problem:** n8n can't connect
- **Solution:** Check firewall, ensure Flask is running, verify URL is correct

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Run `python tests/test_api_auth.py` to diagnose issues
3. Review Flask logs for error messages
4. Verify `.env` configuration
