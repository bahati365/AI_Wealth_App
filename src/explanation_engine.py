import os
from openai import OpenAI
from src.models import PortfolioRecommendation


class ExplanationEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
    def generate(self, recommendation: PortfolioRecommendation) -> str:
        profile = recommendation.profile
        allocation = recommendation.allocation

        prompt = f"""
You are an educational AI wealth advisor simulator.

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
- Do not say this is guaranteed.
- Do not give personalized licensed financial advice.
- Explain tradeoffs clearly.
- Mention that this is educational only.
- Keep it short and practical.
"""

        if self.client is None:
            return self._fallback_explanation(recommendation)

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return response.output_text

    def _fallback_explanation(self, recommendation: PortfolioRecommendation) -> str:
        profile = recommendation.profile
        allocation = recommendation.allocation

        return f"""
You are investing for **{profile.investment_purpose.lower()}** with a **{profile.time_horizon.lower()}** time horizon.

Recommended allocation:

- **Equities:** {allocation["Equities"]}%
- **Bonds:** {allocation["Bonds"]}%
- **Cash:** {allocation["Cash"]}%

This explanation is currently using the fallback rule-based version because no OpenAI API key was found.
"""