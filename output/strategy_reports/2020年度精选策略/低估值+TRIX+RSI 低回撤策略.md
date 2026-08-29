# EvoAgent 量化代码审查

**Repository:** `聚宽2020/低估值+TRIX+RSI 低回撤策略`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `178 ms`

## 审查发现

### 1. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`低估值+TRIX+RSI 低回撤策略.py:66` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
g.codelist = get_index_stocks('000300.XSHG')
```

**证据引用：** `local-rule:ed82f152b0848fac`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 2. 🟠 裸异常吞掉错误

`低估值+TRIX+RSI 低回撤策略.py:253` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except:
```

**证据引用：** `local-rule:1b9638f260864137`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

