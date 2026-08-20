# Frontend

This Streamlit frontend is intentionally simple. It lets a user configure one
backtest from a single page and calls the FastAPI backend.

## Run Locally

Start the FastAPI backend first:

```bash
cd /Users/qiankangwang/Desktop/investment-strategy-lab/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

In a second terminal, start Streamlit:

```bash
cd /Users/qiankangwang/Desktop/investment-strategy-lab
source backend/.venv/bin/activate
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

The page will collect:

- Initial capital
- Ticker and date range
- Strategy condition
- Action
- Sizing rule

It displays:

- Stock price chart
- Portfolio value chart
