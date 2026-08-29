# EvoAgent 量化代码审查

**Repository:** `聚宽2025/（乱改一版）股票加“钱粮”ETF组合`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 6 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `8`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `201 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`（乱改一版）股票加“钱粮”ETF组合.py:297` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
prices = get_price(stocks, count=250, end_date=end_date, frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:ae8eae8b8d27099d`, `diff-ast:eaba167026ac4f8b`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`（乱改一版）股票加“钱粮”ETF组合.py:332` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(initial_list, start_date=yesterday, end_date=yesterday, fields=['close'], fq='pre', panel=False)
```

**证据引用：** `local-rule:70168ba39536f811`, `diff-ast:86483d210917fba2`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`（乱改一版）股票加“钱粮”ETF组合.py:351` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(g.hold_list, end_date=context.previous_date, frequency='daily', fields=['close','high_limit'], count=1, panel=False, fill_paused=False)
```

**证据引用：** `local-rule:96e9ee43054318fe`, `diff-ast:39cf8866df4f893b`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`（乱改一版）股票加“钱粮”ETF组合.py:392` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
current_data = get_price(stock, end_date=now_time, frequency='1m', fields=['close','high_limit'], skip_paused=False, fq='pre', count=1, panel=False, fill_paused=True)
```

**证据引用：** `local-rule:ad8690f5af1788d6`, `diff-ast:98c82beb12f56275`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🟠 假设零手续费（set_commission 缺失/为 0）

`（乱改一版）股票加“钱粮”ETF组合.py:29` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5),type='stock')
```

**证据引用：** `local-rule:0b8cf6ed9fa2fc9d`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 6. 🟡 用 0 填补缺失值可能扭曲收益率

`（乱改一版）股票加“钱粮”ETF组合.py:504` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
dividend = df.fillna(0)
```

**证据引用：** `local-rule:a9e2dc7942d77eee`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

