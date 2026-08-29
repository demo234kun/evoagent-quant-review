from typing import Any, Dict


def to_markdown(report: Dict[str, Any]) -> str:
    title = "# EvoAgent 量化代码审查"
    if report.get("pull_request") is not None:
        title += " — #%s" % report["pull_request"]
    lines = [
        title,
        "",
        "**Repository:** `%s`  " % report.get("repository", ""),
        "**Risk:** `%s`  " % report.get("risk", "unknown"),
        "**Reviewer:** `%s`" % report.get("reviewer", "unknown"),
        "",
        report.get("summary", ""),
        "",
    ]
    run_mode = report.get("run_mode") or {}
    execution = report.get("execution") or {}
    if run_mode:
        lines.extend([
            "## 执行概况",
            "",
            "- 模式：请求 `%s`，实际 `%s`" % (
                run_mode.get("requested", "unknown"), run_mode.get("effective", "unknown")
            ),
            "- 模型调用: `%s`；工具调用: `%s`" % (
                execution.get("llm_calls", 0), execution.get("tool_calls", 0)
            ),
            "- Token：输入 `%s`、输出 `%s`、合计 `%s`" % (
                execution.get("input_tokens", 0), execution.get("output_tokens", 0),
                execution.get("total_tokens", 0),
            ),
            "- Token 成本: `$%.8f`；延迟: `%s ms`" % (
                float(execution.get("cost_usd", 0) or 0), execution.get("duration_ms", 0)
            ),
            "",
        ])
        if run_mode.get("fallback_reason"):
            lines.extend(["> %s" % run_mode["fallback_reason"], ""])
    collaboration = report.get("collaboration") or {}
    if collaboration and run_mode.get("effective") == "agentic" and execution.get("llm_calls", 0):
        lines.extend([
            "## LLM 智能体协作",
            "",
            "- 协议: `%s`" % collaboration.get("protocol", "unknown"),
            "- 实际角色: `%s`" % ", ".join(collaboration.get("roles") or []),
            "- 候选问题: `%s`；评审决策: `%s`" % (
                collaboration.get("candidate_findings", 0),
                len(collaboration.get("critic_decisions") or []),
            ),
            "",
        ])
    findings = report.get("findings", [])
    if not findings:
        lines.append("✅ 在新增代码行中未检测到可处理的问题。")
        return "\n".join(lines) + "\n"
    lines.extend(["## 审查发现", ""])
    icons = {"critical": "🚨", "high": "🔴", "medium": "🟠", "low": "🟡"}
    for index, item in enumerate(findings, 1):
        severity = item.get("severity", "medium")
        lines.extend(
            [
                "### %d. %s %s" % (index, icons.get(severity, "•"), item.get("title", "Finding")),
                "",
                "`%s:%s` · **%s** · `%s`" % (
                    item.get("path", ""), item.get("line", 0), severity.upper(), item.get("rule_id", "")),
                "",
                item.get("explanation", ""),
                "",
                "**证据**",
                "",
                "```text",
                item.get("evidence", ""),
                "```",
                "",
                "**证据引用：** %s" % (
                    ", ".join(
                        "`%s`" % ref.get("evidence_id", "")
                        for ref in item.get("evidence_refs", []) if ref.get("evidence_id")
                    ) or "none"
                ),
                "",
                "**修复建议：** %s" % item.get("fix", ""),
                "",
                "**测试建议：** %s" % item.get("test", ""),
                "",
            ]
        )
    backtest = report.get("backtest") or {}
    if backtest:
        metrics = backtest.get("metrics") or {}
        lines.extend(["", "## 回测结果", ""])
        if metrics:
            lines.extend([
                "- 初始资金: `%s`" % metrics.get("initial_capital", ""),
                "- 最终权益: `%s`" % metrics.get("final_equity", ""),
                "- 总收益: `%s%%`" % metrics.get("total_return", ""),
                "- 年化收益: `%s%%`" % metrics.get("annualized_return", ""),
                "- Sharpe: `%s`" % metrics.get("sharpe", ""),
                "- 最大回撤: `%s%%`" % metrics.get("max_drawdown", ""),
                "- 胜率: `%s%%`" % metrics.get("win_rate", ""),
                "- 交易次数: `%s`" % metrics.get("num_trades", ""),
            ])
        else:
            lines.append("_（未产生回测指标）_")
        errs = backtest.get("errors") or []
        if errs:
            lines.extend(["", "**执行错误：**", ""])
            for err in errs[:5]:
                lines.append("- %s" % err)
        lines.append("")
    return "\n".join(lines) + "\n"
