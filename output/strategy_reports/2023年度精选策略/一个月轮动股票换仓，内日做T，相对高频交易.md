# EvoAgent 量化代码审查

**Repository:** `聚宽2023/一个月轮动股票换仓，内日做T，相对高频交易`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 6 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `9`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `196 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`一个月轮动股票换仓，内日做T，相对高频交易.py:127` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
paused = get_price(self.securities,end_date=self.watch_date,count=paused_N,fields='paused',panel=False)
```

**证据引用：** `local-rule:e06d8d79ca369170`, `diff-ast:2ae872c867196ed3`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`一个月轮动股票换仓，内日做T，相对高频交易.py:383` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df_panel = get_price(stock, count = 1,end_date=pre_date, frequency='daily', fields=['close','high','low'])
```

**证据引用：** `local-rule:f1619cb805f2517e`, `diff-ast:c7e4e0b11532651c`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`一个月轮动股票换仓，内日做T，相对高频交易.py:390` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
df_panel_allday = get_price(stock, start_date=lastToday, end_date=context.current_dt, frequency='minute', fields=['high','low','close','high_limit','money'])
```

**证据引用：** `local-rule:33e74c3232cc8502`, `diff-ast:0e7d2dae734010a8`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`一个月轮动股票换仓，内日做T，相对高频交易.py:411` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df_panel = get_price(stock, count = 1,end_date=pre_date, frequency='daily', fields=['close','high','low'])
```

**证据引用：** `local-rule:6554d98f3251b8cb`, `diff-ast:c4b83850bbe24d5c`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`一个月轮动股票换仓，内日做T，相对高频交易.py:418` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
df_panel_allday = get_price(stock, start_date=lastToday, end_date=context.current_dt, frequency='minute', fields=['high','low','close','high_limit','money'])
```

**证据引用：** `local-rule:29361b1ee097e1b4`, `diff-ast:ec738b0ba2b4661a`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 6. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`一个月轮动股票换仓，内日做T，相对高频交易.py:112` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
self.securities:List = get_index_stocks(self.symbol,self.watch_date)
```

**证据引用：** `local-rule:4fba7f036c7e44f8`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

