#!/bin/bash
# MOLTmarket Dashboard launcher

set -e

echo "MOLTmarket Live Validation Dashboard"
echo "===================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Create template and static directories if needed
mkdir -p templates static

echo "✅ Ready to launch"
echo ""
echo "🚀 Starting dashboard on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Run
python3 moltmarket_dashboard.py
