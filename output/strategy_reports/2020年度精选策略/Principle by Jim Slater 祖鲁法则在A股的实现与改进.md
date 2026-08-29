# EvoAgent 量化代码审查

**Repository:** `聚宽2020/Principle by Jim Slater 祖鲁法则在A股的实现与改进`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 11 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `10`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `183 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:287` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price_p=get_price(list2,end_date=previous_date,count=1,fields='close')['close']
```

**证据引用：** `local-rule:f7a9dc7b4cfeb885`, `diff-ast:27c865b4106ae7e5`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:288` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
market_p=get_price(benchmark,end_date=previous_date,count=1,fields='close')['close']
```

**证据引用：** `local-rule:8bbdc598577dc18c`, `diff-ast:3240b4171196bac0`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:290` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price_m=get_price(list2,end_date=month_date,count=1,fields='close')['close']
```

**证据引用：** `local-rule:069574cbf6dd7be0`, `diff-ast:2460fc32c9b824ca`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:291` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
market_m=get_price(benchmark,end_date=month_date,count=1,fields='close')['close']
```

**证据引用：** `local-rule:b78a420a7f259688`, `diff-ast:3a0420e382bfa72a`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:293` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price_y=get_price(list2,end_date=year_date,count=1,fields='close')['close']
```

**证据引用：** `local-rule:c9de5d3b586610d6`, `diff-ast:1ba8d57ca4f6cae3`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 6. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:294` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
market_y=get_price(benchmark,end_date=year_date,count=1,fields='close')['close']
```

**证据引用：** `local-rule:170e8b309a99111c`, `diff-ast:b368e25d1379e109`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 7. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:38` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
list0=get_index_stocks('000001.XSHG')
```

**证据引用：** `local-rule:649458ec99e49741`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 8. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:89` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
list0=get_index_stocks(index)
```

**证据引用：** `local-rule:35384f4a3e357bf6`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 9. 🟠 假设零手续费（set_commission 缺失/为 0）

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:378` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5), type='stock')
```

**证据引用：** `local-rule:251473a87b216d2c`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 10. 🟠 假设零手续费（set_commission 缺失/为 0）

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:380` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0, open_commission=0, close_commission=0, close_today_commission=0, min_commission=0), type='stock')
```

**证据引用：** `local-rule:37e8ef764b6d1226`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 11. 🟠 假设零手续费（set_commission 缺失/为 0）

`Principle by Jim Slater 祖鲁法则在A股的实现与改进.py:382` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5), type='stock')
```

**证据引用：** `local-rule:5679b6969cbcaef8`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

