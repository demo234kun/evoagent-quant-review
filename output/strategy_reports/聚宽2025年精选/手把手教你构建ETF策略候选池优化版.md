# EvoAgent 量化代码审查

**Repository:** `聚宽2025/手把手教你构建ETF策略候选池优化版`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 4 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `9`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `187 ms`

## 审查发现

### 1. 🔴 策略逻辑使用了真实当前时间

`手把手教你构建ETF策略候选池优化版.py:25` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
today = str(datetime.datetime.today().date())
```

**证据引用：** `local-rule:5ac6ed5eee3747d0`, `diff-ast:4dd465381fa093b7`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 2. 🔴 策略逻辑使用了真实当前时间

`手把手教你构建ETF策略候选池优化版.py:31` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
df = df[df['end_date'] >= datetime.datetime.today().date()]
```

**证据引用：** `local-rule:af80e26c40ae6384`, `diff-ast:07d3c30997663955`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`手把手教你构建ETF策略候选池优化版.py:36` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price = get_price(code, end_date=today, count=300).dropna()
```

**证据引用：** `local-rule:e0bfbaeca06c23da`, `diff-ast:3130b45609e0f38e`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 策略逻辑使用了真实当前时间

`手把手教你构建ETF策略候选池优化版.py:50` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
price = get_price(code, fields='close',end_date=datetime.datetime.today().date(), count=450)
```

**证据引用：** `local-rule:2297a0680416e91d`, `diff-ast:2cd59e4446b66e8a`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

