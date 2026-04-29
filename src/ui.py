import pandas as pd
import plotly.express as px
import streamlit as st

from src.models import ClientProfile
from src.portfolio_engine import PortfolioEngine, ETF_MAPPING
from src.explanation_engine import ExplanationEngine
from src.market_data import MarketDataService

st.set_page_config(layout="wide")


ETF_DESCRIPTIONS = {
    "VTI": "Tracks the total US stock market, giving broad diversification and long-term growth potential.",
    "BND": "Provides exposure to US bonds, helping reduce volatility and adding income/stability.",
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
        monthly_income=st.sidebar.number_input(
            "Monthly Income ($)",
            min_value=0.0,
            value=3000.0,
            step=100.0
        ),
        monthly_expenses=st.sidebar.number_input(
            "Monthly Expenses ($)",
            min_value=0.0,
            value=2000.0,
            step=100.0),
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

    st.success("Your personalized portfolio is ready.")

    # Top: table + pie chart side by side
    table_col, chart_col = st.columns([1, 1])

    with table_col:
        st.subheader("Recommended Portfolio")
        st.dataframe(
            allocation_df,
            use_container_width=True,
            hide_index=True
        )

    with chart_col:
        st.subheader("Portfolio Allocation")
        fig = px.pie(
            allocation_df,
            values="Allocation (%)",
            names="Asset Class",
        )
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    monthly_surplus = profile.monthly_income - profile.monthly_expenses

    st.subheader("Monthly Investment Capacity")

    if monthly_surplus <= 0:
        st.error(
            "Based on your income and expenses, you may not have extra monthly cash flow to invest right now."
        )
    else:
        suggested_investment = monthly_surplus * 0.5
        savings_buffer = monthly_surplus * 0.5

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Monthly Income", f"${profile.monthly_income:,.0f}")

        with col2:
            st.metric("Monthly Expenses", f"${profile.monthly_expenses:,.0f}")

        with col3:
            st.metric("Available Surplus", f"${monthly_surplus:,.0f}")

    st.markdown(
        f"""
    <div style="background-color:#e6f0ff; padding:15px; border-radius:10px;">
    A reasonable starting point could be investing around <b>${suggested_investment:,.0f}/month</b>
    while keeping about <b>${savings_buffer:,.0f}/month</b> for savings, debt repayment, or emergency needs.
    </div>
    """,
        unsafe_allow_html=True
    )
    # Explanation
    st.subheader("Advisor Explanation")
    st.write(explanation_engine.generate(recommendation))

    st.divider()

    # ETF performance
    st.subheader("Your Portfolio – Market Performance")

    for asset, weight in recommendation.allocation.items():
        ticker = ETF_MAPPING.get(asset)

        if ticker is None:
            continue

        with st.container(border=True):
            st.markdown(f"### {asset} ({ticker}) — {weight}%")
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

    st.divider()

    # Bottom: research dropdown
    st.subheader("Explore Other Investments")

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
            with st.spinner(f"Fetching data for {selected_name}..."):
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

            with st.expander("View recent price data"):
                st.dataframe(price_history.tail(), use_container_width=True)

        except Exception as error:
            st.error(f"Could not fetch market data: {error}")

    st.warning(
        "Disclaimer: This is an educational simulation only and is not financial advice."
    )