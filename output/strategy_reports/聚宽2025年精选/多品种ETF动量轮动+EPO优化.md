# EvoAgent 量化代码审查

**Repository:** `聚宽2025/多品种ETF动量轮动+EPO优化`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `209 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`多品种ETF动量轮动+EPO优化.py:115` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
prices = get_price(stocks, count=1200, end_date=end_date, frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:995ced59d2cd0c5a`, `diff-ast:e5f3f66a425a4b52`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🟠 假设零手续费（set_commission 缺失/为 0）

`多品种ETF动量轮动+EPO优化.py:28` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0, open_commission=0.0002, close_commission=0.0002, close_today_commission=0, min_commission=5), type='fund')
```

**证据引用：** `local-rule:50c13d7d8e7336e4`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

