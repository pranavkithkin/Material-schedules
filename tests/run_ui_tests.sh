#!/bin/bash

# Automated UI Testing Runner
# Runs Selenium-based browser automation tests

set -e  # Exit on error

echo "======================================================"
echo "🌐 Material Delivery Dashboard - UI Automation Tests"
echo "======================================================"
echo ""

# Navigate to project root
cd "/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install UI testing dependencies
echo "📥 Installing UI testing dependencies..."
pip install -q -r tests/requirements-ui-tests.txt

# Check if Flask app is running
echo "🔍 Checking if Flask application is running..."
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "❌ ERROR: Flask application is not running!"
    echo ""
    echo "Please start the application first:"
    echo "  python app.py"
    echo ""
    exit 1
fi

echo "✅ Flask application is running"
echo ""

# Run UI tests
echo "🚀 Running UI automation tests..."
echo "======================================================"
pytest tests/test_ui_automation.py -v --tb=short --html=tests/ui_test_report.html --self-contained-html

# Check test results
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================"
    echo "✅ ALL UI TESTS PASSED!"
    echo "======================================================"
    echo ""
    echo "📊 Test report generated: tests/ui_test_report.html"
    echo ""
    echo "Next steps:"
    echo "  1. Review the test report"
    echo "  2. Check the application UI manually"
    echo "  3. Proceed to Phase 3 (AI features)"
    echo ""
else
    echo ""
    echo "======================================================"
    echo "❌ SOME UI TESTS FAILED"
    echo "======================================================"
    echo ""
    echo "Please review the errors above and fix them."
    echo "Test report: tests/ui_test_report.html"
    echo ""
    exit 1
fi
