#!/usr/bin/env bash
# ============================================================
# setup.sh — one-command local dev setup
# Usage: chmod +x setup.sh && ./setup.sh
# ============================================================
set -e

echo ""
echo " Teacher Attrition EWS — Local Setup"
echo "======================================="
echo ""

# 1. Virtual environment
if [ ! -d "venv" ]; then
  echo " Creating virtual environment..."
  python3 -m venv venv
else
  echo " Virtual environment already exists"
fi

source venv/bin/activate

# 2. Dependencies
echo " Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo " Dependencies installed"

# 3. .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo " Created .env from .env.example (SQLite mode — no MySQL needed)"
else
  echo " .env already exists"
fi

# 4. Required directories
mkdir -p models data/raw data/processed mlruns outputs
echo " Directories ready"

# 5. Check for model artefacts
if [ ! -f "models/xgboost_attrition_model.pkl" ]; then
  echo ""
  echo "  No trained model found in models/"
  echo "   Run the notebook first: notebooks/01_eda_baseline.ipynb"
  echo "   Or run: python src/models/train.py"
  echo ""
else
  echo " Model artefacts found"
fi

echo ""
echo " Setup complete. Next steps:"
echo ""
echo "  1. Train the model (if not done):"
echo "     jupyter notebook notebooks/01_eda_baseline.ipynb"
echo ""
echo "  2. Start the API:"
echo "     source venv/bin/activate"
echo "     uvicorn src.api.main:app --reload --port 8000"
echo "     → Swagger UI: http://localhost:8000/docs"
echo ""
echo "  3. Start the dashboard (new terminal):"
echo "     source venv/bin/activate"
echo "     streamlit run dashboard/app.py"
echo "     → Dashboard: http://localhost:8501"
echo ""
