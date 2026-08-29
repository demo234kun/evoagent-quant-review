"""Platform-defined strategy contract and a minimal, dependency-free backtest engine.

Users implement a subclass of :class:`BaseStrategy` and the platform runs it through
:class:`BacktestEngine` against market data.  The engine intentionally uses only the
standard library so it can run inside a restricted subprocess without pandas/numpy.
"""
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Bar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Trade:
    entry_index: int
    entry_date: str
    entry_price: float
    exit_index: int
    exit_date: str
    exit_price: float
    shares: int
    pnl: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BacktestResult:
    equity_curve: List[Dict[str, float]]
    trades: List[Trade]
    metrics: Dict[str, float]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equity_curve": self.equity_curve,
            "trades": [t.to_dict() for t in self.trades],
            "metrics": self.metrics,
            "errors": self.errors,
        }


class Portfolio:
    def __init__(self, initial_cash: float):
        self.cash = float(initial_cash)
        self.shares = 0
        self.avg_price = 0.0


class Context:
    """State handed to a user strategy on every bar."""

    def __init__(self, bars: List[Bar], params: Dict[str, Any]):
        self.bars = bars
        self.params = params
        self.i = 0
        self.bar: Optional[Bar] = None
        self.portfolio = Portfolio(float(params.get("initial_capital", 10000.0)))
        self._target_shares: Optional[int] = None
        self._errors: List[str] = []

    def order_target_shares(self, shares: int) -> None:
        self._target_shares = max(0, int(shares))

    def order_target_percent(self, pct: float) -> None:
        pct = max(0.0, min(1.0, float(pct)))
        price = self.bar.close if self.bar else 0.0
        if price <= 0:
            return
        equity = self.portfolio.cash + self.portfolio.shares * price
        self._target_shares = int((equity * pct) // price)

    def order_value(self, value: float) -> None:
        price = self.bar.close if self.bar else 0.0
        if price <= 0:
            return
        self._target_shares = max(0, int(float(value) // price))

    def warn(self, message: str) -> None:
        self._errors.append(message)


class BaseStrategy:
    """Subclass this and implement :meth:`on_bar`."""

    def initialize(self, context: Context) -> None:  # pragma: no cover - default no-op
        pass

    def on_bar(self, context: Context, bar: Bar) -> None:
        raise NotImplementedError("strategies must implement on_bar(context, bar)")


class BacktestEngine:
    def __init__(self, commission: float = 0.0003, slippage: float = 0.0):
        self.commission = commission
        self.slippage = slippage

    def run(
        self, strategy_cls, bars: List[Bar], params: Dict[str, Any]
    ) -> BacktestResult:
        errors: List[str] = []
        if not bars:
            errors.append("no market data was provided")
            return BacktestResult([], [], {"total_return": 0.0}, errors)
        initial = float(params.get("initial_capital", 10000.0))
        commission = float(params.get("commission", self.commission))
        ctx = Context(bars, params)
        try:
            strategy = strategy_cls()
        except Exception as exc:  # strategy constructor crashed
            errors.append("strategy instantiation failed: %s" % exc)
            return BacktestResult([], [], {"total_return": 0.0}, errors)

        try:
            strategy.initialize(ctx)
        except Exception as exc:
            errors.append("initialize() failed: %s" % exc)
            return BacktestResult([], [], {"total_return": 0.0}, errors)

        cash = initial
        shares = 0
        avg_price = 0.0
        equity_curve: List[Dict[str, float]] = []
        trades: List[Trade] = []
        pending_entry: Optional[Dict[str, Any]] = None

        for i, bar in enumerate(bars):
            ctx.i = i
            ctx.bar = bar
            ctx._target_shares = None
            try:
                strategy.on_bar(ctx, bar)
            except Exception as exc:
                errors.append("on_bar at bar %d (%s) failed: %s" % (i, bar.date, exc))
                break

            target = ctx._target_shares
            if target is None:
                target = shares  # hold
            if target != shares:
                price = bar.close * (
                    1.0 + self.slippage if target > shares else 1.0 - self.slippage
                )
                price = max(price, 0.01)
                if target > shares:  # buy
                    buy_shares = target - shares
                    # cap by what the available cash can actually afford
                    afford = int(cash // (price * (1.0 + commission))) if price > 0 else 0
                    if buy_shares > afford:
                        buy_shares = afford
                    if buy_shares > 0:
                        cost = buy_shares * price * (1.0 + commission)
                        cash -= cost
                        new_total = shares * avg_price + buy_shares * price
                        shares = shares + buy_shares
                        avg_price = new_total / shares if shares else 0.0
                        pending_entry = {
                            "entry_index": i, "entry_date": bar.date,
                            "entry_price": price, "shares": buy_shares,
                        }
                else:  # sell
                    sell_shares = shares - target
                    proceeds = sell_shares * price * (1.0 - commission)
                    cash += proceeds
                    if pending_entry is not None:
                        trades.append(Trade(
                            entry_index=pending_entry["entry_index"],
                            entry_date=pending_entry["entry_date"],
                            entry_price=pending_entry["entry_price"],
                            exit_index=i, exit_date=bar.date, exit_price=price,
                            shares=sell_shares,
                            pnl=(price - pending_entry["entry_price"]) * sell_shares
                            - sell_shares * price * commission,
                        ))
                        pending_entry = None
                    shares = target
                    avg_price = 0.0

            equity = cash + shares * bar.close
            equity_curve.append({"date": bar.date, "equity": round(equity, 4)})

        # force-close any open position at the last bar for final metrics
        if shares > 0 and bars:
            last = bars[-1]
            price = max(last.close, 0.01)
            proceeds = shares * price * (1.0 - commission)
            cash += proceeds
            if pending_entry is not None:
                trades.append(Trade(
                    entry_index=pending_entry["entry_index"],
                    entry_date=pending_entry["entry_date"],
                    entry_price=pending_entry["entry_price"],
                    exit_index=len(bars) - 1, exit_date=last.date, exit_price=price,
                    shares=shares,
                    pnl=(price - pending_entry["entry_price"]) * shares,
                ))
            shares = 0

        final_equity = cash
        metrics = self._metrics(equity_curve, initial, trades)
        errors.extend(ctx._errors)
        return BacktestResult(equity_curve, trades, metrics, errors)

    @staticmethod
    def _metrics(
        equity_curve: List[Dict[str, float]], initial: float, trades: List[Trade]
    ) -> Dict[str, float]:
        import statistics

        if not equity_curve:
            return {"total_return": 0.0, "final_equity": initial}
        equities = [row["equity"] for row in equity_curve]
        final_equity = equities[-1]
        total_return = (final_equity / initial - 1.0) if initial else 0.0
        returns = []
        for a, b in zip(equities, equities[1:]):
            if a > 0:
                returns.append((b - a) / a)
        n = len(equities)
        annualized = ((1.0 + total_return) ** (252.0 / n) - 1.0) if n > 1 else 0.0
        if returns:
            mean_r = statistics.mean(returns)
            std_r = statistics.pstdev(returns) if len(returns) > 1 else 0.0
            sharpe = (mean_r / std_r * (252 ** 0.5)) if std_r > 0 else 0.0
        else:
            sharpe = 0.0
        peak = equities[0]
        max_dd = 0.0
        for eq in equities:
            if eq > peak:
                peak = eq
            if peak > 0:
                dd = (eq - peak) / peak
                if dd < max_dd:
                    max_dd = dd
        wins = sum(1 for t in trades if t.pnl > 0)
        win_rate = (wins / len(trades)) if trades else 0.0
        return {
            "initial_capital": round(initial, 2),
            "final_equity": round(final_equity, 2),
            "total_return": round(total_return * 100.0, 4),
            "annualized_return": round(annualized * 100.0, 4),
            "sharpe": round(sharpe, 4),
            "max_drawdown": round(max_dd * 100.0, 4),
            "win_rate": round(win_rate * 100.0, 2),
            "num_trades": len(trades),
        }
