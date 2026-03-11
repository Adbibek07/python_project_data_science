#!/bin/bash

echo "🎬 CineScope Starting..."

# Get the directory where run.sh is located
DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if venv exists, if not create it and install dependencies
if [ ! -d "$DIR/venv" ]; then
    echo "📦 No venv found — creating one..."
    python3 -m venv "$DIR/venv"
    echo "📥 Installing dependencies..."
    "$DIR/venv/bin/pip" install -r "$DIR/requirements.txt"
    echo "✅ Dependencies installed."
fi

PYTHON="$DIR/venv/bin/python"
STREAMLIT="$DIR/venv/bin/streamlit"

echo "Running scraper..."
"$PYTHON" "$DIR/backend/fetch.py"

if [ $? -eq 0 ]; then
    echo "✅ Scraping successful — fresh data loaded."
else
    echo "⚠️  Scraping failed — using previously scraped CSV file."
    if [ ! -f "$DIR/backend/movies.csv" ]; then
        echo "❌ No previous CSV found. Exiting."
        exit 1
    else
        echo "📁 Found existing movies.csv — continuing with old data."
    fi
fi

echo "🚀 Starting Streamlit..."
"$STREAMLIT" run "$DIR/streamlit/app.py"