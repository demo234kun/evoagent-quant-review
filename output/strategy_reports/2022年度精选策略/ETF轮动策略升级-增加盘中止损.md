# EvoAgent 量化代码审查

**Repository:** `聚宽2022/ETF轮动策略升级-增加盘中止损`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `153 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`ETF轮动策略升级-增加盘中止损.py:221` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price_data = get_price(security, end_date=current_time, frequency='1d', fields=['close','high','low'], count=g.moment_period+1)
```

**证据引用：** `local-rule:7c7dff60c9973012`, `diff-ast:a1fb77abef271682`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🟠 set_order_cost 佣金/税费设为 0，回测收益虚高

`ETF轮动策略升级-增加盘中止损.py:32` · **MEDIUM** · `QUANT-EX-ZERO-ORDERCOST`

聚宽 set_order_cost 将佣金或税费设为 0 会高估策略真实收益，实盘存在成本。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0, \
```

**证据引用：** `local-rule:b77194d6a4a0f158`

**修复建议：** 按真实券商费率设置 open_commission/close_commission/close_tax。

**测试建议：** 对比零成本与真实成本下的收益与回撤差异。

### 3. 🟠 假设零手续费（set_commission 缺失/为 0）

`ETF轮动策略升级-增加盘中止损.py:34` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
close_today_commission=0, min_commission=0), type='stock')
```

**证据引用：** `local-rule:cbcca87484f42ab7`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

