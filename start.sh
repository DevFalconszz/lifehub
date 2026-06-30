#!/bin/bash
# LifeHub - Start both Backend (FastAPI) and Frontend (Vite)
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

cleanup() {
  echo ""
  echo -e "${YELLOW}${BOLD}╔════════════════════════════════════════╗${NC}"
  echo -e "${YELLOW}${BOLD}║     Shutting down LifeHub...           ║${NC}"
  echo -e "${YELLOW}${BOLD}╚════════════════════════════════════════╝${NC}"
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
  echo -e "${GREEN}${BOLD}✓ LifeHub stopped.${NC}"
  exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════╗"
echo "║           LifeHub                       ║"
echo "║     Personal Life Management             ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Start Backend
echo -e "${BLUE}${BOLD}[BACKEND] Starting FastAPI server...${NC}"
cd "$BACKEND_DIR"
python3 run.py > >(while IFS= read -r line; do echo -e "${BLUE}[BACKEND]${NC} $line"; done) 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo -e "${YELLOW}[WAIT] Waiting for backend on port 8004...${NC}"
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:8004/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}[BACKEND] ✓ Ready (http://127.0.0.1:8004)${NC}"
    break
  fi
  if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}[BACKEND] ✗ Process died unexpectedly${NC}"
    exit 1
  fi
  sleep 1
done

# Start Frontend
echo -e "${MAGENTA}${BOLD}[FRONTEND] Starting Vite dev server...${NC}"
cd "$FRONTEND_DIR"
npx vite --host 2>&1 | while IFS= read -r line; do
  if echo "$line" | grep -qi "error\|Error\|ERR!"; then
    echo -e "${RED}[FRONTEND]${NC} $line"
  else
    echo -e "${MAGENTA}[FRONTEND]${NC} $line"
  fi
done &
FRONTEND_PID=$!

sleep 2
echo ""
echo -e "${GREEN}${BOLD}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║  LifeHub is running!                   ║${NC}"
echo -e "${GREEN}${BOLD}║                                        ║${NC}"
echo -e "${GREEN}${BOLD}║  Frontend:  http://localhost:5173       ║${NC}"
echo -e "${GREEN}${BOLD}║  Backend:   http://localhost:8004       ║${NC}"
echo -e "${GREEN}${BOLD}║  API Docs:  http://localhost:8004/docs   ║${NC}"
echo -e "${GREEN}${BOLD}║                                        ║${NC}"
echo -e "${GREEN}${BOLD}║  Press Ctrl+C to stop                  ║${NC}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════╝${NC}"
echo ""

wait
