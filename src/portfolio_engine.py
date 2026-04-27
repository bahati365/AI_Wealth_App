from src.models import ClientProfile, PortfolioRecommendation
ETF_MAPPING = {
    "Equities": "VTI",
    "Bonds": "BND",
    "Cash": "SHV"
}

class PortfolioEngine:
    BASE_ALLOCATIONS = {
        "Low": {"Equities": 30, "Bonds": 55, "Cash": 15},
        "Medium": {"Equities": 60, "Bonds": 30, "Cash": 10},
        "High": {"Equities": 80, "Bonds": 15, "Cash": 5},
    }

    def generate(self, profile: ClientProfile) -> PortfolioRecommendation:
        allocation = self.BASE_ALLOCATIONS[profile.risk_tolerance].copy()

        allocation = self._adjust_for_goal(allocation, profile.goal)
        allocation = self._adjust_for_horizon(allocation, profile.time_horizon)

        return PortfolioRecommendation(allocation=allocation, profile=profile)

    def _adjust_for_goal(self, allocation: dict, goal: str) -> dict:
        if goal == "Income":
            allocation["Bonds"] += 10
            allocation["Equities"] -= 10
        elif goal == "Growth":
            allocation["Equities"] += 5
            allocation["Bonds"] -= 5

        return allocation

    def _adjust_for_horizon(self, allocation: dict, horizon: str) -> dict:
        if horizon == "0–3 years":
            allocation["Cash"] += 10
            allocation["Equities"] -= 10
        elif horizon == "7+ years":
            allocation["Equities"] += 5
            allocation["Cash"] -= 5

        return allocation