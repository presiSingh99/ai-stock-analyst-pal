"""
AI Financial Analyst Copilot
─────────────────────────────
Streamlit dashboard with fake sample data for NVDA.

To swap in real data later, replace the `get_stock_data()` function
with a yfinance call:

    import yfinance as yf
    def get_stock_data(ticker: str, period_days: int) -> pd.DataFrame:
        period_map = {30: "1mo", 90: "3mo", 365: "1y"}
        df = yf.download(ticker, period=period_map[period_days])
        df = df[["Close", "Volume"]].reset_index()
        df.columns = ["Date", "Close", "Volume"]
        return df
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Stock Analyst Copilot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st_autorefresh(interval=60 * 1000, key="stock_refresh")

st.markdown("""
<style>
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CUSTOM CSS  (fintech dark-mode aesthetic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Base ── */
  [data-testid="stAppViewContainer"] {
      background: #0d0b1a;
      color: #e2e8f0;
  }
  [data-testid="stSidebar"] {
      background: #111827;
      border-right: 1px solid #1e2d45;
  }
  [data-testid="stSidebar"] * { color: #cbd5e1 !important; }

  /* ── Header ── */
  .copilot-header {
      display: flex;
      align-items: baseline;
      gap: 12px;
      padding: 0 0 6px 0;
      border-bottom: 1px solid #1e3a5f;
      margin-bottom: 28px;
  }
  @media (max-width: 768px) {
    .copilot-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
        margin-bottom: 18px;
    }

    .copilot-title {
        font-size: 1.4rem !important;
        line-height: 1.2;
    }

    .copilot-sub {
        font-size: 0.75rem !important;
    }
}
  .copilot-title {
      font-family: 'SF Mono', 'Fira Code', monospace;
      font-size: 1.75rem;
      font-weight: 700;
      color: #38bdf8;
      letter-spacing: -0.5px;
  }
  .copilot-sub {
      font-size: 0.85rem;
      color: #475569;
      font-family: monospace;
  }
  .ticker-badge {
      font-family: monospace;
      font-size: 0.8rem;
      background: #0f2944;
      color: #38bdf8;
      padding: 3px 10px;
      border-radius: 4px;
      border: 1px solid #1e4976;
      margin-left: auto;
  }

  /* ── KPI cards ── */
  .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 28px;
  }
  .kpi-card {
      background: #111827;
      border: 1px solid #1e2d45;
      border-radius: 8px;
      padding: 18px 20px;
      position: relative;
      overflow: hidden;
  }
  .kpi-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: linear-gradient(90deg, #38bdf8, #0ea5e9);
  }
  .kpi-card.negative::before {
      background: linear-gradient(90deg, #f87171, #ef4444);
  }
  .kpi-card.neutral::before {
      background: linear-gradient(90deg, #94a3b8, #64748b);
  }
  .kpi-label {
      font-size: 0.7rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      font-family: monospace;
      margin-bottom: 8px;
  }
  .kpi-value {
      font-size: 1.65rem;
      font-weight: 700;
      font-family: 'SF Mono', monospace;
      color: #f1f5f9;
      line-height: 1;
  }
  .kpi-delta {
      font-size: 0.78rem;
      color: #4ade80;
      margin-top: 6px;
      font-family: monospace;
  }
  .kpi-delta.neg { color: #f87171; }
  .kpi-delta.neu { color: #94a3b8; }

  /* ── Section labels ── */
  .section-label {
      font-family: monospace;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: #475569;
      margin-bottom: 10px;
      padding-bottom: 6px;
      border-bottom: 1px solid #1e2d45;
  }

  /* ── AI Summary ── */
  .ai-summary-box {
      background: #0d1f35;
      border: 1px solid #1e3a5f;
      border-left: 3px solid #38bdf8;
      border-radius: 6px;
      padding: 20px 24px;
      font-size: 0.9rem;
      line-height: 1.7;
      color: #cbd5e1;
  }
  .ai-tag {
      display: inline-block;
      font-family: monospace;
      font-size: 0.65rem;
      background: #0f2944;
      color: #38bdf8;
      border: 1px solid #1e4976;
      border-radius: 3px;
      padding: 2px 7px;
      margin-bottom: 10px;
      letter-spacing: 1px;
  }

  /* ── Metrics table ── */
  .metrics-table {
      width: 100%;
      border-collapse: collapse;
      font-family: 'SF Mono', monospace;
      font-size: 0.82rem;
  }
  .metrics-table th {
      background: #111827;
      color: #475569;
      font-size: 0.65rem;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      padding: 10px 14px;
      text-align: left;
      border-bottom: 1px solid #1e2d45;
  }
  .metrics-table td {
      padding: 9px 14px;
      border-bottom: 1px solid #141d2b;
      color: #cbd5e1;
  }
  .metrics-table tr:hover td { background: #111827; }
  .pos { color: #4ade80; }
  .neg { color: #f87171; }
  .neu { color: #94a3b8; }

  /* ── Question input ── */
  .question-area label { color: #64748b !important; font-size: 0.75rem !important; }
  [data-testid="stTextArea"] textarea {
      background: #111827 !important;
      border: 1px solid #1e2d45 !important;
      color: #e2e8f0 !important;
      font-family: monospace;
      font-size: 0.85rem;
  }
  [data-testid="stButton"] > button {
      background: #0369a1;
      color: white;
      border: none;
      border-radius: 5px;
      font-family: monospace;
      font-size: 0.8rem;
      letter-spacing: 0.5px;
      padding: 8px 20px;
  }
  [data-testid="stButton"] > button:hover { background: #0284c7; }

  /* ── Plotly chart container ── */
  .chart-wrapper {
      background: #111827;
      border: 1px solid #1e2d45;
      border-radius: 8px;
      padding: 4px;
      margin-bottom: 28px;
  }

  /* hide default streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LAYER  ← replace this function with yfinance
# ─────────────────────────────────────────────

st.markdown(f"##### {selected_ticker} · {period_label}")

FAKE_PRICES = {
    "NVDA": 875.50,   # approximate seed price
}


def get_stock_data(ticker: str, period_days: int) -> pd.DataFrame:
    """
    Pulls real stock data from Yahoo Finance.
    Returns a DataFrame with columns: Date, Close, Volume.
    """
    import yfinance as yf

    period_map = {
        30: "1mo",
        90: "3mo",
        365: "1y"
    }

    ticker = ticker.upper().strip()

    df = yf.download(
        ticker,
        period=period_map.get(period_days, "1mo"),
        progress=False,
        auto_adjust=False
    )

    if df.empty:
        raise ValueError(f"No data found for ticker: {ticker}")

    df = df[["Close", "Volume"]].reset_index()
    df.columns = ["Date", "Close", "Volume"]

    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MA7"] = df["Close"].rolling(7).mean()
    df["MA30"] = df["Close"].rolling(30).mean()
    df["Daily_Return"] = df["Close"].pct_change()
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    latest = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    start = df["Close"].iloc[0]
    change_d = (latest - prev) / prev * 100
    change_p = (latest - start) / start * 100
    vol = df["Daily_Return"].std() * np.sqrt(252) * 100  # annualised %
    trend = "Bullish 🟢" if df["MA7"].iloc[-1] > df["MA30"].iloc[-1] else "Bearish 🔴"
    return {
        "price":    latest,
        "change_d": change_d,
        "change_p": change_p,
        "vol":      vol,
        "trend":    trend,
    }


def build_metrics_table(df: pd.DataFrame) -> str:
    latest = df["Close"].iloc[-1]
    high_52 = df["Close"].max()
    low_52 = df["Close"].min()
    avg_vol = df["Volume"].mean()
    rsi_val = compute_rsi(df["Close"])
    dd = max_drawdown(df["Close"])
    sharpe = compute_sharpe(df["Daily_Return"])

    rows = [
        ("Current Price",       f"${latest:.2f}",              "neu"),
        ("Period High",         f"${high_52:.2f}",             "pos"),
        ("Period Low",          f"${low_52:.2f}",              "neg"),
        ("Avg Daily Volume",    f"{avg_vol/1e6:.1f}M shares",  "neu"),
        ("RSI (14)",            f"{rsi_val:.1f}",
            "pos" if rsi_val < 70 else "neg" if rsi_val > 70 else "neu"),
        ("Max Drawdown",        f"{dd:.1f}%",                  "neg"),
        ("Sharpe (annualised)", f"{sharpe:.2f}",
            "pos" if sharpe > 1 else "neg" if sharpe < 0 else "neu"),
    ]

    html = '<table class="metrics-table"><thead><tr>'
    html += "<th>Metric</th><th>Value</th></tr></thead><tbody>"
    for label, val, cls in rows:
        html += f'<tr><td class="neu">{label}</td><td class="{cls}">{val}</td></tr>'
    html += "</tbody></table>"
    return html


def compute_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


def max_drawdown(series: pd.Series) -> float:
    roll_max = series.cummax()
    dd = (series - roll_max) / roll_max * 100
    return float(dd.min())


def compute_sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns.dropna() - rf / 252
    if excess.std() == 0:
        return 0.0
    return float(excess.mean() / excess.std() * np.sqrt(252))


AI_SUMMARIES = {
    "bullish": (
        "NVDA exhibits strong upward momentum over the selected period, with the 7-day moving "
        "average trading above the 30-day MA — a classic golden-cross signal. Annualised "
        "volatility remains elevated relative to the broader semiconductor sector, reflecting "
        "ongoing market sensitivity to AI infrastructure demand cycles.\n\n"
        "Key support sits near the 30-day MA. A sustained close above the recent high would "
        "confirm the trend extension. Watch for volume confirmation: accumulation days "
        "(up-price / above-avg volume) outnumber distribution days in this window, which "
        "supports the bull case. RSI is approaching overbought territory — consider monitoring "
        "for potential short-term mean reversion before the next leg higher."
    ),
    "bearish": (
        "NVDA is showing near-term weakness with the 7-day MA declining below the 30-day MA — "
        "a death-cross pattern that historically precedes further consolidation. Annualised "
        "volatility is elevated, reflecting investor uncertainty around near-term earnings "
        "guidance and export regulation headwinds.\n\n"
        "Current price action is testing a critical support zone. A break below the period low "
        "could trigger additional selling pressure. RSI readings suggest the stock is not yet "
        "in oversold territory, leaving room for further downside. Monitor macroeconomic "
        "catalysts — particularly Fed rate decisions and semiconductor supply-chain data — "
        "for directional clarity."
    ),
}


def get_ai_summary(kpis: dict, question: str) -> str:
    import os
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    question_clean = question.strip().lower()

    if not question_clean:
        intent = "general_summary"
    elif any(word in question_clean for word in ["invest", "buy", "sell", "should", "when"]):
        intent = "investment_question"
    elif len(question_clean.split()) <= 3:
        intent = "executive_summary"
    else:
        intent = "custom_question"

    prompt = f"""
You are an AI financial analyst assistant.

User intent: {intent}

Stock Metrics:
- Current Price: ${kpis["price"]:.2f}
- Daily Change: {kpis["change_d"]:.2f}%
- Period Change: {kpis["change_p"]:.2f}%
- Annualized Volatility: {kpis["vol"]:.2f}%
- Trend Signal: {kpis["trend"]}

User Question:
{question if question.strip() else "No question provided."}

Instructions:
- If intent is general_summary, give a concise analyst overview.
- If intent is executive_summary, explain the company and what investors should monitor.
- If intent is investment_question, do not give direct buy/sell advice. Explain factors to consider.
- If intent is custom_question, answer using the available metrics.

Keep the answer practical, concise, and beginner-friendly.
Always avoid direct financial advice.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a careful financial analyst. Explain market data clearly without giving direct buy/sell advice.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


def compare_tickers(tickers, period_days):
    results = []
    for ticker in tickers:
        try:
            raw_df = get_stock_data(ticker, period_days)
            df = enrich(raw_df)
            kpis = compute_kpis(df)

            results.append({
                "Ticker": ticker,
                "Current Price": round(kpis["price"], 2),
                "Daily Change %": round(kpis["change_d"], 2),
                "Period Change %": round(kpis["change_p"], 2),
                "Volatility %": round(kpis["vol"], 2),
                "Trend": kpis["trend"],
            })

        except Exception:
            continue
    return pd.DataFrame(results)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style='font-family:monospace;font-size:0.7rem;letter-spacing:2px;
                    text-transform:uppercase;color:#475569;margin-bottom:18px;
                    padding-bottom:8px;border-bottom:1px solid #1e2d45;'>
            ⚙ Analyst Controls
        </div>
    """, unsafe_allow_html=True)

    ticker_input = st.text_input(
        "Tickers",
        value="NVDA, AAPL, MSFT",
        help="Enter up to 5 tickers separated by commas"
    )

    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    tickers = tickers[:5]

    period_label = st.selectbox(
        "Time Period",
        options=["30 Days", "90 Days", "1 Year"],
    )

    period_map = {
        "30 Days": 30,
        "90 Days": 90,
        "1 Year": 365
    }
    period_days = period_map[period_label]

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    question = st.text_area(
        "Ask the AI Analyst",
        placeholder="e.g. Is NVDA a buy right now?\nWhat does the trend suggest?",
        height=100,
    )

    run_analysis = st.button(
        "▶ Run Analysis",
        use_container_width=True
    )

    st.markdown("""
        <div style='margin-top:32px;font-family:monospace;font-size:0.65rem;
                    color:#334155;line-height:1.8;'>
            ⚠ AI summaries are illustrative and not financial advice.
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN PANEL
# ─────────────────────────────────────────────

# ── Header ──

st.markdown(f"""
<div class="copilot-header">
  <span class="copilot-title">AI Financial Analyst Copilot</span>
  <span class="copilot-sub">/ market intelligence dashboard</span>
</div>
""", unsafe_allow_html=True)

comparison_df = compare_tickers(tickers, period_days)
st.markdown(
    '<div class="section-label">Side-by-Side KPI Comparison</div>',
    unsafe_allow_html=True
)
st.dataframe(comparison_df, use_container_width=True)
selected_ticker = st.selectbox(
    "Detailed View",
    tickers
)

# ── Load & enrich data ──
with st.spinner("Loading market data…"):
    raw_df = get_stock_data(selected_ticker, period_days)
    st.caption(
        f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption(f"Latest market data date: {raw_df['Date'].max()}")
    df = enrich(raw_df)
    kpis = compute_kpis(df)

# ── KPI Cards ──

price_cls = "positive" if kpis["change_d"] >= 0 else "negative"
change_cls = "neg" if kpis["change_d"] < 0 else ""
period_cls = "neg" if kpis["change_p"] < 0 else ""
trend_cls = "neutral"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card {price_cls}">
    <div class="kpi-label">Current Price</div>
    <div class="kpi-value">${kpis['price']:.2f}</div>
    <div class="kpi-delta {change_cls}">
      {"▲" if kpis['change_d'] >= 0 else "▼"} {abs(kpis['change_d']):.2f}% today
    </div>
  </div>
  <div class="kpi-card {"negative" if kpis['change_p'] < 0 else ""}">
    <div class="kpi-label">Period Return</div>
    <div class="kpi-value">{kpis['change_p']:+.2f}%</div>
    <div class="kpi-delta {period_cls}">
      {"▲" if kpis['change_p'] >= 0 else "▼"} vs. period open
    </div>
  </div>
  <div class="kpi-card neutral">
    <div class="kpi-label">Annualised Volatility</div>
    <div class="kpi-value">{kpis['vol']:.1f}%</div>
    <div class="kpi-delta neu">σ based on daily returns</div>
  </div>
  <div class="kpi-card neutral">
    <div class="kpi-label">Trend Signal</div>
    <div class="kpi-value" style="font-size:1.1rem;padding-top:6px;">{kpis['trend']}</div>
    <div class="kpi-delta neu">7d MA vs 30d MA</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Chart ──
st.markdown('<div class="section-label">Price Chart · Closing Price + Moving Averages</div>',
            unsafe_allow_html=True)
chart_df = df.set_index("Date")[["Close", "MA7", "MA30"]]
st.line_chart(chart_df, height=340)

# ── Metrics Table + AI Summary ──
col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown('<div class="section-label">Key Metrics</div>',
                unsafe_allow_html=True)
    st.markdown(build_metrics_table(df), unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-label">AI Analyst Summary</div>',
                unsafe_allow_html=True)
    summary = get_ai_summary(kpis, question if run_analysis else "")
    st.markdown(f"""
    <div class="ai-summary-box">
      <div class="ai-tag">✦ AI GENERATED · SAMPLE ONLY</div>
      <div>{summary.replace(chr(10), '<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Raw data expander ──
with st.expander("🗃  View raw data", expanded=False):
    st.dataframe(
        df[["Date", "Close", "MA7", "MA30", "Volume", "Daily_Return"]]
        .sort_values("Date", ascending=False)
        .style.format({
            "Close": "${:.2f}", "MA7": "${:.2f}", "MA30": "${:.2f}",
            "Volume": "{:,.0f}", "Daily_Return": "{:.2%}",
        }),
        use_container_width=True, height=240,
    )
