# EvoAgent 量化代码审查

**Repository:** `聚宽2025/分享一种K线小碎步后突破的分钟级打法`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 10 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `16`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `196 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:252` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df =  get_price(stock_list, end_date=date, frequency='daily', fields=['close'], count=1, panel=False, fill_paused=False, skip_paused=True).set_index('code') if len(stock_list) != 0 else pd.DataFrame()
```

**证据引用：** `local-rule:2a8a80e01e37db6b`, `diff-ast:eff5eb231d2da4f5`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:360` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(initial_list, end_date=date, frequency='daily', fields=['close','high_limit'], count=watch_days, panel=False, fill_paused=False, skip_paused=False)
```

**证据引用：** `local-rule:8f52799b24019fb1`, `diff-ast:0f0d884ff53a1931`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:368` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(initial_list, end_date=date, frequency='daily', fields=['close','high_limit'], count=watch_days, panel=False, fill_paused=False, skip_paused=False)
```

**证据引用：** `local-rule:8b0831f974d3ee3e`, `diff-ast:51818cb2fa8c76b1`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:405` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(initial_list, end_date=date, frequency='daily', fields=['paused'], count=1, panel=False, fill_paused=True)
```

**证据引用：** `local-rule:3b84741fef3610f6`, `diff-ast:1aeeea6886afe2fa`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:447` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock_list, end_date=date, fields=['high', 'low', 'close'], count=watch_days, fill_paused=False, skip_paused=False, panel=False).dropna()
```

**证据引用：** `local-rule:fb0b0b9693f3c513`, `diff-ast:9fa90a7aa1ebd195`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 6. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:461` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock_list, end_date=date, fields=['high', 'low', 'close'], frequency='30d', count=watch_months, fill_paused=False, skip_paused=False, panel=False).dropna()
```

**证据引用：** `local-rule:e7bbcab80027850f`, `diff-ast:2dfc22857e30f184`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 7. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:475` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock_list, end_date=date, fields=['high', 'low', 'close'], frequency='5d', count=watch_weeks, fill_paused=False, skip_paused=False, panel=False).dropna()
```

**证据引用：** `local-rule:7576925094e319e8`, `diff-ast:e2221c041a1073a6`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 8. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:486` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(initial_list, end_date=date, frequency='daily', fields=['close','pre_close'], count=watch_days, panel=False, fill_paused=False, skip_paused=False)
```

**证据引用：** `local-rule:ee4d86b51ecb4939`, `diff-ast:d2e01aa4a3550def`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 9. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:496` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock_list, end_date=date, fields=['high', 'low', 'close'], count=watch_days, fill_paused=False, skip_paused=False, panel=False).dropna()
```

**证据引用：** `local-rule:f637e7111c6ed979`, `diff-ast:30852118204258d9`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 10. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`分享一种K线小碎步后突破的分钟级打法.py:511` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock_list, end_date=date, fields=['high', 'low', 'close'], count=watch_days, fill_paused=False, skip_paused=False, panel=False).dropna()
```

**证据引用：** `local-rule:201820555a0bed25`, `diff-ast:28195a049d4a3546`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

