# EvoAgent 量化代码审查

**Repository:** `聚宽2021/迪马克TD趋势反转指标`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 7 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `11`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `148 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:210` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
close = get_price(g.code,end_date=g.today,count=g.n1+5,fields='close')
```

**证据引用：** `local-rule:de5341ef878efb18`, `diff-ast:a06b6ff0192112f8`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:216` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
high = get_price(g.code,end_date=g.today,count=g.n1,fields='high').values.max()
```

**证据引用：** `local-rule:8e932e0e6eafdf23`, `diff-ast:382cb2c28150d962`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:220` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
low = get_price(g.code,end_date=g.today,count=g.n1,fields='low').values.min()
```

**证据引用：** `local-rule:1b1f8fc8085621e1`, `diff-ast:297e8ca06584fced`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:225` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
pre2low = get_price(g.code,end_date=g.today,count=3,fields='low').values[0]
```

**证据引用：** `local-rule:f2019d99da9da27c`, `diff-ast:8c6718a8b349bbbb`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:230` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
pre2high = get_price(g.code,end_date=g.today,count=3,fields='high').values[0]
```

**证据引用：** `local-rule:3cb136b4e465f8f6`, `diff-ast:bae7002902958dc5`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 6. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:251` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
low = get_price(g.code,end_date=g.today,count=g.n1,fields='low').values.min()
```

**证据引用：** `local-rule:67eed2cf2d667ce6`, `diff-ast:52401e4ebedf29ea`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 7. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`迪马克TD趋势反转指标.py:271` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
high = get_price(g.code,end_date=g.today,count=g.n1,fields='high').values.max()
```

**证据引用：** `local-rule:db910bc8df883999`, `diff-ast:aa2d34787fe70bde`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

