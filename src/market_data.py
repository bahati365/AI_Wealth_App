import yfinance as yf
import pandas as pd


class MarketDataService:
    def get_price_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        ticker = ticker.upper().strip()

        data = yf.download(
            ticker,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            raise ValueError(f"No market data found for {ticker}.")

        data = data.reset_index()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        return data

    def get_latest_price(self, ticker: str) -> float:
        data = self.get_price_history(ticker, period="5d")
        latest_price = data["Close"].dropna().iloc[-1]
        return round(float(latest_price), 2)