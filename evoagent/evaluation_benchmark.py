"""Deterministic benchmark corpus and reviewers for local Evaluation Harness demos."""
import difflib
import os
import re
from typing import Dict, List, Tuple

from .diff_parser import ParsedDiff, parse_unified_diff
from .evaluation_harness import RULE_TO_CWE
from .models import Finding, Severity
from .reviewer import Reviewer


class ContextRuleReviewer(Reviewer):
    """Reserved deterministic scanner used by the controlled benchmark.

    The historical class name is kept for compatibility.  All quant review
    rules live in `LocalRuleReviewer`, so this scanner is intentionally empty
    to avoid duplicate findings across evaluation arms.
    """

    name = "context-security-reliability-agent"
    RULES: list = []

    def review(self, diff: str, parsed: ParsedDiff) -> List[Finding]:
        findings = []
        for line in parsed.added_lines:
            for rule_id, severity, pattern in self.RULES:
                if not pattern.search(line.content):
                    continue
                findings.append(Finding(
                    rule_id=rule_id,
                    severity=severity,
                    title="Supplemental benchmark finding",
                    explanation=(
                        "The changed line matches a context-sensitive security or reliability "
                        "risk that requires evidence review."
                    ),
                    path=line.path,
                    line=line.line,
                    evidence=line.content.strip()[:240],
                    fix="Replace the unsafe operation with a constrained, validated alternative.",
                    test="Add a focused reproduction and run compilation plus regression tests.",
                    confidence=0.86,
                ))
        return findings


def _risk_scenarios() -> List[dict]:
    scenarios = []

    def add(
        rule_id: str, severity: str, line: str, risk_pattern: str,
        required: str, count: int = 1, repairable: bool = True,
    ) -> None:
        for number in range(count):
            scenarios.append({
                "name": "%s-%02d" % (rule_id.lower(), number + 1),
                "rule_id": rule_id,
                "cwe": RULE_TO_CWE[rule_id],
                "severity": severity,
                "line": line.format(n=number + 1),
                "risk_pattern": risk_pattern,
                "required_after_patterns": [required] if required else [],
                "auto_fixable": repairable,
            })

    # 量化风险场景：覆盖未来函数、数据泄露、幸存者偏差、交易安全、执行成本、
    # 过拟合、数据质量。每条新增行经过设计，只触发其目标规则，便于精确评测。
    # 量化风险场景：覆盖未来函数、数据泄露、幸存者偏差、交易安全、执行成本、
    # 过拟合、数据质量。每条新增行经过设计，只触发其目标规则，便于精确评测。
    # 样本量已扩大（80 条风险）以支撑消融检验所需的更稳健指标。
    add("QUANT-FF-SHIFT-NEG", "critical", "signal = df['close'].shift(-1)", r"\.shift\(-", "", 6, False)
    add("QUANT-FF-REF-NEG", "critical", "x = ref(close, -1)", r"ref\(", "", 5, False)
    add("QUANT-FF-DATETIME-NOW", "high", "now = datetime.now()", r"datetime\.now", "", 4, False)
    add("QUANT-FF-GETPRICE-NOW", "high", "prices = get_price('000001.XSHE', end_date=context.current_dt)", r"current_dt", "", 4, False)
    add("QUANT-FF-CHEAT-CLOSE", "high", "cerebro.broker.set_coc(True)", r"set_coc", "", 4, False)
    add("QUANT-LK-FULL-NORM", "high", "Xs = scaler.fit_transform(X)", r"fit_transform", "", 4, False)
    add("QUANT-LK-FULL-ZSCORE", "high", "z = (df['close'] - df['close'].mean()) / df['close'].std()", r"\.mean\(", "", 4, False)
    add("QUANT-LK-FORWARD-FILL", "medium", "df = df.fillna(method='bfill')", r"bfill", "", 4, False)
    add("QUANT-LK-STATDATE", "medium", "q = get_fundamentals(query, statDate='2023-03-31')", r"statDate", "", 4, False)
    add("QUANT-LK-INDEX-NOW", "medium", "stocks = get_index_stocks('000300.XSHG')", r"get_index_stocks", "", 4, False)
    add("QUANT-SEC-HARDCODED-KEY", "high", 'api_key = "sk-live-abcdef123456"', r"api_key\s*=", "", 5, False)
    add("QUANT-SEC-NO-RISK", "medium", "order_target_percent(context.portfolio, 1.0)", r"1\.0", "", 4, False)
    add("QUANT-EX-ZERO-SLIP", "medium", "cerebro.broker.set_slippage(slip_perc=0)", r"slip_perc", "", 4, False)
    add("QUANT-EX-ZERO-COMM", "medium", "cerebro.broker.set_commission(commission=0)", r"commission", "", 4, False)
    add("QUANT-OF-OPTSTRATEGY", "medium", "cerebro.optstrategy(MyStrategy, period=range(5, 20))", r"optstrategy", "", 4, False)
    add("QUANT-OF-GRIDSEARCH", "medium", "grid = GridSearchCV(model, params)", r"GridSearchCV", "", 4, False)
    add("QUANT-DQ-ADJUST-POST", "high", "prices = get_price('000001.XSHE', fq='post')", r"fq='post'", "", 4, False)
    add("QUANT-DQ-FILLNA0", "low", "df = df.fillna(0)", r"fillna\(0", "", 4, False)
    add("QUANT-REL-DEBUG-PRINT", "low", "print('debug signal', signal)", r"print\(", "", 4, False)
    if len(scenarios) != 80:
        raise AssertionError("benchmark must contain exactly 80 risk scenarios")
    return scenarios


def _risk_source(scenario: dict) -> Tuple[str, str, str]:
    line = scenario["line"]
    before = "def process(value):\n    normalized = str(value)\n    return normalized\n"
    after = (
        "def process(value):\n"
        "    normalized = str(value)\n"
        "    %s\n"
        "    return value\n" % line
    )
    return before, after, line.strip()


def _clean_source(index: int) -> Tuple[str, str]:
    before = "def process(value):\n    return value\n"
    # 60 中性变体，结构上接近风险写法但刻意避开所有 QUANT-* 规则，用于检验假阳性。
    variants = [
        "    normalized = df['close'].shift(1)\n",
        "    x = ref(close, 1)\n",
        "    now = context.current_dt\n",
        "    prices = get_price('000001.XSHE', end_date=context.previous_date)\n",
        "    cerebro.broker.set_coc(False)\n",
        "    Xs = scaler.fit(X).transform(X)\n",
        "    z = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()\n",
        "    df = df.fillna(method='ffill')\n",
        "    q = get_fundamentals(query, date=context.current_dt)\n",
        "    stocks = get_index_stocks('000300.XSHG', date=context.current_dt)\n",
        "    api_key = os.environ['QUANT_API_KEY']\n",
        "    order_target_percent(context.portfolio, 0.5)\n",
        "    cerebro.broker.set_slippage(slip_perc=0.001)\n",
        "    cerebro.broker.set_commission(commission=0.0003)\n",
        "    cerebro.run()\n",
        "    pipeline = make_pipeline(StandardScaler(), model)\n",
        "    prices = get_price('000001.XSHE', fq='pre')\n",
        "    df = df.dropna()\n",
        "    logger.info('loaded %d bars', n)\n",
        "    ret = df['close'].pct_change().dropna()\n",
    ]
    after = "def process(value):\n%s    return value\n" % variants[index % len(variants)]
    return before, after


def _unified_diff(path: str, before: str, after: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(True),
        after.splitlines(True),
        fromfile="a/" + path,
        tofile="b/" + path,
        n=3,
    ))


# Real-factor multifile PR (alpha101 + pandas_ta, 19 injected QUANT triggers).
# Loaded live from the committed demo diff so labels never drift from the code.
_REAL_FACTOR_DIFF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "quant_sample_multifile.diff",
)

# (rule_id, severity, regex uniquely identifying its added line in the diff)
_REAL_FACTOR_RULE_SPECS = [
    ("QUANT-FF-SHIFT-NEG", "critical", r'\.shift\(-1\)'),
    ("QUANT-FF-REF-NEG", "critical", r'ref\(.*?-1\)'),
    ("QUANT-FF-DATETIME-NOW", "high", r'datetime\.now\(\)'),
    ("QUANT-FF-GETPRICE-NOW", "high", r'end_date=context\.current_dt'),
    ("QUANT-FF-CHEAT-CLOSE", "high", r'set_coc\(True\)'),
    ("QUANT-LK-FULL-NORM", "high", r'fit_transform\(X\)'),
    ("QUANT-LK-FULL-ZSCORE", "high", r'\.mean\(\)'),
    ("QUANT-LK-FORWARD-FILL", "medium", r'method="bfill"'),
    ("QUANT-LK-STATDATE", "medium", r'statDate='),
    ("QUANT-LK-INDEX-NOW", "medium", r'get_index_stocks\('),
    ("QUANT-SEC-HARDCODED-KEY", "high", r'api_key = "sk-live'),
    ("QUANT-SEC-NO-RISK", "medium", r'order_target_percent\(context\.portfolio, 1\.0\)'),
    ("QUANT-EX-ZERO-SLIP", "medium", r'slip_perc=0'),
    ("QUANT-EX-ZERO-COMM", "medium", r'commission=0'),
    ("QUANT-OF-OPTSTRATEGY", "medium", r'optstrategy'),
    ("QUANT-OF-GRIDSEARCH", "medium", r'GridSearchCV\('),
    ("QUANT-DQ-ADJUST-POST", "high", r"fq='post'"),
    ("QUANT-DQ-FILLNA0", "low", r'fillna\(0\)'),
    ("QUANT-REL-DEBUG-PRINT", "low", r"print\('debug signal'"),
]


def _build_real_factor_expected() -> List[dict]:
    """Locate the 19 injected quant triggers in the real-factor multifile diff.

    Each label's path/line is derived directly from the parsed diff so it can
    never drift from the actual added lines. Mirrors the rules-only review that
    already reproduces all 19 QUANT findings on this PR.
    """
    with open(_REAL_FACTOR_DIFF_PATH, "r", encoding="utf-8") as handle:
        diff = handle.read()
    parsed = parse_unified_diff(diff)
    added = [(ln.path, ln.line, ln.content) for ln in parsed.added_lines]
    expected: List[dict] = []
    for rule_id, severity, pattern in _REAL_FACTOR_RULE_SPECS:
        compiled = re.compile(pattern)
        hits = [(p, line, content) for (p, line, content) in added
                if compiled.search(content)]
        if len(hits) != 1:
            raise AssertionError(
                "real-factor rule %s matched %d lines (expected 1)" % (rule_id, len(hits))
            )
        path, line, _ = hits[0]
        expected.append({
            "path": path,
            "start_line": line,
            "end_line": line,
            "cwe": RULE_TO_CWE[rule_id],
            "rule_id": rule_id,
            "severity": severity,
            "should_comment": True,
        })
    return expected


def _real_factor_case() -> dict:
    with open(_REAL_FACTOR_DIFF_PATH, "r", encoding="utf-8") as handle:
        diff = handle.read()
    return {
        "schema_version": 1,
        "id": "pr-real-factor-001",
        # Reuse an existing holdout repository so the corpus' repository-level
        # split invariants (8 validation / 2 holdout repos) stay unchanged.
        "repository": "acme/service-09",
        "pull_request": 2007,
        "split": "holdout",
        "source": {
            "kind": "synthetic-controlled",
            "generator": "evoagent-e2e-v1",
            "public_url": None,
        },
        "diff": diff,
        "after_files": {},
        "expected_findings": _build_real_factor_expected(),
        "repair_validation": {},
    }


def generate_controlled_pr_cases() -> List[dict]:
    """Generate 100 reproducible PR-like diffs.

    These are deliberately labelled synthetic-controlled. They are useful for testing
    the harness, not for making claims about production performance on public PRs.
    """
    repositories = ["acme/service-%02d" % number for number in range(1, 11)]
    by_repo: Dict[str, List[dict]] = {repository: [] for repository in repositories}
    scenarios = _risk_scenarios()
    for index, scenario in enumerate(scenarios):
        repository = repositories[index % len(repositories)]
        path = "src/change_%02d.py" % (index + 1)
        before, after, needle = _risk_source(scenario)
        diff = _unified_diff(path, before, after)
        added = parse_unified_diff(diff).added_lines
        target = next(item for item in added if item.content.strip() == needle)
        by_repo[repository].append({
            "kind": "risk",
            "path": path,
            "diff": diff,
            "after": after,
            "scenario": scenario,
            "target_line": target.line,
        })
    for index in range(120):
        repository = repositories[index % len(repositories)]
        path = "src/clean_%02d.py" % (index + 1)
        before, after = _clean_source(index)
        by_repo[repository].append({
            "kind": "clean", "path": path,
            "diff": _unified_diff(path, before, after), "after": after,
        })

    cases = []
    sequence = 1
    for repository_index, repository in enumerate(repositories):
        split = "validation" if repository_index < 8 else "holdout"
        for local_index, item in enumerate(by_repo[repository], 1):
            expected = []
            repair_validation = {}
            if item["kind"] == "risk":
                scenario = item["scenario"]
                expected = [{
                    "path": item["path"],
                    "start_line": item["target_line"],
                    "end_line": item["target_line"],
                    "cwe": scenario["cwe"],
                    "rule_id": scenario["rule_id"],
                    "severity": scenario["severity"],
                    "should_comment": True,
                }]
                repair_validation = {
                    "auto_fixable": scenario["auto_fixable"],
                    "risk_pattern": scenario["risk_pattern"],
                    "required_after_patterns": scenario["required_after_patterns"],
                }
            cases.append({
                "schema_version": 1,
                "id": "pr-%04d" % sequence,
                "repository": repository,
                "pull_request": 1000 + local_index,
                "split": split,
                "source": {
                    "kind": "synthetic-controlled",
                    "generator": "evoagent-e2e-v1",
                    "public_url": None,
                },
                "diff": item["diff"],
                "after_files": {item["path"]: item["after"]},
                "expected_findings": expected,
                "repair_validation": repair_validation,
            })
            sequence += 1
    cases.append(_real_factor_case())
    if len(cases) != 201:
        raise AssertionError("benchmark must contain exactly 201 cases")
    return cases
