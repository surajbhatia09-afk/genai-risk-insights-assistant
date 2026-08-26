# GenAI Risk Insights Assistant

A generative-AI layer on top of a scored credit-risk portfolio: an
auto-generated portfolio briefing for a risk committee, plain-language
explanations of why a specific account was scored the way it was, and a
Q&A assistant that can only answer using the numbers actually in the data.

Designed as the natural "part 2" of **credit-default-risk-dashboard** — that
project produces `scored_portfolio.csv` (PD, risk band, expected loss per
account); this project turns those numbers into narrative.

## Why this project

Every 2026 analytics posting I looked at during my job search mentioned
GenAI in some form. This demonstrates the actual pattern — not "I used
ChatGPT," but a deliberately **grounded** LLM layer: every prompt states
explicitly that the model may only use the figures it's given, and must say
so if the data doesn't answer the question. That constraint matters more in
a risk/compliance context than almost anywhere else — a model that
quietly invents numbers is worse than no model at all.

## Quick start (free — no API key needed)

```bash
git clone <your-repo-url>
cd genai-risk-insights-assistant
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

It runs immediately against the bundled `sample_data/scored_portfolio_sample.csv`
in **offline demo mode** — no API key required. You'll see a templated
summary rather than a real LLM-generated one; the app tells you this on
screen.

## Turning on real GenAI output

1. Get an OpenAI API key: <https://platform.openai.com/api-keys> (pay-as-you-go;
   this app's prompts are short, expect a few cents total for a full test session
   using the `gpt-4o-mini` default model).
2. Set it as an environment variable — **never commit it to Git**:
   ```bash
   export OPENAI_API_KEY=sk-...          # macOS/Linux
   setx OPENAI_API_KEY "sk-..."          # Windows (new terminal after)
   ```
3. Re-run `streamlit run app.py` — the sidebar will show "✅ OPENAI_API_KEY detected."

Prefer a fully free/local model instead of paying for API calls? Swap in
[Ollama](https://ollama.com) running something like `llama3.1` locally —
add a branch to `src/llm_client.py::generate()` following the same pattern
as the OpenAI branch. The rest of the app doesn't need to change.

## Using your own data instead of the sample

The sidebar has three data-source options:

1. **Bundled sample** — 500 accounts, works immediately, no setup.
2. **Upload a scored CSV** — for anyone visiting the live deployed app,
   including strangers with no access to your machine. Run the
   `credit-default-risk-dashboard` app first (upload your own raw data there
   too, if you like), click its **"Download this scored portfolio as CSV"**
   button, then upload that file here. Required columns: `account_id`,
   `credit_limit`, `pd_score`, `risk_band`, `expected_loss`, `ead`, `age_band`.
3. **Local file path (advanced)** — only works when running on your own
   machine, not on a deployed app: point it directly at
   `../credit-default-risk-dashboard/data/processed/scored_portfolio.csv`.

## Project structure

```
genai-risk-insights-assistant/
├── app.py                    # Streamlit app — 3 tabs: briefing / explain / Q&A
├── src/
│   ├── llm_client.py         # swappable LLM call — OpenAI or free offline mode
│   ├── prompts.py            # prompt templates (the actual "prompt engineering")
│   └── insights_engine.py    # builds grounded context from the scored portfolio
├── sample_data/
│   └── scored_portfolio_sample.csv   # small bundled sample so this repo runs standalone
└── requirements.txt
```

## A note on the sample data

`scored_portfolio_sample.csv` is a small, clearly-synthetic sample — it
exists purely so this repo demos on its own without requiring the other
project to be run first. Use the "Upload a scored CSV" option for anything
beyond a first look.
