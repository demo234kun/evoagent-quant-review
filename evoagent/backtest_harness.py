"""Backtest pipeline: code review + sandboxed backtest merged into one report.

Mirrors :class:`evoagent.harness.ReviewHarness` but drives a user-submitted quant
strategy through :mod:`evoagent.strategy_sdk` instead of the agent runtime.  The
code-review half reuses the existing Reviewer (rules-only by default) so the same
finding taxonomy applies.
"""
from typing import Any, Dict, List, Optional

from .diff_parser import parse_unified_diff
from .market_data import MarketDataProvider
from .models import Finding, ReviewReport, Severity, TaskState, TraceEvent
from .reviewer import Reviewer
from .sandbox_runner import run_backtest_in_sandbox
from .store import TaskStore, utc_now


def _strategy_to_diff(code: str) -> str:
    lines = code.splitlines()
    header = (
        "diff --git a/strategy.py b/strategy.py\n"
        "--- /dev/null\n"
        "+++ b/strategy.py\n"
        "@@ -0,0 +1,%d @@\n" % (len(lines) + 1)
    )
    body = "\n".join("+" + line for line in lines)
    return header + body + "\n"


class BacktestHarness:
    def __init__(
        self, store: TaskStore, reviewer: Reviewer, settings,
        market_data: Optional[MarketDataProvider] = None,
    ):
        self.store = store
        self.reviewer = reviewer
        self.settings = settings
        self.market = market_data or MarketDataProvider(
            getattr(settings, "backtest_data_dir", "data/market")
        )

    def run(
        self, task_id: str, repository: str, strategy_code: str,
        params: Dict[str, Any], tenant_id: str = "default",
    ) -> ReviewReport:
        # 1) code review (reuse the existing Reviewer)
        findings = self._review_code(strategy_code)

        # 2) market data
        try:
            bars = self._load_bars(params)
        except Exception as exc:
            report = ReviewReport(
                repository=repository, pull_request=None,
                summary=self._summary(findings, "backtest failed: %s" % exc),
                risk=self._risk(findings),
                findings=findings, files_reviewed=["strategy.py"],
                reviewer=self.reviewer.name,
                backtest={"metrics": {}, "errors": [str(exc)]},
            )
            self.store.succeed(
                task_id, report,
                TraceEvent(1, TaskState.SUCCESS, "Backtest completed", utc_now()),
            )
            return report

        # 3) sandboxed backtest
        sandbox = run_backtest_in_sandbox(
            strategy_code, bars, params,
            timeout_seconds=getattr(self.settings, "backtest_sandbox_timeout_seconds", 60),
        )
        if sandbox["ok"]:
            backtest = {
                "metrics": sandbox["result"].get("metrics", {}),
                "equity_curve": sandbox["result"].get("equity_curve", []),
                "trades": sandbox["result"].get("trades", []),
                "errors": sandbox["result"].get("errors", []),
            }
        else:
            backtest = {"metrics": {}, "errors": [sandbox.get("error", "sandbox error")]}

        # 4) merged report
        risk = self._risk(findings)
        summary = self._summary(findings, "backtest completed")
        report = ReviewReport(
            repository=repository, pull_request=None,
            summary=summary, risk=risk,
            findings=findings, files_reviewed=["strategy.py"],
            reviewer=self.reviewer.name, backtest=backtest,
        )
        self.store.succeed(
            task_id, report,
            TraceEvent(1, TaskState.SUCCESS, "Backtest completed", utc_now()),
        )
        return report

    def _review_code(self, strategy_code: str) -> List[Finding]:
        try:
            diff = _strategy_to_diff(strategy_code)
            parsed = parse_unified_diff(diff)
            contextual = getattr(self.reviewer, "review_with_context", None)
            if contextual:
                return contextual(
                    "backtest", diff, parsed, repository="backtest", tenant_id="default"
                )
            return self.reviewer.review(diff, parsed)
        except Exception as exc:
            # never let code review break the backtest task
            return []

    def _load_bars(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        csv_path = params.get("csv_path")
        if csv_path:
            return self.market.load_csv(csv_path)
        symbol = str(params.get("symbol", ""))
        if not symbol:
            raise ValueError("params.symbol is required (or params.csv_path)")
        return self.market.fetch(
            symbol,
            str(params.get("start_date", "")),
            str(params.get("end_date", "")),
            str(params.get("adjust", "qfq")),
        )

    @staticmethod
    def _risk(findings: List[Finding]) -> str:
        severities = {item.severity for item in findings}
        if Severity.CRITICAL in severities or Severity.HIGH in severities:
            return "high"
        if Severity.MEDIUM in severities:
            return "medium"
        return "low"

    @staticmethod
    def _summary(findings: List[Finding], tail: str) -> str:
        if findings:
            return "Reviewed strategy code; found %d actionable issue(s). %s." % (
                len(findings), tail,
            )
        return "已审查策略代码；未检测到可处理的问题。%s。" % tail
