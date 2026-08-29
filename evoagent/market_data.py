"""Market data access for backtests.

Primary source is AKShare (free A-share daily bars).  Fetched data is cached to disk
so that the backtest sandbox can run fully offline (the sandbox never needs network).
A CSV loader is provided as an offline fallback for demos without network access.
"""
import hashlib
import json
import os
from typing import Any, Dict, List, Optional


def _norm(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


class MarketDataProvider:
    def __init__(self, cache_dir: str = "data/market"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    # -- public API ---------------------------------------------------------
    def fetch(
        self, symbol: str, start: str, end: str, adjust: str = "qfq"
    ) -> List[Dict[str, Any]]:
        """Return normalized daily bars: {date, open, high, low, close, volume}."""
        cached = self._load_cache(symbol, start, end, adjust)
        if cached is not None:
            return cached
        bars = self._fetch_akshare(symbol, start, end, adjust)
        self._save_cache(symbol, start, end, adjust, bars)
        return bars

    def load_csv(self, path: str) -> List[Dict[str, Any]]:
        import csv

        bars: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                bars.append({
                    "date": str(row.get("date", "")).strip(),
                    "open": _norm(row.get("open")),
                    "high": _norm(row.get("high")),
                    "low": _norm(row.get("low")),
                    "close": _norm(row.get("close")),
                    "volume": _norm(row.get("volume")),
                })
        return bars

    # -- AKShare -------------------------------------------------------------
    def _fetch_akshare(
        self, symbol: str, start: str, end: str, adjust: str
    ) -> List[Dict[str, Any]]:
        try:
            import akshare as ak
        except ImportError as exc:
            raise RuntimeError(
                "akshare is not installed; install it or use the CSV upload fallback"
            ) from exc
        df = ak.stock_zh_a_hist(
            symbol=symbol, period="daily",
            start_date=start, end_date=end, adjust=adjust or "",
        )
        if df is None or len(df) == 0:
            raise RuntimeError("AKShare returned no data for %s" % symbol)
        bars: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            bars.append({
                "date": str(row.get("日期", "")),
                "open": _norm(row.get("开盘")),
                "high": _norm(row.get("最高")),
                "low": _norm(row.get("最低")),
                "close": _norm(row.get("收盘")),
                "volume": _norm(row.get("成交量")),
            })
        return bars

    # -- cache ---------------------------------------------------------------
    def _cache_path(self, symbol: str, start: str, end: str, adjust: str) -> str:
        key = "%s|%s|%s|%s" % (symbol, start, end, adjust)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return os.path.join(self.cache_dir, "%s_%s.json" % (symbol, digest))

    def _load_cache(
        self, symbol: str, start: str, end: str, adjust: str
    ) -> Optional[List[Dict[str, Any]]]:
        path = self._cache_path(symbol, start, end, adjust)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            return None

    def _save_cache(
        self, symbol: str, start: str, end: str, adjust: str,
        bars: List[Dict[str, Any]],
    ) -> None:
        path = self._cache_path(symbol, start, end, adjust)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(bars, handle, ensure_ascii=False)
        except OSError:
            pass
