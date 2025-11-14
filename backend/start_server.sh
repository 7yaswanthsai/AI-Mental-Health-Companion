#!/bin/bash
echo "Starting PAI-MHC Backend Server..."
echo ""
echo "Server will be accessible at:"
echo "  - Local: http://127.0.0.1:8000"
echo "  - Android Emulator: http://10.0.2.2:8000"
echo "  - iOS Simulator: http://localhost:8000"
echo "  - Network: http://YOUR_IP:8000"
echo ""
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

