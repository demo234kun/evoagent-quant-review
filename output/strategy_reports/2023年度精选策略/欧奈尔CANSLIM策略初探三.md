# EvoAgent 量化代码审查

**Repository:** `聚宽2023/欧奈尔CANSLIM策略初探三`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 4 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `8`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `167 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`欧奈尔CANSLIM策略初探三.py:95` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
HS300 = get_price('000300.XSHG', count=250, end_date=day, panel=False)
```

**证据引用：** `local-rule:125b5f0d23ee453f`, `diff-ast:290b6dc093b67ec1`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`欧奈尔CANSLIM策略初探三.py:156` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
p_df = get_price(stock_list, count=1, end_date=date, fields=['paused'], panel=False)
```

**证据引用：** `local-rule:3886037f03d77ac1`, `diff-ast:367591feb6a77c73`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`欧奈尔CANSLIM策略初探三.py:200` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
p_df = get_price(stocks, count=250, end_date=date, panel=False)
```

**证据引用：** `local-rule:e730d882fc6e301c`, `diff-ast:404d1f1585d1d665`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`欧奈尔CANSLIM策略初探三.py:205` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
p_df = get_price(stocks, count=250, end_date=date, panel=False)
```

**证据引用：** `local-rule:b9a9ad4b69c126de`, `diff-ast:4a8354b692a610ab`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

