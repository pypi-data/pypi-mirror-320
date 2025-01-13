from dataclasses import dataclass, field
import logging
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
from pybacktestchain.broker import Broker
from pybacktestchain.data_module import get_stocks_data

@dataclass
class BacktestRating:
    sharpe_threshold: float = 1.0
    max_drawdown_threshold: float = -0.4

    def rate_backtest(self, metrics: dict) -> float:
        sharpe_ratio = metrics.get("Sharpe Ratio")
        max_drawdown = metrics.get("Maximum Drawdown")
        final_portfolio_value = metrics.get("Final Portfolio Value")

        if sharpe_ratio is None or max_drawdown is None or final_portfolio_value is None:
            return 0.0  # Insufficient data yields the lowest score

        # Sharpe Ratio Score (25% weight)
        sharpe_score = min(2.5, max(0, sharpe_ratio / self.sharpe_threshold * 2.5))

        # Maximum Drawdown Score (25% weight, inverted scale)
        if max_drawdown <= self.max_drawdown_threshold:
            max_drawdown_score = 0
        else:
            max_drawdown_score = min(2.5, max(0, (1 + max_drawdown / self.max_drawdown_threshold) * 2.5))

        # Final Portfolio Value Score (50% weight)
        initial_portfolio_value = 1_000_000  
        portfolio_growth = final_portfolio_value / initial_portfolio_value
        portfolio_value_score = min(5, max(0, (portfolio_growth - 1) * 5))  # Scaled based on growth above initial value

        # Final weighted score
        total_score = sharpe_score + max_drawdown_score + portfolio_value_score
        return round(min(total_score, 10), 2)


@dataclass
class BacktestEvaluator:
    def compute_metrics(self, trades: dict):
        logging.info("Calculating performance metrics...")

        # Validate input
        if not trades:
            logging.error("No trades executed. Cannot calculate metrics.")
            return {
                "Sharpe Ratio": None,
                "Maximum Drawdown": None,
                "Final Portfolio Value": None
            }

        # Extract necessary data
        portfolio_value = trades.get("Final Portfolio Value")
        daily_returns = trades.get("Daily Returns")
        max_drawdown = trades.get("Maximum Drawdown")

        if portfolio_value is None:
            logging.error("Final Portfolio Value is missing. Cannot calculate metrics.")
            return {
                "Sharpe Ratio": None,
                "Maximum Drawdown": None,
                "Final Portfolio Value": None
            }

        if daily_returns is None or not isinstance(daily_returns, pd.Series):
            logging.error("Daily Returns are missing or not a valid pandas Series. Cannot calculate metrics.")
            return {
                "Sharpe Ratio": None,
                "Maximum Drawdown": None,
                "Final Portfolio Value": portfolio_value
            }

        # Calculate Sharpe Ratio
        try:
            risk_free_rate = 0.01  # Annualized risk-free rate
            daily_excess_returns = daily_returns - (risk_free_rate / 252)
            sharpe_ratio = daily_excess_returns.mean() / daily_excess_returns.std()
        except Exception as e:
            logging.error(f"Error calculating Sharpe Ratio: {e}")
            sharpe_ratio = None

        # Return the computed metrics
        return {
            "Sharpe Ratio": sharpe_ratio,
            "Maximum Drawdown": max_drawdown,
            "Final Portfolio Value": portfolio_value
        }