# EvoAgent 量化代码审查

**Repository:** `聚宽2020/低PB价值投资策略分享`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 4 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `166 ms`

## 审查发现

### 1. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`低PB价值投资策略分享.py:113` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
df_price = get_price(security, start_date=context.portfolio.positions[security].init_time, end_date=context.current_dt, frequency='1m', fields=['high','low'])
```

**证据引用：** `local-rule:444fc365f71df62a`, `diff-ast:2f9996816b989ed2`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 2. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`低PB价值投资策略分享.py:301` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
df_price = get_price(security, start_date=context.portfolio.positions[security].init_time, end_date=context.current_dt, frequency='1m', fields=['high','low'])
```

**证据引用：** `local-rule:1cc3e0e2fc11b5c8`, `diff-ast:8c1f833a6cd6786e`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 3. 🟠 set_order_cost 佣金/税费设为 0，回测收益虚高

`低PB价值投资策略分享.py:54` · **MEDIUM** · `QUANT-EX-ZERO-ORDERCOST`

聚宽 set_order_cost 将佣金或税费设为 0 会高估策略真实收益，实盘存在成本。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
```

**证据引用：** `local-rule:2115907512410557`

**修复建议：** 按真实券商费率设置 open_commission/close_commission/close_tax。

**测试建议：** 对比零成本与真实成本下的收益与回撤差异。

### 4. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`低PB价值投资策略分享.py:203` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
temp_index += get_index_stocks(s)
```

**证据引用：** `local-rule:34fc78e3254851ac`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

