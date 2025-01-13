import logging
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
from pybacktestchain.broker import Broker
from pybacktestchain.data_module import get_stocks_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class Tradesignals:
    broker: Broker
    max_allocation: float = 0.15  # Maximum allocation per asset

    def execute_trades(self, data: pd.DataFrame):

        if "Position" not in data.columns:
            raise KeyError("Missing 'Position' column in data. Ensure signals are generated.")

        portfolio_values = []  # To track portfolio value over time

        for date in sorted(data["Date"].unique()):
            daily_data = data[data["Date"] == date]
            prices = dict(zip(daily_data["ticker"], daily_data["Adj Close"]))

            # Calculate current portfolio value
            portfolio_value = self.broker.get_portfolio_value(market_prices=prices)

            for _, row in daily_data.iterrows():
                ticker = row["ticker"]
                signal = row["Position"]
                price = row["Adj Close"]
                max_position_value = self.broker.get_cash_balance() * self.max_allocation
                max_quantity = int(max_position_value / price)

                if signal == 1:  # Buy signal
                    quantity = min(max_quantity, int(self.broker.get_cash_balance() / price))
                    if quantity > 0:
                        self.broker.buy(ticker, quantity, price, date)

                elif signal == -1:  # Sell signal
                    if ticker in self.broker.positions:
                        self.broker.sell(ticker, self.broker.positions[ticker].quantity, price, date)

            # Append portfolio value for the current date
            portfolio_values.append({"Date": date, "Portfolio Value": portfolio_value})

        # Combine portfolio values into a DataFrame
        portfolio_values_df = pd.DataFrame(portfolio_values)

        # Compute Final Portfolio Value
        final_portfolio_value = portfolio_values_df.iloc[-1]["Portfolio Value"]

        # Compute Metrics
        portfolio_values_df["Daily Returns"] = portfolio_values_df["Portfolio Value"].pct_change().dropna()
        risk_free_rate = 0.01
        daily_excess_returns = portfolio_values_df["Daily Returns"] - (risk_free_rate / 252)
        sharpe_ratio = daily_excess_returns.mean() / daily_excess_returns.std()

        rolling_max = portfolio_values_df["Portfolio Value"].cummax()
        drawdown = (portfolio_values_df["Portfolio Value"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Return final results
        return {
            "Final Portfolio Value": final_portfolio_value,
            "Sharpe Ratio": sharpe_ratio,
            "Maximum Drawdown": max_drawdown
        }

@dataclass
class VolumeBacktest:
    initial_date: datetime
    final_date: datetime
    universe: List[str] = field(default_factory=lambda: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'INTC', 'CSCO', 'NFLX'])
    initial_cash: int = 1_000_000  # Initial cash in the portfolio
    verbose: bool = True
    broker: Broker = field(init=False)

    def __post_init__(self):
        self.broker = Broker(cash=self.initial_cash, verbose=self.verbose)

    def compute_signals(self, data: pd.DataFrame):

        logging.info("Generating volume-based signals...")
        data = data.sort_values(by=["ticker", "Date"])

        # Compute average volume over the last 15 days
        data["Avg Volume"] = data.groupby("ticker")["Volume"].transform(lambda x: x.rolling(15).mean())

        # Generate signals: 1 for high volume, -1 for low volume
        data["Position"] = 0
        data.loc[data["Volume"] > data["Avg Volume"] * 1.5, "Position"] = 1  # Buy signal
        data.loc[data["Volume"] < data["Avg Volume"] * 0.5, "Position"] = -1  # Sell signal

        data = data.dropna(subset=["Avg Volume"])  # Remove rows with NaN Avg Volume
        return data
