# EvoAgent 量化代码审查

**Repository:** `聚宽2025/手把手教你构建ETF策略候选池`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 5 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `9`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `196 ms`

## 审查发现

### 1. 🔴 策略逻辑使用了真实当前时间

`手把手教你构建ETF策略候选池.py:27` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
today = str(datetime.datetime.today().date())
```

**证据引用：** `local-rule:c6ff5d7719bf8bd8`, `diff-ast:ec8266741d548b00`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`手把手教你构建ETF策略候选池.py:47` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price = get_price(code, end_date=today, count=1000).dropna()
```

**证据引用：** `local-rule:c69f69ba3bae956b`, `diff-ast:2741892b76701d93`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 策略逻辑使用了真实当前时间

`手把手教你构建ETF策略候选池.py:68` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
today = datetime.datetime.today().date()
```

**证据引用：** `local-rule:01bd13803bc98e0e`, `diff-ast:5fdd32a6605d344b`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`手把手教你构建ETF策略候选池.py:73` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price = get_price(code, fields='close',end_date=end_date, count=240)
```

**证据引用：** `local-rule:5552a59f935b71e0`, `diff-ast:887b334fe45efa01`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`手把手教你构建ETF策略候选池.py:194` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
tmp = get_price(code, start_date='2017-01-01', end_date=today, fields=['close', 'low']).dropna()
```

**证据引用：** `local-rule:e098f447f9634ec2`, `diff-ast:3a69d5241ea383b9`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

