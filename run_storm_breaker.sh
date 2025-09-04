#!/bin/bash

# Storm-Breaker Tool Runner
# This script demonstrates different ways to run the Storm-Breaker tool

echo "🌪️  Storm-Breaker Tool Runner"
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if storm_breaker.py exists
if [ ! -f "storm_breaker.py" ]; then
    echo "❌ storm_breaker.py not found in current directory"
    exit 1
fi

echo "1. Basic Storm-Breaker scan (verbose):"
echo "   python3 storm_breaker.py -v"
echo ""

echo "2. Storm-Breaker with custom output:"
echo "   python3 storm_breaker.py -v -o custom_scan_results.json"
echo ""

echo "3. Storm-Breaker help:"
echo "   python3 storm_breaker.py --help"
echo ""

echo "Choose an option (1-3) or press Enter to run basic scan:"
read -r choice

case $choice in
    1|"")
        echo "🔥 Running basic Storm-Breaker scan..."
        python3 storm_breaker.py -v
        ;;
    2)
        echo "🔥 Running Storm-Breaker with custom output..."
        python3 storm_breaker.py -v -o custom_scan_results.json
        ;;
    3)
        echo "📖 Showing Storm-Breaker help..."
        python3 storm_breaker.py --help
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Storm-Breaker operation completed!"
echo "📁 Check the 'output' directory for results and logs"
echo "📁 Check the 'overlays' directory for generated overlay files"