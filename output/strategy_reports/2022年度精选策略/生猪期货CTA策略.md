# EvoAgent 量化代码审查

**Repository:** `聚宽2022/生猪期货CTA策略`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 6 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `10`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `171 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`生猪期货CTA策略.py:161` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count = timePeriod, end_date=end_date, frequency='daily', fields=['close'])
```

**证据引用：** `local-rule:571d171be8ace13f`, `diff-ast:dcfd3a113f677bc2`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`生猪期货CTA策略.py:271` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
hist = get_price(g.main_symbol, count = amount, end_date=strdate, frequency='daily', fields=['high', 'low'])
```

**证据引用：** `local-rule:d9a9f33051a38293`, `diff-ast:0f2448e01b045b07`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`生猪期货CTA策略.py:320` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count = sma_length + duration_day, end_date=end_date, frequency='daily', fields=['open', 'close'])
```

**证据引用：** `local-rule:054e096b2e44a606`, `diff-ast:cec90ad1a5330871`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`生猪期货CTA策略.py:328` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count = 30, end_date=end_date, frequency='daily', fields=['high','low','close'])
```

**证据引用：** `local-rule:4a0d99050867c735`, `diff-ast:105c028c5e10958d`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`生猪期货CTA策略.py:381` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count = period, end_date=date, frequency='daily', fields=['close'])
```

**证据引用：** `local-rule:02e66a3bed61ab72`, `diff-ast:5932db0747e9da52`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 6. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`生猪期货CTA策略.py:413` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count =300, end_date=date,frequency='daily', fields=['close'])
```

**证据引用：** `local-rule:01d09206ae662ee6`, `diff-ast:b5efc6841c7fc540`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

