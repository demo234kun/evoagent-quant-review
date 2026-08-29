# EvoAgent 量化代码审查

**Repository:** `聚宽2022/一创PEG+EBIT+turnover_volatility`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `183 ms`

## 审查发现

### 1. 🟠 假设零手续费（set_commission 缺失/为 0）

`一创PEG+EBIT+turnover_volatility.py:18` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5),type='fund')
```

**证据引用：** `local-rule:ff34791e6c5419ae`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 2. 🟠 使用 statDate 拉取财报期数据，可能包含未披露数据

`一创PEG+EBIT+turnover_volatility.py:157` · **MEDIUM** · `QUANT-LK-STATDATE`

用 statDate 指定报告期会在报告实际发布前取到数据，形成前视。

**证据**

```text
df1 = get_fundamentals(q, statDate=qdate)
```

**证据引用：** `local-rule:7226754fbf32fef1`

**修复建议：** 用 point-in-time 的发布日字段，或在回测日之前取最近已披露财报。

**测试建议：** 断言取到的财报披露日不晚于回测当前日。

