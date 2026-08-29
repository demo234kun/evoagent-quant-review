# EvoAgent 量化代码审查

**Repository:** `聚宽2022/期货日内策略三价均线结合ATR指标`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 4 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `8`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `224 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`期货日内策略三价均线结合ATR指标.py:122` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
hist = get_price(stock, count = sma_length + duration, end_date=end_date, frequency='1m', fields=['high','low','close'])
```

**证据引用：** `local-rule:9936b2aa5475fed4`, `diff-ast:c98ec652bce35e65`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`期货日内策略三价均线结合ATR指标.py:130` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
data = get_price(stock, count = atr_length+duration, end_date=end_date, frequency='1m', fields=['high', 'low','close'])
```

**证据引用：** `local-rule:d603f82974280eab`, `diff-ast:4017a753312ba66e`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`期货日内策略三价均线结合ATR指标.py:161` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count = timePeriod+1, end_date=end_date, frequency='daily', fields=['close'])
```

**证据引用：** `local-rule:5a062d11f8446c6b`, `diff-ast:34807f978026d2d9`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`期货日内策略三价均线结合ATR指标.py:169` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock, count = period+1, end_date=end_date, frequency='daily', fields=['close'])
```

**证据引用：** `local-rule:a2e7d22ed67ca4fb`, `diff-ast:945e00ddeef123c4`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

