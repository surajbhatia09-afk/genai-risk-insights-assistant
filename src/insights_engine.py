"""
Bridges the scored portfolio data (produced by the
credit-default-risk-dashboard project) and the LLM layer: builds grounded
context, fills prompt templates, and calls llm_client.generate().
"""

from __future__ import annotations

import pandas as pd

from llm_client import generate
from prompts import SYSTEM_PROMPT, account_explanation_prompt, portfolio_briefing_prompt, qa_prompt


def _portfolio_summary(df: pd.DataFrame) -> dict:
    return {
        "n_accounts": int(len(df)),
        "total_exposure": float(df["ead"].sum()),
        "expected_loss": float(df["expected_loss"].sum()),
        "expected_loss_rate": float(df["expected_loss"].sum() / max(df["ead"].sum(), 1)),
        "avg_pd": float(df["pd_score"].mean()),
        "pct_high_or_severe": float(df["risk_band"].isin(["High", "Severe"]).mean()),
    }


def _band_table(df: pd.DataFrame) -> str:
    band = (
        df.groupby("risk_band", observed=True)
        .agg(accounts=("account_id", "count"), exposure=("ead", "sum"), expected_loss=("expected_loss", "sum"))
        .reset_index()
    )
    return band.to_markdown(index=False)


def _segment_table(df: pd.DataFrame) -> str:
    seg = (
        df.groupby("age_band", observed=True)
        .agg(accounts=("account_id", "count"), expected_loss=("expected_loss", "sum"))
        .reset_index()
        .sort_values("expected_loss", ascending=False)
    )
    return seg.to_markdown(index=False)


def generate_portfolio_briefing(df: pd.DataFrame, mode: str = "auto") -> str:
    summary = _portfolio_summary(df)
    prompt = portfolio_briefing_prompt(summary, _band_table(df), _segment_table(df))
    return generate(SYSTEM_PROMPT, prompt, mode=mode)


def generate_account_explanation(df: pd.DataFrame, account_id: int, mode: str = "auto") -> str:
    row = df[df["account_id"] == account_id]
    if row.empty:
        return f"Account {account_id} not found in the scored portfolio."
    account = row.iloc[0][
        [
            "account_id", "credit_limit", "pd_score", "risk_band", "expected_loss",
            "utilization", "worst_delinquency_6m", "delinquency_trend", "payment_ratio_6m",
        ]
    ].to_dict()
    prompt = account_explanation_prompt(account)
    return generate(SYSTEM_PROMPT, prompt, mode=mode)


def answer_question(df: pd.DataFrame, question: str, mode: str = "auto") -> str:
    summary = _portfolio_summary(df)
    context_md = (
        f"Portfolio summary: {summary}\n\n"
        f"Risk band breakdown:\n{_band_table(df)}\n\n"
        f"Segment breakdown (age):\n{_segment_table(df)}\n\n"
        f"Top 10 highest expected-loss accounts:\n"
        f"{df.sort_values('expected_loss', ascending=False).head(10)[['account_id','pd_score','risk_band','expected_loss']].to_markdown(index=False)}"
    )
    prompt = qa_prompt(question, context_md)
    return generate(SYSTEM_PROMPT, prompt, mode=mode)
