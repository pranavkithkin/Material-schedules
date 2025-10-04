#!/bin/bash
# Quick fix for anthropic/httpx dependency issue

echo "============================================"
echo "🔧 FIXING ANTHROPIC DEPENDENCY ISSUE"
echo "============================================"
echo ""
echo "This will update anthropic and httpx packages..."
echo ""

# Upgrade the problematic packages
pip install --upgrade anthropic httpx

echo ""
echo "============================================"
echo "✅ FIX COMPLETE!"
echo "============================================"
echo ""
echo "Now you can run:"
echo "  python app.py"
echo ""
