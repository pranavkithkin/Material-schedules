# Automated UI Testing Guide

## 🎯 Overview

This guide covers **automated browser testing** using Selenium WebDriver. These tests simulate a real user interacting with the application through a browser, clicking buttons, filling forms, and verifying the UI works correctly.

---

## 🆚 Automated vs Manual Testing

### Automated UI Tests (Selenium)
✅ **Pros:**
- Tests the actual browser UI
- Simulates real user interactions
- Catches frontend JavaScript errors
- Verifies form submissions work
- Tests complete click-through workflows
- Can run in CI/CD pipelines
- Generates detailed HTML reports

❌ **Cons:**
- Requires browser drivers (Chrome/Firefox)
- Slower than unit tests (5-10 minutes)
- Can be flaky with timing issues
- Needs the Flask app running first

### Backend Unit Tests (pytest)
✅ **Pros:**
- Very fast (runs in seconds)
- Tests database logic directly
- No browser needed
- More stable and reliable
- Great for TDD

❌ **Cons:**
- Doesn't test actual UI
- Won't catch frontend bugs
- Doesn't test JavaScript
- Misses form validation issues

---

## 🚀 Quick Start

### 1. Install Dependencies

**In WSL:**
```bash
cd "/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard"
source venv/bin/activate
pip install -r tests/requirements-ui-tests.txt
```

This installs:
- `selenium` - Browser automation
- `pytest` - Test framework
- `pytest-html` - HTML test reports
- `webdriver-manager` - Auto-downloads browser drivers

### 2. Start the Flask Application

**In a separate WSL terminal:**
```bash
cd "/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard"
source venv/bin/activate
python app.py
```

Keep this running while tests execute.

### 3. Run the UI Tests

**Method 1: Using the test runner (recommended)**
```bash
wsl bash tests/run_ui_tests.sh
```

**Method 2: Direct pytest**
```bash
pytest tests/test_ui_automation.py -v
```

**Method 3: With HTML report**
```bash
pytest tests/test_ui_automation.py -v --html=tests/ui_test_report.html --self-contained-html
```

---

## 📋 Test Coverage

### What Gets Tested:

#### ✅ Material Management UI
- **Test 01:** Create new material through form
- **Test 02:** Update material approval status
- **Test 03:** Create material revision with linking

#### ✅ Purchase Order UI
- **Test 04:** Create PO with all fields
- **Test 05:** Release purchase order workflow

#### ✅ Payment Management UI
- **Test 06:** Create advance payment (50%)
- **Test 07:** Create balance payment (50%)
- Verifies payment terms auto-fill from PO

#### ✅ Delivery Tracking UI
- **Test 08:** Create pending delivery
- **Test 09:** Update to partial delivery (65%)
- **Test 10:** Complete delivery (100%)

#### ✅ End-to-End Workflow
- **Test 11:** Verify all pages load correctly
- Check data appears in tables
- Verify relationships work
- Confirm complete workflow

---

## 🎬 How It Works

### Test Execution Flow:

```
1. Browser Setup
   ├── Launch Chrome in headless mode
   ├── Set window size to 1920x1080
   └── Configure implicit wait (10 seconds)

2. For Each Test:
   ├── Navigate to page (e.g., /materials)
   ├── Wait for page to load
   ├── Click button (e.g., "Add Material")
   ├── Wait for modal to appear
   ├── Fill form fields
   ├── Click "Save" button
   ├── Wait for modal to close
   └── Verify data appears in table

3. Cleanup
   └── Close browser
```

### Key Features:

- **Headless Mode:** Tests run without opening visible browser windows
- **Smart Waits:** Automatically waits for elements to appear
- **Error Screenshots:** Captures screenshots on failures (can be enabled)
- **Detailed Logging:** Shows every action in the output
- **HTML Reports:** Beautiful reports with pass/fail details

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. Flask App Not Running
```
❌ ERROR: Flask application is not running!
```

**Solution:** Start Flask in another terminal:
```bash
python app.py
```

#### 2. Selenium Not Installed
```
ModuleNotFoundError: No module named 'selenium'
```

**Solution:** Install dependencies:
```bash
pip install -r tests/requirements-ui-tests.txt
```

#### 3. ChromeDriver Issues
```
WebDriverException: unknown error: cannot find Chrome binary
```

**Solution:** Tests use Chrome in headless mode. Install Chrome or use Firefox:
```bash
# In test_ui_automation.py, change to Firefox:
driver = webdriver.Firefox(options=options)
```

#### 4. Element Not Found
```
NoSuchElementException: Unable to locate element: {"method":"css selector","selector":"#materialModal"}
```

**Solution:** 
- Check if the element ID matches your HTML template
- Increase timeout: `TIMEOUT = 20` (line 17 in test_ui_automation.py)
- Check if JavaScript is loading correctly

#### 5. Tests Are Slow
```
Tests taking 10+ minutes
```

**Solution:**
- Normal for UI tests (they're slower than unit tests)
- Run specific test: `pytest tests/test_ui_automation.py::TestMaterialUI::test_01_create_material -v`
- Use backend unit tests for faster feedback

---

## 📊 Reading Test Results

### Terminal Output:

```
tests/test_ui_automation.py::TestMaterialUI::test_01_create_material PASSED
✅ Material created successfully

tests/test_ui_automation.py::TestMaterialUI::test_02_update_material_status PASSED
✅ Material status updated successfully

tests/test_ui_automation.py::TestPurchaseOrderUI::test_04_create_purchase_order PASSED
✅ Purchase Order created successfully

================= 11 passed in 142.33s =================
```

### HTML Report:

Open `tests/ui_test_report.html` in browser:
- ✅ Green = Passed
- ❌ Red = Failed
- ⚠️ Yellow = Skipped
- Full error traces for failures
- Execution time for each test

---

## 🎯 Best Practices

### When to Run UI Tests:

✅ **Good Times:**
- After making frontend changes
- Before deploying to production
- When testing complete workflows
- To verify forms work end-to-end
- After updating templates

❌ **Not Needed:**
- During active development (too slow)
- For backend-only changes
- When unit tests already caught the bug

### Recommended Testing Strategy:

```
1. Development Phase:
   └── Use backend unit tests (fast feedback)
   
2. Feature Complete:
   └── Run UI automation tests (catch frontend bugs)
   
3. Before Deployment:
   ├── Run all backend tests
   ├── Run all UI tests
   └── Manual smoke test
```

---

## 🔧 Customizing Tests

### Change Browser:

```python
# In test_ui_automation.py, line ~23:

# Use Firefox instead of Chrome:
driver = webdriver.Firefox(options=options)

# Show browser window (not headless):
# Remove this line:
options.add_argument('--headless')
```

### Add New Test:

```python
def test_12_custom_workflow(self, browser):
    """Test custom functionality"""
    browser.get(f"{BASE_URL}/your_page")
    
    # Your test steps here
    element = browser.find_element(By.ID, "your_element")
    element.click()
    
    # Assertions
    assert "Expected Text" in browser.page_source
```

### Take Screenshots:

```python
# Add after any step:
browser.save_screenshot("tests/screenshots/step1.png")
```

---

## 📈 Integration with CI/CD

### GitHub Actions Example:

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  ui-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-ui-tests.txt
      
      - name: Start Flask app
        run: |
          python app.py &
          sleep 5
      
      - name: Run UI tests
        run: |
          pytest tests/test_ui_automation.py -v --html=report.html
      
      - name: Upload test report
        uses: actions/upload-artifact@v3
        with:
          name: ui-test-report
          path: report.html
```

---

## ✅ Success Criteria

### All Tests Should Pass:

```
✅ TestMaterialUI
   ├── test_01_create_material
   ├── test_02_update_material_status
   └── test_03_create_material_revision

✅ TestPurchaseOrderUI
   ├── test_04_create_purchase_order
   └── test_05_release_purchase_order

✅ TestPaymentUI
   ├── test_06_create_advance_payment
   └── test_07_create_balance_payment

✅ TestDeliveryUI
   ├── test_08_create_pending_delivery
   ├── test_09_update_to_partial_delivery
   └── test_10_complete_delivery

✅ TestCompleteWorkflow
   └── test_11_verify_complete_workflow
```

### Expected Output:

```
====================================================
🎉 COMPLETE WORKFLOW VERIFIED SUCCESSFULLY!
====================================================
✅ 2+ Materials created
✅ 1+ Purchase Orders created
✅ 2+ Payments recorded
✅ 1+ Deliveries tracked
====================================================
```

---

## 🚦 Next Steps

**After all UI tests pass:**

1. ✅ Backend unit tests passed
2. ✅ UI automation tests passed
3. 🎯 **Manual smoke test** (quick visual check)
4. 📝 Document any edge cases
5. 🚀 **Proceed to Phase 3: AI Features**

---

## 📚 Additional Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)
- [WebDriver API](https://www.selenium.dev/selenium/docs/api/py/api.html)
- [pytest-html Plugin](https://pytest-html.readthedocs.io/)

---

**Remember:** UI tests complement unit tests, they don't replace them! Use both for comprehensive coverage. 🎯
