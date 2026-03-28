from groq import Groq
import os
from dotenv import load_dotenv
from prompts import portfolio_summary_prompt, risk_profile_prompt, chat_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

def _call(prompt: str, max_tokens: int = 2000) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content

def analyze_portfolio(portfolio: dict) -> str:
    try:
        holdings_json = portfolio["holdings"].to_json(orient="records", indent=2)
        prompt = portfolio_summary_prompt(holdings_json, portfolio["total_value"])
        return _call(prompt, max_tokens=2000)
    except Exception as e:
        return f"❌ Analysis failed: {e}"

def get_risk_profile(portfolio: dict) -> str:
    try:
        holdings_json = portfolio["holdings"].to_json(orient="records", indent=2)
        prompt = risk_profile_prompt(holdings_json)
        return _call(prompt, max_tokens=1000)
    except Exception as e:
        return f"❌ Risk profile failed: {e}"

def chat_with_portfolio(portfolio: dict, user_question: str, history: list) -> str:
    try:
        holdings_json = portfolio["holdings"].to_json(orient="records", indent=2)
        system, messages = chat_prompt(holdings_json, user_question, history)

        groq_messages = [{"role": "system", "content": system}]
        for msg in history:
            groq_messages.append({"role": msg["role"], "content": msg["content"]})
        groq_messages.append({"role": "user", "content": user_question})

        response = client.chat.completions.create(
            model=MODEL,
            messages=groq_messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Chat failed: {e}"