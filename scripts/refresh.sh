#!/bin/bash
# GitHub Reading List Generator - Refresh Script

set -e  # Exit on any error

echo "🔄 Starting GitHub Reading List refresh..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if package is installed
if ! python -c "import reading_list" 2>/dev/null; then
    echo "📦 Installing reading-list package..."
    pip install -e .
fi

# Run the refresh
echo "🚀 Running refresh..."
python -m reading_list.scripts.refresh

echo "✅ Refresh completed!"
echo "📄 Check the data/ directory for generated files." 