# EvoAgent 量化代码审查

**Repository:** `聚宽2021/RSRS择时+货币基金--6年8倍行业周期股策略`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `192 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`RSRS择时+货币基金--6年8倍行业周期股策略.py:284` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
prices = get_price(g.security, '2005-01-05', previous_date, '1d', ['high', 'low'])
```

**证据引用：** `local-rule:8e1201683328ef83`, `diff-ast:b557e17563251c87`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🟠 使用 statDate 拉取财报期数据，可能包含未披露数据

`RSRS择时+货币基金--6年8倍行业周期股策略.py:335` · **MEDIUM** · `QUANT-LK-STATDATE`

用 statDate 指定报告期会在报告实际发布前取到数据，形成前视。

**证据**

```text
oneData=get_fundamentals(lqt,statDate=statq)
```

**证据引用：** `local-rule:3307665ad82f5ae0`

**修复建议：** 用 point-in-time 的发布日字段，或在回测日之前取最近已披露财报。

**测试建议：** 断言取到的财报披露日不晚于回测当前日。

### 3. 🟡 用 0 填补缺失值可能扭曲收益率

`RSRS择时+货币基金--6年8倍行业周期股策略.py:337` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
one_period=one_period.fillna(0)
```

**证据引用：** `local-rule:b85e0da85eeabf48`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

