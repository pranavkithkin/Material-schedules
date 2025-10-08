# Phase 5: Dynamic Column Structure for LPO Generation

## Problem Statement

PKP Contracting LLC deals with various suppliers across different trades:
- **Steel suppliers**: Need MAKE, CODE, DESCRIPTION columns
- **Electrical suppliers**: May only have CODE, DESCRIPTION (no MAKE)
- **Service providers**: May only have DESCRIPTION (no MAKE, no CODE)
- **Plumbing suppliers**: May use BRAND instead of MAKE

**Forcing a standard column structure would:**
- Create empty columns in LPOs (unprofessional)
- Make verification harder (LPO doesn't match quote)
- Limit flexibility for different material types

## Solution: Mirror the Supplier's Quote Structure

The LPO will **dynamically adapt** to match exactly what columns the supplier provided.

### Architecture

```
┌─────────────────┐
│ Supplier Quote  │
│ (Any Structure) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ GPT-4 AI Extraction             │
│ - Identifies column names       │
│ - Extracts all items            │
│ - Returns structured JSON       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Database Storage                │
│ column_structure: ["MAKE",      │
│   "DESCRIPTION", "UNIT", ...]   │
│ items: [{...}, {...}]           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Dynamic Template Rendering      │
│ - Loops through columns         │
│ - Renders only columns present  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ LPO PDF (Matches Quote Exactly) │
└─────────────────────────────────┘
```

## Examples

### Example 1: Steel Supplier (Full Columns)

**Input Quote:**
```
SN | MAKE     | CODE    | DESCRIPTION      | UNIT | QTY | RATE  | AMOUNT
1  | Samsung  | LED-100 | LED Light 10W    | Nos  | 50  | 25.00 | 1250.00
2  | Philips  | BUL-200 | Bulb 20W         | Nos  | 100 | 15.00 | 1500.00
```

**Stored in Database:**
```json
{
  "column_structure": ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
  "items": [
    {
      "number": 1,
      "make": "Samsung",
      "code": "LED-100",
      "description": "LED Light 10W",
      "unit": "Nos",
      "quantity": 50,
      "unit_price": 25.00,
      "total_amount": 1250.00
    }
  ]
}
```

**Generated LPO:**
```
Item | MAKE     | CODE    | DESCRIPTION      | UNIT | QTY | RATE  | AMOUNT (AED)
1    | Samsung  | LED-100 | LED Light 10W    | Nos  | 50  | 25.00 | 1,250.00
2    | Philips  | BUL-200 | Bulb 20W         | Nos  | 100 | 15.00 | 1,500.00
```

### Example 2: Electrical Supplier (No MAKE Column)

**Input Quote:**
```
SN | CODE    | DESCRIPTION            | UNIT | QTY | RATE  | AMOUNT
1  | CAB-500 | 2.5mm Cable 100m Roll  | Roll | 10  | 85.00 | 850.00
2  | CAB-600 | 4.0mm Cable 100m Roll  | Roll | 5   | 120.00| 600.00
```

**Stored in Database:**
```json
{
  "column_structure": ["CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
  "items": [
    {
      "number": 1,
      "code": "CAB-500",
      "description": "2.5mm Cable 100m Roll",
      "unit": "Roll",
      "quantity": 10,
      "unit_price": 85.00,
      "total_amount": 850.00
    }
  ]
}
```

**Generated LPO:**
```
Item | CODE    | DESCRIPTION            | UNIT | QTY | RATE   | AMOUNT (AED)
1    | CAB-500 | 2.5mm Cable 100m Roll  | Roll | 10  | 85.00  | 850.00
2    | CAB-600 | 4.0mm Cable 100m Roll  | Roll | 5   | 120.00 | 600.00
```
*(Note: No MAKE column - cleaner, matches quote exactly)*

### Example 3: Service Provider (Minimal Columns)

**Input Quote:**
```
SN | DESCRIPTION                    | UNIT  | QTY | RATE    | AMOUNT
1  | Labor - Electrical Installation| Day   | 5   | 450.00  | 2250.00
2  | Labor - Plumbing Installation  | Day   | 3   | 400.00  | 1200.00
```

**Stored in Database:**
```json
{
  "column_structure": ["DESCRIPTION", "UNIT", "QTY", "RATE"],
  "items": [
    {
      "number": 1,
      "description": "Labor - Electrical Installation",
      "unit": "Day",
      "quantity": 5,
      "unit_price": 450.00,
      "total_amount": 2250.00
    }
  ]
}
```

**Generated LPO:**
```
Item | DESCRIPTION                    | UNIT  | QTY | RATE   | AMOUNT (AED)
1    | Labor - Electrical Installation| Day   | 5   | 450.00 | 2,250.00
2    | Labor - Plumbing Installation  | Day   | 3   | 400.00 | 1,200.00
```
*(Note: No MAKE, no CODE - just service description)*

### Example 4: Plumbing Supplier (BRAND instead of MAKE)

**Input Quote:**
```
SN | BRAND    | MODEL   | DESCRIPTION          | UNIT | QTY | RATE  | AMOUNT
1  | Grohe    | 32665   | Basin Mixer Chrome   | Nos  | 10  | 185.00| 1850.00
2  | Kohler   | K-8211  | Kitchen Sink Single  | Nos  | 8   | 320.00| 2560.00
```

**Stored in Database:**
```json
{
  "column_structure": ["BRAND", "MODEL", "DESCRIPTION", "UNIT", "QTY", "RATE"],
  "items": [
    {
      "number": 1,
      "brand": "Grohe",
      "model": "32665",
      "description": "Basin Mixer Chrome",
      "unit": "Nos",
      "quantity": 10,
      "unit_price": 185.00,
      "total_amount": 1850.00
    }
  ]
}
```

**Generated LPO:**
```
Item | BRAND    | MODEL   | DESCRIPTION          | UNIT | QTY | RATE   | AMOUNT (AED)
1    | Grohe    | 32665   | Basin Mixer Chrome   | Nos  | 10  | 185.00 | 1,850.00
2    | Kohler   | K-8211  | Kitchen Sink Single  | Nos  | 8   | 320.00 | 2,560.00
```
*(Note: Uses BRAND and MODEL instead of MAKE and CODE)*

## Implementation Details

### 1. Database Model (models/lpo.py)

```python
class LPO(db.Model):
    __tablename__ = 'lpos'
    
    id = db.Column(db.Integer, primary_key=True)
    lpo_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Dynamic column structure
    column_structure = db.Column(db.JSON)  
    # Example: ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"]
    # or: ["BRAND", "MODEL", "DESCRIPTION", "UNIT", "QTY", "RATE"]
    # or: ["CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"]
    # or: ["DESCRIPTION", "UNIT", "QTY", "RATE"]
    
    items = db.Column(db.JSON)  # Each item has keys matching column_structure
    
    # ... other fields (supplier, project, totals, etc)
```

### 2. AI Extraction (services/lpo_extraction.py)

```python
def extract_items_from_quote(quote_pdf_path):
    """Extract items and column structure from supplier quote"""
    
    # Read PDF text
    quote_text = extract_text_from_pdf(quote_pdf_path)
    
    prompt = f"""
    Analyze this supplier quotation and extract:
    
    1. COLUMN NAMES: Identify all column headers in the items table
       Common names: SN, MAKE, BRAND, CODE, MODEL, DESCRIPTION, UNIT, QTY, QUANTITY, RATE, PRICE, AMOUNT
       Return exactly as they appear in the quote
    
    2. ITEM DATA: Extract all rows with their data
    
    Return JSON format:
    {{
        "column_structure": ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
        "items": [
            {{
                "make": "Samsung",
                "code": "LED-100",
                "description": "LED Light 10W",
                "unit": "Nos",
                "qty": "50",
                "rate": "25.00"
            }}
        ]
    }}
    
    IMPORTANT: 
    - Include ONLY columns that exist in the quote
    - Use lowercase keys in items (make, code, description, etc)
    - Do not add AMOUNT column (will be calculated)
    
    Quote text:
    {quote_text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    extracted = json.loads(response.choices[0].message.content)
    
    # Calculate amounts for each item
    for item in extracted['items']:
        qty = float(item.get('qty') or item.get('quantity') or 0)
        rate = float(item.get('rate') or item.get('unit_price') or item.get('price') or 0)
        item['total_amount'] = qty * rate
    
    return extracted
```

### 3. Template Rendering (templates/lpo_template.html)

```html
<table class="items-table">
    <thead>
        <tr>
            <th class="col-item">Item</th>
            {% for col in column_structure %}
                {% if col.upper() not in ['ITEM', 'S.N', 'SN', 'AMOUNT', 'AMOUNT (AED)'] %}
                    <th>{{ col }}</th>
                {% endif %}
            {% endfor %}
            <th class="col-amount">AMOUNT (AED)</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr>
            <td class="col-item">{{ item.number or loop.index }}</td>
            {% for col in column_structure %}
                {% if col.upper() not in ['ITEM', 'S.N', 'SN', 'AMOUNT', 'AMOUNT (AED)'] %}
                    <td>{{ item.get(col.lower().replace(' ', '_')) or '-' }}</td>
                {% endif %}
            {% endfor %}
            <td class="col-amount">{{ "{:,.2f}".format(item.total_amount) }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### 4. Review UI (templates/lpo_review.html)

```html
<h3>Detected Structure</h3>
<div class="column-preview">
    <strong>Columns Found:</strong>
    {% for col in column_structure %}
        <span class="badge">{{ col }}</span>
    {% endfor %}
</div>

<div class="preview-table">
    <p>Preview of extracted items (first 5):</p>
    <!-- Shows dynamic table like final LPO -->
</div>

<div class="actions">
    <button onclick="acceptExtraction()">✓ Accept & Generate LPO</button>
    <button onclick="editColumns()">✏️ Edit Column Mapping</button>
    <button onclick="reExtract()">🔄 Re-extract from Quote</button>
</div>
```

## Benefits

1. **Flexible**: Works with any supplier quote structure
2. **Professional**: LPO matches quote exactly (easy for supplier to verify)
3. **Accurate**: No forced columns that don't exist in quote
4. **Scalable**: Handles steel, electrical, plumbing, services, HVAC, etc.
5. **Clean**: No empty columns or placeholder values
6. **Future-proof**: New column types automatically supported

## Edge Cases Handled

1. **Column name variations**: MAKE vs BRAND vs MANUFACTURER
2. **Missing columns**: Some quotes may not have make/code
3. **Extra columns**: Some quotes may have warranty, origin, certification
4. **Unit variations**: Nos vs Pcs vs Each vs Mtrs vs Roll
5. **Price columns**: RATE vs UNIT PRICE vs PRICE vs RATE/AED

## Testing Strategy

1. Test with actual supplier quotes from different trades
2. Verify column detection accuracy
3. Ensure PDF rendering adapts column widths properly
4. Test edge cases (very long descriptions, many columns, few columns)
5. Validate totals calculation works with any structure

---

**Status**: Template updated ✓  
**Next**: Implement database model and AI extraction service
