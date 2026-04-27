import pandas as pd
import plotly.express as px
import streamlit as st

from src.models import ClientProfile
from src.portfolio_engine import PortfolioEngine, ETF_MAPPING
from src.explanation_engine import ExplanationEngine
from src.market_data import MarketDataService


ETF_DESCRIPTIONS = {
    "VTI": "Tracks the total US stock market, giving broad diversification and long-term growth potential.",
    "BND": "Provides exposure to US bonds, helping reduce volatility and add income/stability.",
    "SHV": "Focuses on short-term US Treasury bills, useful for liquidity and capital preservation.",
    "SPY": "Tracks the S&P 500, representing many of the largest US companies.",
    "QQQ": "Tracks the Nasdaq-100, with higher exposure to technology and growth companies.",
    "AAPL": "Apple is a large-cap technology company with strong consumer and services businesses.",
    "MSFT": "Microsoft is a major software, cloud, and AI infrastructure company.",
    "NVDA": "Nvidia is a major semiconductor company tied strongly to AI and GPU demand.",
}


def render_sidebar() -> tuple[ClientProfile, bool]:
    st.sidebar.header("Client Profile")

    profile = ClientProfile(
        age_range=st.sidebar.selectbox(
            "Age Range",
            ["18–25", "26–35", "36–45", "46–60", "60+"]
        ),
        investment_purpose=st.sidebar.selectbox(
            "What are you investing for?",
            [
                "Emergency fund",
                "Buying a car",
                "Down payment",
                "Education",
                "Retirement",
                "Building wealth",
                "Passive income",
            ]
        ),
        goal=st.sidebar.selectbox(
            "Investment Style",
            ["Preserve money", "Balanced growth", "Aggressive growth", "Income"]
        ),
        risk_tolerance=st.sidebar.selectbox(
            "Risk Tolerance",
            ["Low", "Medium", "High"]
        ),
        time_horizon=st.sidebar.selectbox(
            "Time Horizon",
            ["0–2 years", "3–5 years", "6–10 years", "10+ years"]
        ),
    )

    generate = st.sidebar.button("Generate Portfolio")
    return profile, generate


def render_recommendation(profile: ClientProfile) -> None:
    portfolio_engine = PortfolioEngine()
    explanation_engine = ExplanationEngine()
    market_data_service = MarketDataService()

    recommendation = portfolio_engine.generate(profile)

    allocation_df = pd.DataFrame({
        "Asset Class": list(recommendation.allocation.keys()),
        "Allocation (%)": list(recommendation.allocation.values()),
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Recommended Portfolio")
        st.dataframe(allocation_df, use_container_width=True)

    with col2:
        st.subheader("Portfolio Allocation")
        fig = px.pie(
            allocation_df,
            values="Allocation (%)",
            names="Asset Class",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Why This Portfolio?")

    st.write(
        f"""
        You are investing for **{profile.investment_purpose.lower()}** with a **{profile.time_horizon.lower()}** time horizon.
        Your selected style is **{profile.goal.lower()}** and your risk tolerance is **{profile.risk_tolerance.lower()}**.
        """
    )

    st.subheader("Your Portfolio – Market Performance")

    for asset, weight in recommendation.allocation.items():
        ticker = ETF_MAPPING.get(asset)

        if ticker is None:
            continue

        st.write(f"### {asset} ({ticker}) — {weight}%")
        st.caption(ETF_DESCRIPTIONS.get(ticker, ""))

        try:
            price_history = market_data_service.get_price_history(
                ticker=ticker,
                period="1y"
            )

            chart_data = price_history[["Date", "Close"]].dropna()
            chart_data = chart_data.set_index("Date")

            latest_price = round(float(chart_data["Close"].iloc[-1]), 2)
            one_year_return = (
                (chart_data["Close"].iloc[-1] / chart_data["Close"].iloc[0]) - 1
            ) * 100

            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:
                st.metric(f"{ticker} Latest Price", f"${latest_price}")

            with metric_col2:
                st.metric(f"{ticker} 1Y Return", f"{one_year_return:.2f}%")

            st.line_chart(chart_data)

        except Exception as error:
            st.error(f"Error loading {ticker}: {error}")

    st.subheader("Research Another Investment")

    ticker_options = {
        "S&P 500 ETF (SPY)": "SPY",
        "Total US Market ETF (VTI)": "VTI",
        "Nasdaq 100 ETF (QQQ)": "QQQ",
        "US Bond ETF (BND)": "BND",
        "Short-Term Treasury ETF (SHV)": "SHV",
        "Apple (AAPL)": "AAPL",
        "Microsoft (MSFT)": "MSFT",
        "Nvidia (NVDA)": "NVDA",
    }

    selected_name = st.selectbox(
        "Choose an investment to research",
        list(ticker_options.keys())
    )

    selected_ticker = ticker_options[selected_name]

    if st.button("Fetch Market Data"):
        try:
            price_history = market_data_service.get_price_history(
                ticker=selected_ticker,
                period="1y"
            )

            chart_data = price_history[["Date", "Close"]].dropna()
            chart_data = chart_data.set_index("Date")

            latest_price = round(float(chart_data["Close"].iloc[-1]), 2)
            one_year_return = (
                (chart_data["Close"].iloc[-1] / chart_data["Close"].iloc[0]) - 1
            ) * 100

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label=f"Latest Price for {selected_name}",
                    value=f"${latest_price}"
                )

            with col2:
                st.metric(
                    label="1Y Return",
                    value=f"{one_year_return:.2f}%"
                )

            st.caption(ETF_DESCRIPTIONS.get(selected_ticker, ""))
            st.line_chart(chart_data)

            st.write("Recent price data:")
            st.dataframe(price_history.tail(), use_container_width=True)

        except Exception as error:
            st.error(f"Could not fetch market data: {error}")

    st.subheader("Advisor Explanation")
    st.write(explanation_engine.generate(recommendation))

    st.warning(
        "Disclaimer: This is an educational simulation only and is not financial advice."
    )