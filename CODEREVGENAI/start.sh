#!/usr/bin/env bash
# Quick Start Guide for Code Refine

echo "=========================================="
echo "Code Refine - Quick Start"
echo "=========================================="
echo ""

# Change to backend directory
cd "$(dirname "$0")/backend" || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Show server info
echo ""
echo "=========================================="
echo "Starting Server..."
echo "=========================================="
echo "URL: http://127.0.0.1:8000/login"
echo ""
echo "Demo Credentials:"
echo "  Username: admin"
echo "  Password: password"
echo ""
echo "Or try: student1 / teacher with same password"
echo "=========================================="
echo ""

# Run the server
python main.py
