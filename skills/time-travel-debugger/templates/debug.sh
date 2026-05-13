#!/bin/bash

# Ensure we are in the visualizer directory
cd /home/integrity/Desktop/agent/01_Projects/architecture-visualizer

if [ -z "$1" ]; then
    echo "Usage: ./debug.sh <path/to/target.cpp>"
    echo "Example: ./debug.sh parser/interactive.cpp"
    exit 1
fi

TARGET_FILE=$(realpath "$1")
DIRNAME=$(dirname "$TARGET_FILE")
FILENAME=$(basename -- "$TARGET_FILE")
BASENAME="${FILENAME%.*}"

echo "=========================================="
echo " 🚀 Starting Architecture Visualizer..."
echo "=========================================="

echo "[1/4] Starting Telemetry Bridge (Port 4000/4001/4002)..."
if ! pgrep -f "node server.js" > /dev/null; then
    nohup node server.js > telemetry.log 2>&1 &
    sleep 1
else
    echo "      -> Already running."
fi

echo "[2/4] Starting Web Visualizer (Port 5175)..."
# Check if Vite is running specifically for architecture-visualizer
if ! lsof -i:5175 > /dev/null; then
    nohup npm run dev > vite.log 2>&1 &
    sleep 1
else
    echo "      -> Already running."
fi

echo "[3/4] Parsing AST & Injecting Telemetry Hooks..."
cd parser
./venv/bin/python parse_cpp.py "$TARGET_FILE"

if [ -f "$DIRNAME/${BASENAME}_traced.cpp" ]; then
    echo "[4/4] Compiling traced executable..."
    # Compile in the directory of the target file
    cd "$DIRNAME"
    g++ "${BASENAME}_traced.cpp" -o "${BASENAME}_app"
else
    echo "❌ AST Parsing failed. Traced file not found."
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed."
    exit 1
fi

echo "=========================================="
echo " ✅ Setup Complete!"
echo " 1. Open your browser to: http://localhost:5175"
echo " 2. Follow the prompt below in this terminal"
echo " 3. Click STEP NEXT in your browser to advance code execution!"
echo "=========================================="
echo ""

./"${BASENAME}_app"
