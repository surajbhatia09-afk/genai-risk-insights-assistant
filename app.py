"""
GenAI Risk Insights Assistant
------------------------------
A GenAI layer on top of a scored credit-risk portfolio: an auto-generated
portfolio briefing, per-account risk explanations, and a grounded Q&A
assistant that can only answer from the numbers actually in the data.

Run:
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...      # optional — omit to run in free offline demo mode
    streamlit run app.py

Data: reads sample_data/scored_portfolio_sample.csv by default. Point it at
the real output of the credit-default-risk-dashboard project instead via the
sidebar to use your own trained model's scores.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent / "src"))
from insights_engine import answer_question, generate_account_explanation, generate_portfolio_briefing  # noqa: E402

st.set_page_config(page_title="GenAI Risk Insights Assistant", page_icon="🧠", layout="wide")

st.title("🧠 GenAI Risk Insights Assistant")
st.caption("Narrative layer on top of the credit-default-risk-dashboard model output.")

# --- Sidebar: data source + LLM mode ---
st.sidebar.header("Settings")

default_path = Path(__file__).resolve().parent / "sample_data" / "scored_portfolio_sample.csv"
data_path = st.sidebar.text_input("Scored portfolio CSV path", value=str(default_path))

import os

has_key = bool(os.getenv("OPENAI_API_KEY"))
mode_choice = st.sidebar.radio(
    "LLM mode",
    ["Auto (use API key if set)", "Force offline demo (free, no key)"],
    index=0 if has_key else 1,
)
mode = "auto" if mode_choice.startswith("Auto") else "offline"
st.sidebar.caption(
    "✅ OPENAI_API_KEY detected — real GenAI calls enabled." if has_key
    else "⚠️ No OPENAI_API_KEY set — running in free offline demo mode. "
         "See README.md to add a key."
)

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Couldn't find {data_path}")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📋 Portfolio Briefing", "🔍 Explain an Account", "💬 Ask the Assistant"])

with tab1:
    st.subheader("Auto-generated portfolio briefing")
    if st.button("Generate briefing", type="primary"):
        with st.spinner("Generating..."):
            briefing = generate_portfolio_briefing(df, mode=mode)
        st.markdown(briefing)
    else:
        st.info("Click **Generate briefing** — this sends the portfolio's summary "
                "statistics (never raw account-level data) as grounding context.")

with tab2:
    st.subheader("Explain why a specific account was scored the way it was")
    account_id = st.selectbox("Account ID", sorted(df["account_id"].unique().tolist()))
    if st.button("Explain this account"):
        with st.spinner("Generating..."):
            explanation = generate_account_explanation(df, account_id, mode=mode)
        st.markdown(explanation)

with tab3:
    st.subheader("Ask a question about the portfolio")
    st.caption("Answers are grounded only in portfolio summary stats + the top 10 highest-risk accounts.")
    question = st.text_input("Your question", placeholder="Which risk band is driving the most expected loss?")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            answer = answer_question(df, question, mode=mode)
        st.markdown(answer)

with st.expander("How this is grounded (and why that matters)"):
    st.markdown(
        """
        Every prompt sent to the model includes an explicit instruction: **only use the
        numbers provided, and say so plainly if the data doesn't answer the question.**

        In a risk/compliance context, an assistant that quietly invents plausible-sounding
        numbers is worse than no assistant at all. This project treats that as a hard
        constraint on the prompt design, not an afterthought — see `src/prompts.py`.
        """
    )
