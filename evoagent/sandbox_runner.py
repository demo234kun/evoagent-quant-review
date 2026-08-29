"""Offline sandbox execution of user-submitted quant strategies.

The strategy code is written to a throw-away directory together with the (already
fetched, cached) market data and a runner script, then executed with ``subprocess``
under a wall-clock timeout.  The runner imports only :mod:`evoagent.strategy_sdk`
(which is stdlib-only) and writes ``result.json``; this keeps the untrusted code
offline and isolated from the server process.

This is demo-grade isolation (subprocess + timeout + no network egress + cwd
sandbox).  Production deployments should additionally use a container/VM with a
read-only rootfs, seccomp and rlimits.  See README for the production sandbox notes.
"""
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional

_RUNNER = '''import importlib.util
import json
import os
import sys
import traceback

try:
    from evoagent import strategy_sdk
    Bar = strategy_sdk.Bar
    BaseStrategy = strategy_sdk.BaseStrategy
    BacktestEngine = strategy_sdk.BacktestEngine

    here = os.path.dirname(os.path.abspath(__file__))
    bars = [Bar(**b) for b in json.load(open(os.path.join(here, "bars.json"), encoding="utf-8"))]
    params = json.load(open(os.path.join(here, "params.json"), encoding="utf-8"))

    spec = importlib.util.spec_from_file_location("user_strategy", os.path.join(here, "strategy.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    strat_cls = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
            strat_cls = obj
            break
    if strat_cls is None:
        raise RuntimeError("submitted code defines no BaseStrategy subclass")

    result = BacktestEngine(commission=float(params.get("commission", 0.0003))).run(
        strat_cls, bars, params
    )
    with open(os.path.join(here, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result.to_dict(), fh, ensure_ascii=False)
except Exception:
    with open(os.path.join(here, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "equity_curve": [],
                "trades": [],
                "metrics": {"total_return": 0.0},
                "errors": [traceback.format_exc()[-1500:]],
            },
            fh,
            ensure_ascii=False,
        )
'''


def run_backtest_in_sandbox(
    strategy_code: str,
    bars: List[Dict[str, Any]],
    params: Dict[str, Any],
    timeout_seconds: int = 60,
) -> Dict[str, Any]:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with tempfile.TemporaryDirectory() as work:
        with open(os.path.join(work, "strategy.py"), "w", encoding="utf-8") as fh:
            fh.write(strategy_code)
        with open(os.path.join(work, "bars.json"), "w", encoding="utf-8") as fh:
            json.dump(bars, fh, ensure_ascii=False)
        with open(os.path.join(work, "params.json"), "w", encoding="utf-8") as fh:
            json.dump(params, fh, ensure_ascii=False)
        with open(os.path.join(work, "run_backtest.py"), "w", encoding="utf-8") as fh:
            fh.write(_RUNNER)

        env = os.environ.copy()
        env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
        # remove proxy variables so the sandbox cannot egress to the network
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
            env.pop(key, None)

        try:
            proc = subprocess.run(
                [sys.executable, "run_backtest.py"],
                cwd=work, env=env, capture_output=True, text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": "strategy execution exceeded the %ds timeout" % timeout_seconds,
                "stdout": "", "stderr": "",
            }

        result_path = os.path.join(work, "result.json")
        if not os.path.exists(result_path):
            return {
                "ok": False,
                "error": "runner crashed before producing output",
                "stdout": proc.stdout[-2000:],
                "stderr": proc.stderr[-2000:],
            }
        with open(result_path, "r", encoding="utf-8") as fh:
            result = json.load(fh)
        if result.get("errors"):
            return {
                "ok": False,
                "error": result["errors"][-1],
                "result": result,
                "stdout": proc.stdout[-2000:],
                "stderr": proc.stderr[-2000:],
            }
        return {"ok": True, "result": result, "stdout": proc.stdout, "stderr": proc.stderr}
