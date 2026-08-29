# EvoAgent 量化代码审查

**Repository:** `聚宽2024/低代码迁移成本的实盘方案jqtrade+one quant`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `181 ms`

## 审查发现

### 1. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`低代码迁移成本的实盘方案jqtrade+one quant.py:101` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
pdata = get_price(stock_list,count=1,frequency='1m',end_date=context.current_dt,fields=['close','high_limit','low_limit'],panel=False)
```

**证据引用：** `local-rule:6d6904dcd398a4d3`, `diff-ast:b0d64b014a1df105`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 2. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`低代码迁移成本的实盘方案jqtrade+one quant.py:51` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
codes = get_index_stocks(g.security_universe_index)
```

**证据引用：** `local-rule:4d192137f16f2f27`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

