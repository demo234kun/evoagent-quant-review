"""Demonstrate that the QUANT CODE REVIEW actually runs on the live container.

Tests BOTH endpoints with a realistic quant strategy containing deliberate flaws:
  - hardcoded API key / token
  - debug print
  - full-position entry with no stop-loss / risk control
"""
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:18080"

STRATEGY = '''from evoagent.strategy_sdk import BaseStrategy, Context
import os

API_KEY = "sk-1234567890abcdef1234567890abcdef"
TOKEN = os.getenv("TOKEN", "hardcoded-token-xyz")

class MyStrategy(BaseStrategy):
    def initialize(self, context):
        context.fast = 5
        context.slow = 20
        print("init done")

    def on_bar(self, context, bar):
        if context.i < context.slow:
            return
        closes = [b.close for b in context.bars[:context.i + 1]]
        if len(closes) < context.slow:
            return
        fast_ma = sum(closes[-context.fast:]) / context.fast
        slow_ma = sum(closes[-context.slow:]) / context.slow
        if fast_ma > slow_ma:
            context.order_target_percent(1.0)
        else:
            context.order_target_percent(0.0)
'''

DIFF = (
    "diff --git a/strategies/my_strategy.py b/strategies/my_strategy.py\n"
    "new file mode 100644\n"
    "--- /dev/null\n"
    "+++ b/strategies/my_strategy.py\n"
    "@@ -0,0 +1,21 @@\n"
    + "".join("+" + line + "\n" for line in STRATEGY.splitlines())
)


def post(path, payload, token=None, timeout=90):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def show_findings(title, findings):
    print("\n### %s : %d finding(s)" % (title, len(findings)))
    for f in findings:
        print("  [%s] %s  (%s:%s)" % (
            f.get("severity", "?"), f.get("rule_id", "?"),
            f.get("path", "?"), f.get("line", "?")))
        if f.get("evidence"):
            print("      evidence: %s" % f.get("evidence"))


def main():
    status, body = post("/v1/auth/login", {
        "username": "admin", "password": "evoagent-local-admin"})
    print("LOGIN", status)
    token = body.get("access_token", "")

    # 1) Standalone quant code review (the core product)
    status, body = post("/v1/reviews", {
        "repository": "quant/strategies",
        "diff": DIFF,
        "mode": "rules-only",
    }, token=token)
    print("\n=== /v1/reviews ===", status)
    if status == 201:
        rep = body.get("report", {})
        show_findings("reviews", rep.get("findings", []))
        print("  summary:", rep.get("summary"))
    else:
        print(json.dumps(body, ensure_ascii=False)[:400])

    # 2) Integrated backtest + review
    status, body = post("/v1/backtests", {
        "strategy_code": STRATEGY,
        "params": {
            "csv_path": "/app/sample_600519.csv",
            "symbol": "600519",
            "initial_capital": 100000.0,
            "commission": 0.0003,
        },
        "repository": "backtest/demo",
    }, token=token)
    print("\n=== /v1/backtests ===", status, "state=", body.get("state"))
    if status == 201:
        rep = body.get("report", {})
        m = rep.get("backtest", {}).get("metrics", {})
        print("  backtest metrics:", json.dumps(m, ensure_ascii=False))
        show_findings("backtests.review", rep.get("findings", []))


if __name__ == "__main__":
    main()
