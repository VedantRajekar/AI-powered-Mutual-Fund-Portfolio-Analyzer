def portfolio_summary_prompt(holdings_json: str, total_value: float) -> str:
    return f"""
You are a SEBI-registered investment advisor analyzing an Indian mutual fund portfolio.

Portfolio Current Value: Rs.{total_value:,.2f}
Holdings (JSON):
{holdings_json}

Analyze this portfolio and provide EXACTLY the following 5 sections:

---

## 1. Investment Summary
- Total Amount Invested: Calculate by summing investedValue from holdings
- Total Current Value: Rs.{total_value:,.2f}
- Absolute Gain/Loss: Current Value minus Invested Amount in Rs.

## 2. Overall Absolute Return
- Formula: ((Current Value - Invested Amount) / Invested Amount) x 100
- Show the formula with actual numbers and the final percentage
- Also mention approximate CAGR if investment period can be estimated

## 3. Best and Worst Performing Fund
- Best Performing Fund: Name, return percentage, reason it outperformed
- Worst Performing Fund: Name, return percentage, reason it underperformed
- Rank all funds from best to worst in a simple table

## 4. Comparison with Nifty 50
- Nifty 50 average annual return benchmark: 14%
- This portfolio return: calculated above
- Is the portfolio beating, matching, or lagging the Nifty 50?
- By how many percentage points is it ahead or behind?

## 5. One-Line Verdict
Give a single bold sentence verdict: is this portfolio performing WELL or POORLY and why?

---

Use Rs. for currency. Be specific with numbers. Keep it simple and easy to understand.
"""

def risk_profile_prompt(holdings_json: str) -> str:
    return f"""
You are an expert mutual fund advisor analyzing an Indian investor portfolio.

Holdings:
{holdings_json}

Provide EXACTLY the following sections:

## Implied Risk Profile
State clearly: Conservative / Moderate / Aggressive

## Evidence from Portfolio
- List exactly what in the portfolio supports this risk assessment
- Mention equity percentage, debt percentage, ELSS, mid-cap, large-cap breakdown

## Mismatch Warning
- Is the current allocation consistent or inconsistent for this risk profile?
- Any red flags?

## Suggested Ideal Allocation
Show a simple table comparing:
| Risk Profile | Equity % | Debt % | Gold/Other % |
|---|---|---|---|
| Conservative | ... | ... | ... |
| Moderate | ... | ... | ... |
| Aggressive | ... | ... | ... |
| This Portfolio | ... | ... | ... |

Use Rs. for currency. Be direct and specific.
"""

def chat_prompt(holdings_json: str, user_question: str, history: list):
    system = f"""You are an expert Indian mutual fund advisor.
The investor portfolio data:
{holdings_json}

Answer questions about their portfolio. Be concise and specific. Use Rs. for amounts.
Reference actual fund names and numbers from the portfolio in your answers.
"""
    messages = history + [{"role": "user", "content": user_question}]
    return system, messages