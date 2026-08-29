import re

from evoagent.models import Finding, Severity
from evoagent.reviewer import Reviewer, category_for

SKILL_NAME = "code-quality"
SKILL_VERSION = "1.0.0"
SKILL_DESCRIPTION = (
    "Detects quantitative-trading code smells: blocking sleep, interactive debug "
    "plots and unsafe dynamic execution in added production code"
)


class CodeQualitySkill(Reviewer):
    name = "code-quality-agent"

    RULES = [
        (
            "QUANT-CQ-BLOCKING-SLEEP", Severity.LOW, re.compile(r"\btime\.sleep\s*\("),
            "策略中存在阻塞式 sleep",
            "在回测或实盘策略热路径里调用 time.sleep 会阻塞事件循环或下单线程，导致漏单与超时。",
            "改为基于事件/定时器的调度，或将等待逻辑移出策略核心。",
            "验证移除 sleep 后策略仍能按预期频率触发。",
        ),
        (
            "QUANT-CQ-DEBUG-PLOT", Severity.LOW, re.compile(r"\bplt\.show\s*\(\s*\)"),
            "非交互式回测中调用 plt.show()",
            "plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。",
            "改用 plt.savefig 或将绘图移到独立的可视化脚本。",
            "验证批处理模式下不会弹出窗口或阻塞进程。",
        ),
        (
            "QUANT-CQ-UNSAFE-EVAL", Severity.HIGH, re.compile(r"\b(?:eval|exec)\s*\("),
            "策略代码中出现 eval/exec",
            "在量化脚本里执行动态代码存在注入与不可复现风险，且难以做静态审查。",
            "改为显式函数与配置驱动的参数解析。",
            "验证移除 eval/exec 后策略逻辑等价且可静态审查。",
        ),
    ]

    def review(self, diff, parsed):
        findings = []
        for line in parsed.added_lines:
            if line.path.startswith("tests/"):
                continue
            for rule_id, severity, pattern, title, explanation, fix, test in self.RULES:
                if pattern.search(line.content):
                    findings.append(Finding(
                        rule_id=rule_id, severity=severity,
                        title=title, explanation=explanation,
                        path=line.path, line=line.line,
                        evidence=line.content.strip(),
                        fix=fix, test=test, confidence=0.8,
                        category=category_for(rule_id),
                    ))
        return findings


def create_skill():
    return CodeQualitySkill()
