"""
AI Service for extracting data from documents and emails
Uses Claude and OpenAI APIs
"""

import os
import json
from config import Config

# Import AI libraries conditionally
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIService:
    """Service for AI-powered data extraction"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize Claude if available
        if ANTHROPIC_AVAILABLE and Config.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.openai_client = openai
    
    def extract_po_from_text(self, text, model='claude'):
        """Extract PO information from text"""
        prompt = self._load_prompt('po_extraction.txt')
        prompt = prompt.replace('{TEXT}', text)
        
        if model == 'claude' and self.anthropic_client:
            return self._extract_with_claude(prompt)
        elif model == 'openai' and self.openai_client:
            return self._extract_with_openai(prompt)
        else:
            return self._mock_extraction(text, 'purchase_order')
    
    def extract_invoice_from_text(self, text, model='claude'):
        """Extract invoice/payment information from text"""
        prompt = self._load_prompt('invoice_extraction.txt')
        prompt = prompt.replace('{TEXT}', text)
        
        if model == 'claude' and self.anthropic_client:
            return self._extract_with_claude(prompt)
        elif model == 'openai' and self.openai_client:
            return self._extract_with_openai(prompt)
        else:
            return self._mock_extraction(text, 'payment')
    
    def extract_delivery_from_text(self, text, model='claude'):
        """Extract delivery information from text"""
        prompt = self._load_prompt('delivery_extraction.txt')
        prompt = prompt.replace('{TEXT}', text)
        
        if model == 'claude' and self.anthropic_client:
            return self._extract_with_claude(prompt)
        elif model == 'openai' and self.openai_client:
            return self._extract_with_openai(prompt)
        else:
            return self._mock_extraction(text, 'delivery')
    
    def _extract_with_claude(self, prompt):
        """Extract data using Claude API"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            content = response.content[0].text
            return self._parse_ai_response(content)
        except Exception as e:
            print(f"Claude API error: {e}")
            return None
    
    def _extract_with_openai(self, prompt):
        """Extract data using OpenAI API"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Extract structured data from the given text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def _parse_ai_response(self, response_text):
        """Parse AI response and extract JSON data"""
        try:
            # Try to find JSON in the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                data = json.loads(json_str)
                return data
            else:
                return None
        except json.JSONDecodeError:
            print("Failed to parse AI response as JSON")
            return None
    
    def _load_prompt(self, filename):
        """Load prompt template from file"""
        prompt_path = os.path.join('prompts', filename)
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return default prompt if file doesn't exist
            return self._get_default_prompt(filename)
    
    def _get_default_prompt(self, filename):
        """Get default prompt if file doesn't exist"""
        if 'po_extraction' in filename:
            return """
Extract purchase order information from the following text. Return a JSON object with these fields:
- po_ref: PO reference number
- quote_ref: Quote reference
- supplier_name: Supplier company name
- supplier_contact: Phone number
- supplier_email: Email address
- total_amount: Total amount (number only)
- currency: Currency code
- po_date: Date (YYYY-MM-DD format)
- confidence_score: Your confidence in this extraction (0-100)
- missing_fields: Array of fields you couldn't extract
- reasoning: Brief explanation of your extraction

Text to extract from:
{TEXT}
"""
        elif 'invoice_extraction' in filename:
            return """
Extract payment/invoice information from the following text. Return a JSON object with these fields:
- invoice_ref: Invoice reference
- payment_ref: Payment reference
- total_amount: Total amount
- paid_amount: Amount paid
- payment_date: Payment date (YYYY-MM-DD)
- payment_method: Payment method
- confidence_score: Your confidence (0-100)
- missing_fields: Array of missing fields
- reasoning: Explanation

Text:
{TEXT}
"""
        elif 'delivery_extraction' in filename:
            return """
Extract delivery information from the following text. Return a JSON object with these fields:
- tracking_number: Tracking number
- carrier: Carrier/shipping company
- delivery_status: Status (Pending, In Transit, Delivered, etc.)
- expected_delivery_date: Expected date (YYYY-MM-DD)
- actual_delivery_date: Actual date if delivered
- confidence_score: Your confidence (0-100)
- missing_fields: Array of missing fields
- reasoning: Explanation

Text:
{TEXT}
"""
        else:
            return "Extract information from: {TEXT}"
    
    def _mock_extraction(self, text, extraction_type):
        """Mock extraction for testing when API is not available"""
        return {
            'data': {},
            'confidence_score': 50,
            'missing_fields': ['all'],
            'reasoning': 'Mock extraction - AI API not configured',
            'error': 'AI API not available'
        }
    
    def calculate_confidence(self, extracted_data):
        """Calculate confidence score based on extracted data completeness"""
        if not extracted_data or 'data' not in extracted_data:
            return 0
        
        # If AI already provided a confidence score, use it
        if 'confidence_score' in extracted_data:
            return extracted_data['confidence_score']
        
        # Otherwise calculate based on completeness
        data = extracted_data['data']
        missing = extracted_data.get('missing_fields', [])
        
        if not data:
            return 0
        
        total_fields = len(data) + len(missing)
        filled_fields = len(data)
        
        if total_fields == 0:
            return 0
        
        confidence = (filled_fields / total_fields) * 100
        return round(confidence, 2)
