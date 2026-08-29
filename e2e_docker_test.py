"""End-to-end test against the running Docker container (coding-evoagent-1)."""
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:18080"

STRATEGY = '''
from evoagent.strategy_sdk import BaseStrategy, Context

API_KEY = "sk-1234567890abcdef1234567890abcdef"

class MyStrategy(BaseStrategy):
    def initialize(self, context):
        context.fast = 5
        context.slow = 20
        print("backtest initialized")

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


def main():
    status, body = post("/v1/auth/login", {
        "username": "admin", "password": "evoagent-local-admin",
    })
    print("LOGIN", status, "token_len=", len(body.get("access_token", "")))
    if status != 200:
        print("LOGIN_FAILED", body)
        return
    token = body["access_token"]

    params = {
        "csv_path": "/app/sample_600519.csv",
        "symbol": "600519",
        "initial_capital": 100000.0,
        "commission": 0.0003,
    }
    status, body = post("/v1/backtests", {
        "strategy_code": STRATEGY,
        "params": params,
        "repository": "backtest/demo",
    }, token=token)
    print("BACKTEST", status)
    if status != 201:
        print(json.dumps(body, ensure_ascii=False, indent=2)[:1500])
        return
    print("STATE", body.get("state"))
    print("METRICS", json.dumps(body.get("report", {}).get("backtest", {}).get("metrics", {}), ensure_ascii=False))
    eq = body.get("report", {}).get("backtest", {}).get("equity_curve", [])
    print("EQUITY_POINTS", len(eq), "LAST", eq[-1] if eq else None)
    print("FINDINGS_COUNT", len(body.get("report", {}).get("findings", [])))
    for f in body.get("report", {}).get("findings", []):
        print("  -", f.get("rule_id"), f.get("severity"))

    tid = body.get("task_id")
    if tid:
        try:
            req = urllib.request.Request(BASE + "/v1/tasks/%s/report" % tid)
            req.add_header("Authorization", "Bearer " + token)
            with urllib.request.urlopen(req, timeout=10) as r:
                md = r.read().decode("utf-8")
            idx = md.find("## Backtest")
            print("\n--- REPORT MARKDOWN (backtest) ---")
            print(md[idx:idx + 400] if idx >= 0 else md[:400])
        except Exception as exc:
            print("REPORT_FETCH_ERR", exc)


if __name__ == "__main__":
    main()
