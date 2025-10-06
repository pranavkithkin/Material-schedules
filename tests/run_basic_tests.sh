#!/bin/bash

# Test Runner for Basic CRUD Operations (Manual Entry Testing)
# ==============================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║  Material Delivery Dashboard - Basic CRUD Tests                  ║"
echo "║  Testing Manual Entry Features (No AI)                           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Change to project directory
cd "/mnt/c/Users/PKP/Documents/PRANAV/Projects/With a clear picture/9. material delivery dashboard"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update test dependencies
echo "📦 Installing test dependencies..."
pip install pytest pytest-cov pytest-flask -q

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Running Basic CRUD Tests"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Run tests with verbose output
pytest tests/test_basic_crud_manual.py -v --tb=short

# Store exit code
EXIT_CODE=$?

echo ""
echo "════════════════════════════════════════════════════════════════════"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅  ALL TESTS PASSED!"
    echo "    Basic CRUD operations are working correctly."
    echo "    Ready for manual data entry."
else
    echo "❌  TESTS FAILED!"
    echo "    Please fix errors before using manual entry."
fi

echo "════════════════════════════════════════════════════════════════════"
echo ""

# Optional: Run with coverage
read -p "📊 Run with coverage report? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running tests with coverage..."
    pytest tests/test_basic_crud_manual.py --cov=models --cov=routes --cov-report=term-missing
fi

echo ""
echo "Test run complete!"

exit $EXIT_CODE
