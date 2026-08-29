# EvoAgent 量化代码审查

**Repository:** `聚宽2021/识别趋势震荡之神器 MESA最大熵谱分析（一）：滤波器建立`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `7`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `179 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`识别趋势震荡之神器 MESA最大熵谱分析（一）：滤波器建立.py:70` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price('000300.XSHG', start_date = start_date, end_date = end_date, frequency = 'minute')
```

**证据引用：** `local-rule:537bea7f9234c512`, `diff-ast:af59eeb0bbad2d93`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 策略逻辑使用了真实当前时间

`识别趋势震荡之神器 MESA最大熵谱分析（一）：滤波器建立.py:513` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
now = datetime.datetime.now()
```

**证据引用：** `local-rule:843080532126835f`, `diff-ast:5208145884ec5571`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`识别趋势震荡之神器 MESA最大熵谱分析（一）：滤波器建立.py:523` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price('000300.XSHG', start_date = start_date, end_date = end_date, frequency = 'minute')
```

**证据引用：** `local-rule:630de292ab69cc60`, `diff-ast:ba7b810110ec0e6f`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

