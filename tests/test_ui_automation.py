"""
Automated UI Testing Suite for Material Delivery Dashboard
Tests the complete user interface workflow automatically using Selenium
"""

import pytest
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10  # seconds


@pytest.fixture(scope="module")
def browser():
    """Initialize Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(TIMEOUT)
    
    yield driver
    
    driver.quit()


class TestMaterialUI:
    """Test Material Management UI"""
    
    def test_01_create_material(self, browser):
        """Test creating a new material through UI"""
        browser.get(f"{BASE_URL}/materials")
        
        # Wait for page to load
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Click Add Material button
        add_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Add Material')]")
        add_btn.click()
        
        # Wait for modal to appear
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "materialModal"))
        )
        
        # Fill in the form
        browser.find_element(By.ID, "material_type").send_keys("PVC Conduits & Accessories")
        browser.find_element(By.ID, "description").send_keys("20mm PVC conduit pipes - standard grade")
        
        # Select approval status
        status_select = Select(browser.find_element(By.ID, "approval_status"))
        status_select.select_by_value("Pending")
        
        browser.find_element(By.ID, "submittal_ref").send_keys("SUB-PVC-001")
        browser.find_element(By.ID, "specification_ref").send_keys("SPEC-001")
        browser.find_element(By.ID, "revision_number").clear()
        browser.find_element(By.ID, "revision_number").send_keys("0")
        
        # Submit form
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        # Wait for modal to close and table to update
        time.sleep(2)
        
        # Verify material appears in table
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "PVC Conduits & Accessories" in table_text
        assert "SUB-PVC-001" in table_text
        assert "Pending" in table_text
        
        print("✅ Material created successfully")
    
    def test_02_update_material_status(self, browser):
        """Test updating material approval status"""
        browser.get(f"{BASE_URL}/materials")
        
        # Click Edit button on first material
        edit_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-edit')]"))
        )
        edit_btn.click()
        
        # Wait for modal
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "materialModal"))
        )
        
        # Update approval status
        status_select = Select(browser.find_element(By.ID, "approval_status"))
        status_select.select_by_value("Approved")
        
        # Add approval notes
        browser.find_element(By.ID, "approval_notes").send_keys("Approved for construction")
        
        # Set approval date to today
        today = datetime.now().strftime("%Y-%m-%d")
        browser.find_element(By.ID, "approval_date").send_keys(today)
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify status updated
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "Approved" in table_text
        
        print("✅ Material status updated successfully")
    
    def test_03_create_material_revision(self, browser):
        """Test creating a material revision"""
        browser.get(f"{BASE_URL}/materials")
        
        # Click Add Material
        add_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Add Material')]")
        add_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "materialModal"))
        )
        
        # Fill in revision details
        browser.find_element(By.ID, "material_type").send_keys("PVC Conduits & Accessories")
        browser.find_element(By.ID, "description").send_keys("20mm PVC conduit pipes - improved specs")
        browser.find_element(By.ID, "submittal_ref").send_keys("SUB-PVC-001-R1")
        browser.find_element(By.ID, "specification_ref").send_keys("SPEC-001")
        browser.find_element(By.ID, "revision_number").clear()
        browser.find_element(By.ID, "revision_number").send_keys("1")
        
        # Select previous submittal if dropdown exists
        try:
            prev_select = Select(browser.find_element(By.ID, "previous_submittal_id"))
            # Select first option (if any materials exist)
            if len(prev_select.options) > 1:
                prev_select.select_by_index(1)
        except NoSuchElementException:
            pass
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify revision created
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "SUB-PVC-001-R1" in table_text
        
        print("✅ Material revision created successfully")


class TestPurchaseOrderUI:
    """Test Purchase Order UI"""
    
    def test_04_create_purchase_order(self, browser):
        """Test creating a purchase order through UI"""
        browser.get(f"{BASE_URL}/purchase_orders")
        
        # Click Add PO
        add_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Purchase Order')]"))
        )
        add_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "poModal"))
        )
        
        # Select material
        material_select = Select(browser.find_element(By.ID, "material_id"))
        if len(material_select.options) > 1:
            material_select.select_by_index(1)
        
        # Fill in PO details
        browser.find_element(By.ID, "quote_ref").send_keys("QUO-2025-001")
        browser.find_element(By.ID, "po_ref").send_keys("PO-2025-001")
        
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        browser.find_element(By.ID, "po_date").send_keys(today)
        browser.find_element(By.ID, "expected_delivery_date").send_keys(future)
        
        browser.find_element(By.ID, "supplier_name").send_keys("ABC Trading LLC")
        browser.find_element(By.ID, "supplier_contact").send_keys("+971-4-1234567")
        browser.find_element(By.ID, "supplier_email").send_keys("supplier@abc.ae")
        
        browser.find_element(By.ID, "total_amount").send_keys("50000.00")
        
        currency_select = Select(browser.find_element(By.ID, "currency"))
        currency_select.select_by_value("AED")
        
        status_select = Select(browser.find_element(By.ID, "po_status"))
        status_select.select_by_value("Not Released")
        
        browser.find_element(By.ID, "payment_terms").send_keys("50% advance, 50% on delivery")
        browser.find_element(By.ID, "delivery_terms").send_keys("DDP Dubai")
        browser.find_element(By.ID, "notes").send_keys("Urgent requirement for Phase 1")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify PO created
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "PO-2025-001" in table_text
        assert "ABC Trading LLC" in table_text
        assert "Not Released" in table_text
        
        print("✅ Purchase Order created successfully")
    
    def test_05_release_purchase_order(self, browser):
        """Test releasing a purchase order"""
        browser.get(f"{BASE_URL}/purchase_orders")
        
        # Click Edit on PO
        edit_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-edit')]"))
        )
        edit_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "poModal"))
        )
        
        # Change status to Released
        status_select = Select(browser.find_element(By.ID, "po_status"))
        status_select.select_by_value("Released")
        
        # Add note
        notes_field = browser.find_element(By.ID, "notes")
        current_notes = notes_field.get_attribute("value")
        notes_field.clear()
        notes_field.send_keys(f"{current_notes}\nPO released on {datetime.now().strftime('%Y-%m-%d')}")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify status changed
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "Released" in table_text
        
        print("✅ Purchase Order released successfully")


class TestPaymentUI:
    """Test Payment Management UI"""
    
    def test_06_create_advance_payment(self, browser):
        """Test creating advance payment"""
        browser.get(f"{BASE_URL}/payments")
        
        # Click Add Payment
        add_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Payment')]"))
        )
        add_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "paymentModal"))
        )
        
        # Select PO
        po_select = Select(browser.find_element(By.ID, "po_id"))
        if len(po_select.options) > 1:
            po_select.select_by_index(1)
        
        time.sleep(1)  # Wait for auto-fill
        
        # Select payment structure
        structure_select = Select(browser.find_element(By.ID, "payment_structure"))
        structure_select.select_by_value("Advance + Balance")
        
        type_select = Select(browser.find_element(By.ID, "payment_type"))
        type_select.select_by_value("Advance")
        
        # Fill payment details
        browser.find_element(By.ID, "paid_amount").clear()
        browser.find_element(By.ID, "paid_amount").send_keys("25000.00")
        
        browser.find_element(By.ID, "payment_percentage").clear()
        browser.find_element(By.ID, "payment_percentage").send_keys("50")
        
        today = datetime.now().strftime("%Y-%m-%d")
        browser.find_element(By.ID, "payment_date").send_keys(today)
        
        browser.find_element(By.ID, "payment_ref").send_keys("PAY-001-ADV")
        browser.find_element(By.ID, "invoice_ref").send_keys("INV-001")
        
        method_select = Select(browser.find_element(By.ID, "payment_method"))
        method_select.select_by_value("Bank Transfer")
        
        status_select = Select(browser.find_element(By.ID, "payment_status"))
        status_select.select_by_value("Completed")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify payment created
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "PAY-001-ADV" in table_text
        assert "Advance" in table_text
        assert "50" in table_text or "50%" in table_text
        
        print("✅ Advance payment created successfully")
    
    def test_07_create_balance_payment(self, browser):
        """Test creating balance payment"""
        browser.get(f"{BASE_URL}/payments")
        
        # Click Add Payment
        add_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Add Payment')]")
        add_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "paymentModal"))
        )
        
        # Select same PO
        po_select = Select(browser.find_element(By.ID, "po_id"))
        if len(po_select.options) > 1:
            po_select.select_by_index(1)
        
        time.sleep(1)
        
        # Select balance payment
        structure_select = Select(browser.find_element(By.ID, "payment_structure"))
        structure_select.select_by_value("Advance + Balance")
        
        type_select = Select(browser.find_element(By.ID, "payment_type"))
        type_select.select_by_value("Balance")
        
        # Fill payment details
        browser.find_element(By.ID, "paid_amount").clear()
        browser.find_element(By.ID, "paid_amount").send_keys("25000.00")
        
        browser.find_element(By.ID, "payment_percentage").clear()
        browser.find_element(By.ID, "payment_percentage").send_keys("50")
        
        today = datetime.now().strftime("%Y-%m-%d")
        browser.find_element(By.ID, "payment_date").send_keys(today)
        
        browser.find_element(By.ID, "payment_ref").send_keys("PAY-001-BAL")
        browser.find_element(By.ID, "invoice_ref").send_keys("INV-002")
        
        method_select = Select(browser.find_element(By.ID, "payment_method"))
        method_select.select_by_value("Bank Transfer")
        
        status_select = Select(browser.find_element(By.ID, "payment_status"))
        status_select.select_by_value("Completed")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify both payments exist
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "PAY-001-BAL" in table_text
        assert "Balance" in table_text
        
        print("✅ Balance payment created successfully (Total: 100%)")


class TestDeliveryUI:
    """Test Delivery Management UI"""
    
    def test_08_create_pending_delivery(self, browser):
        """Test creating pending delivery"""
        browser.get(f"{BASE_URL}/deliveries")
        
        # Click Add Delivery
        add_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Delivery')]"))
        )
        add_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "deliveryModal"))
        )
        
        # Select PO
        po_select = Select(browser.find_element(By.ID, "po_id"))
        if len(po_select.options) > 1:
            po_select.select_by_index(1)
        
        time.sleep(1)
        
        # Fill delivery details
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        browser.find_element(By.ID, "expected_delivery_date").send_keys(future)
        
        status_select = Select(browser.find_element(By.ID, "delivery_status"))
        status_select.select_by_value("Pending")
        
        browser.find_element(By.ID, "delivery_percentage").clear()
        browser.find_element(By.ID, "delivery_percentage").send_keys("0")
        
        browser.find_element(By.ID, "tracking_number").send_keys("TRK-2025-001")
        browser.find_element(By.ID, "carrier").send_keys("Aramex")
        browser.find_element(By.ID, "delivery_location").send_keys("Project Site - Dubai")
        browser.find_element(By.ID, "notes").send_keys("Awaiting dispatch confirmation")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify delivery created
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "TRK-2025-001" in table_text
        assert "Pending" in table_text
        
        print("✅ Pending delivery created successfully")
    
    def test_09_update_to_partial_delivery(self, browser):
        """Test updating delivery to partial"""
        browser.get(f"{BASE_URL}/deliveries")
        
        # Click Edit
        edit_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-edit')]"))
        )
        edit_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "deliveryModal"))
        )
        
        # Update to partial
        status_select = Select(browser.find_element(By.ID, "delivery_status"))
        status_select.select_by_value("Partial")
        
        browser.find_element(By.ID, "delivery_percentage").clear()
        browser.find_element(By.ID, "delivery_percentage").send_keys("65")
        
        today = datetime.now().strftime("%Y-%m-%d")
        browser.find_element(By.ID, "actual_delivery_date").send_keys(today)
        browser.find_element(By.ID, "received_by").send_keys("Site Manager")
        
        notes_field = browser.find_element(By.ID, "notes")
        notes_field.clear()
        notes_field.send_keys("65% of items received and inspected")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify update
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "Partial" in table_text
        assert "65" in table_text or "65%" in table_text
        
        print("✅ Delivery updated to partial (65%)")
    
    def test_10_complete_delivery(self, browser):
        """Test completing delivery"""
        browser.get(f"{BASE_URL}/deliveries")
        
        # Click Edit
        edit_btn = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-edit')]"))
        )
        edit_btn.click()
        
        WebDriverWait(browser, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "deliveryModal"))
        )
        
        # Complete delivery
        status_select = Select(browser.find_element(By.ID, "delivery_status"))
        status_select.select_by_value("Delivered")
        
        browser.find_element(By.ID, "delivery_percentage").clear()
        browser.find_element(By.ID, "delivery_percentage").send_keys("100")
        
        notes_field = browser.find_element(By.ID, "notes")
        notes_field.clear()
        notes_field.send_keys("All items received, inspected and accepted")
        
        # Save
        save_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        time.sleep(2)
        
        # Verify completion
        table_text = browser.find_element(By.TAG_NAME, "table").text
        assert "Delivered" in table_text
        assert "100" in table_text or "100%" in table_text
        
        print("✅ Delivery completed successfully (100%)")


class TestCompleteWorkflow:
    """Test complete end-to-end workflow"""
    
    def test_11_verify_complete_workflow(self, browser):
        """Verify all components are connected properly"""
        
        # Check materials page
        browser.get(f"{BASE_URL}/materials")
        assert "Materials" in browser.title or "Materials" in browser.find_element(By.TAG_NAME, "h1").text
        materials_count = len(browser.find_elements(By.XPATH, "//table//tbody//tr"))
        assert materials_count > 0, "No materials found"
        print(f"✅ Materials page: {materials_count} materials")
        
        # Check POs page
        browser.get(f"{BASE_URL}/purchase_orders")
        assert "Purchase Order" in browser.title or "Purchase" in browser.find_element(By.TAG_NAME, "h1").text
        po_count = len(browser.find_elements(By.XPATH, "//table//tbody//tr"))
        assert po_count > 0, "No purchase orders found"
        print(f"✅ Purchase Orders page: {po_count} POs")
        
        # Check payments page
        browser.get(f"{BASE_URL}/payments")
        assert "Payment" in browser.title or "Payment" in browser.find_element(By.TAG_NAME, "h1").text
        payment_count = len(browser.find_elements(By.XPATH, "//table//tbody//tr"))
        assert payment_count >= 2, "Expected at least 2 payments (advance + balance)"
        print(f"✅ Payments page: {payment_count} payments")
        
        # Check deliveries page
        browser.get(f"{BASE_URL}/deliveries")
        assert "Deliver" in browser.title or "Deliver" in browser.find_element(By.TAG_NAME, "h1").text
        delivery_count = len(browser.find_elements(By.XPATH, "//table//tbody//tr"))
        assert delivery_count > 0, "No deliveries found"
        print(f"✅ Deliveries page: {delivery_count} deliveries")
        
        print("\n" + "="*60)
        print("🎉 COMPLETE WORKFLOW VERIFIED SUCCESSFULLY!")
        print("="*60)
        print(f"✅ {materials_count} Materials created")
        print(f"✅ {po_count} Purchase Orders created")
        print(f"✅ {payment_count} Payments recorded")
        print(f"✅ {delivery_count} Deliveries tracked")
        print("="*60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
