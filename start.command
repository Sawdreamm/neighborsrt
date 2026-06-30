#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
URL="http://127.0.0.1:8765"
echo "Starting NeighborSRT Local Web..."
echo "Open: $URL"
(sleep 1 && open "$URL") &
python3 app/server.py
