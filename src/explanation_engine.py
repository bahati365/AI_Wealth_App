import os
import streamlit as st
from anthropic import Anthropic
from typing import Optional

from src.models import PortfolioRecommendation


def get_anthropic_api_key() -> Optional [str]:
    # Local development
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Streamlit Cloud deployment
    if not api_key:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)

    return api_key


class ExplanationEngine:
    def __init__(self):
        api_key = get_anthropic_api_key()

        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None


class ExplanationEngine:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None

    def generate(self, recommendation: PortfolioRecommendation) -> str:
        if self.client is None:
            return self._fallback_explanation(recommendation)

        profile = recommendation.profile
        allocation = recommendation.allocation

        prompt = f"""
You are an educational wealth advisor simulator.

Explain this portfolio recommendation in plain English.

Client profile:
- Age range: {profile.age_range}
- Investment purpose: {profile.investment_purpose}
- Investment style: {profile.goal}
- Risk tolerance: {profile.risk_tolerance}
- Time horizon: {profile.time_horizon}

Portfolio allocation:
- Equities: {allocation["Equities"]}%
- Bonds: {allocation["Bonds"]}%
- Cash: {allocation["Cash"]}%

Rules:
- Do not say returns are guaranteed.
- Do not give licensed financial advice.
- Explain tradeoffs clearly.
- Keep it short, practical, and beginner-friendly.
- Mention this is educational only.
"""

        response = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=350,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.content[0].text

    def _fallback_explanation(self, recommendation: PortfolioRecommendation) -> str:
        profile = recommendation.profile
        allocation = recommendation.allocation

        return f"""
You are investing for **{profile.investment_purpose.lower()}** with a **{profile.time_horizon.lower()}** time horizon.

Recommended allocation:

- **Equities:** {allocation["Equities"]}%
- **Bonds:** {allocation["Bonds"]}%
- **Cash:** {allocation["Cash"]}%

This is using the fallback explanation because no Claude API key was found.
"""