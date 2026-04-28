from pydantic import BaseModel
from typing import Dict


class ClientProfile(BaseModel):
    age_range: str
    monthly_income: float
    monthly_expenses: float
    investment_purpose: str
    goal: str
    risk_tolerance: str
    time_horizon: str


class PortfolioRecommendation(BaseModel):
    allocation: Dict[str, int]
    profile: ClientProfile