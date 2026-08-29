"""End-to-end test for the backtest platform, run directly (no Docker needed).

Starts the real EvoAgent HTTP server with auth enabled on a throwaway SQLite DB,
then drives: login -> POST /v1/backtests -> inspect report.

Market data comes from a local CSV (offline fallback) so the test does not depend
on AKShare network access. The same code path runs with real AKShare when a symbol
is supplied instead of csv_path.
"""
import csv
import json
import os
import random
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "data", "market", "sample_600519.csv")

# --- force a deterministic, isolated test configuration -------------------
os.environ["EVOAGENT_AUTH_REQUIRED"] = "true"
os.environ["EVOAGENT_AUTH_SECRET"] = "test-secret-ats-backtest-e2e-1234567890ab"
os.environ["EVOAGENT_BOOTSTRAP_ADMIN_USERNAME"] = "admin"
os.environ["EVOAGENT_BOOTSTRAP_ADMIN_PASSWORD"] = "test-password-123"
os.environ["EVOAGENT_HOST"] = "127.0.0.1"
os.environ["EVOAGENT_PORT"] = "8099"
os.environ["EVOAGENT_DB_PATH"] = os.path.join(tempfile.gettempdir(), "e2e_backtest.db")


def make_sample_csv(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rng = random.Random(42)
    price = 1700.0
    rows = []
    for d in range(1, 121):  # 120 trading days
        date = "2024-%02d-%02d" % ((d - 1) // 20 + 1, (d - 1) % 20 + 1)
        drift = rng.uniform(-8, 9)
        openp = price
        close = max(1.0, price + drift)
        high = max(openp, close) + rng.uniform(0, 6)
        low = min(openp, close) - rng.uniform(0, 6)
        vol = rng.uniform(2_000_000, 6_000_000)
        rows.append({
            "date": date, "open": round(openp, 2), "high": round(high, 2),
            "low": round(low, 2), "close": round(close, 2), "volume": round(vol, 0),
        })
        price = close
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["date", "open", "high", "low", "close", "volume"]
        )
        writer.writeheader()
        writer.writerows(rows)


STRATEGY = '''
from evoagent.strategy_sdk import BaseStrategy, Context

# Intentionally weak secret + debug print so the code review can flag them.
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


def post(path, payload, token=None, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8099" + path, data=data, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main():
    make_sample_csv(CSV_PATH)

    from evoagent.config import Settings
    from evoagent.service import ReviewService
    from evoagent.api import ApiHandler

    settings = Settings.from_env()
    service = ReviewService(settings)
    handler = type("TestApiHandler", (ApiHandler,), {
        "service": service, "settings": settings
    })
    server = ThreadingHTTPServer((settings.host, settings.port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # wait for health
    for _ in range(50):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8099/health", timeout=5) as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(0.3)
    else:
        print("SERVER_FAILED_TO_START")
        return

    # 1) login
    status, body = post("/v1/auth/login", {
        "username": "admin", "password": "test-password-123",
    })
    print("LOGIN", status, "token_len=", len(body.get("access_token", "")))
    if status != 200:
        print("LOGIN_FAILED", body)
        return
    token = body["access_token"]

    # 2) backtest
    params = {
        "csv_path": CSV_PATH,
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
    print("BACKTEST_METRICS",
          json.dumps(body.get("report", {}).get("backtest", {}).get("metrics", {}),
                     ensure_ascii=False))
    equity = body.get("report", {}).get("backtest", {}).get("equity_curve", [])
    print("EQUITY_POINTS", len(equity),
          "FIRST", equity[0] if equity else None,
          "LAST", equity[-1] if equity else None)
    print("FINDINGS_COUNT", len(body.get("report", {}).get("findings", [])))

    # 3) fetch report markdown (with auth) to confirm backtest section renders
    if status == 201 and body.get("task_id"):
        tid = body["task_id"]
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8099/v1/tasks/%s/report" % tid
            )
            req.add_header("Authorization", "Bearer " + token)
            with urllib.request.urlopen(req, timeout=10) as r:
                md = r.read().decode("utf-8")
            print("\n--- REPORT MARKDOWN (backtest section) ---")
            print(md[md.find("## Backtest"):] if "## Backtest" in md else md[:800])
        except Exception as exc:
            print("REPORT_FETCH_ERR", exc)

    server.shutdown()


if __name__ == "__main__":
    main()
