# EvoAgent 量化代码审查

**Repository:** `聚宽2020/AdaptiveMA自适应均线 过滤器 期货多品种模型 收益稳定增长`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `758 ms`

## 审查发现

### 1. 🟠 裸异常吞掉错误

`AdaptiveMA自适应均线 过滤器 期货多品种模型 收益稳定增长.py:325` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except:
```

**证据引用：** `local-rule:9118a98f84945f5b`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

