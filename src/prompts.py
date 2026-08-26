"""
Prompt templates. Kept in one place, separate from the calling code, so
they're easy to iterate on and review — this is the actual "prompt
engineering" artifact of the project.

Grounding rule baked into every system prompt: the assistant may ONLY use
numbers given to it in the user prompt. This matters for a risk/compliance
context — an assistant that quietly invents plausible-sounding numbers is
worse than useless in this domain.
"""

SYSTEM_PROMPT = """You are a risk-analytics assistant supporting a credit portfolio review.

Rules:
- Only use the figures given to you in the data below. Never invent, estimate,
  or round numbers that weren't provided.
- If the data provided doesn't answer the question, say so plainly instead of
  guessing.
- Write for a risk manager audience: concise, specific, no filler, no hedging
  language like "it appears that" — state what the data shows.
- When you flag a concern, name the specific metric and value that supports it.
"""


def portfolio_briefing_prompt(summary: dict, band_table_md: str, segment_table_md: str) -> str:
    return f"""Write a 4-6 sentence portfolio risk briefing for a risk committee, using only this data:

PORTFOLIO SUMMARY
- Accounts: {summary['n_accounts']:,}
- Total exposure (EAD): ${summary['total_exposure']:,.0f}
- Expected loss: ${summary['expected_loss']:,.0f}
- Expected loss rate: {summary['expected_loss_rate']:.2%}
- Average PD: {summary['avg_pd']:.2%}
- Share of accounts High/Severe risk: {summary['pct_high_or_severe']:.1%}

RISK BAND BREAKDOWN
{band_table_md}

SEGMENT BREAKDOWN (by age band)
{segment_table_md}

Cover: overall portfolio health, which risk band/segment is driving expected loss,
and one thing worth watching next review cycle."""


def account_explanation_prompt(account: dict) -> str:
    rows = "\n".join(f"- {k}: {v}" for k, v in account.items())
    return f"""Explain in 3-4 sentences why this specific account was scored the way it was,
using only the fields below. Name the specific factors driving the score.

ACCOUNT DATA
{rows}"""


def qa_prompt(question: str, context_md: str) -> str:
    return f"""Answer this question using ONLY the data below. If the data doesn't contain
the answer, say so explicitly rather than guessing.

QUESTION: {question}

AVAILABLE DATA
{context_md}"""
