# EvoAgent 量化代码审查

**Repository:** `聚宽2025/SVR机器学习上证综指择时中小板财务选股策略`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 5 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `160 ms`

## 审查发现

### 1. 🟠 假设零手续费（set_commission 缺失/为 0）

`SVR机器学习上证综指择时中小板财务选股策略.py:15` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0001, close_commission=0.0001, close_today_commission=0, min_commission=5),
```

**证据引用：** `local-rule:058ca5ce22d12fff`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 2. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`SVR机器学习上证综指择时中小板财务选股策略.py:184` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stocks = stocks + get_index_stocks(index, dt_date)
```

**证据引用：** `local-rule:e7c8b33a1134366b`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 3. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`SVR机器学习上证综指择时中小板财务选股策略.py:199` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
# stocks = get_index_stocks(index, dt_last) # 获取指数成分股
```

**证据引用：** `local-rule:bfc35b64e62df4c9`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 4. 🟡 用 0 填补缺失值可能扭曲收益率

`SVR机器学习上证综指择时中小板财务选股策略.py:222` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
df = get_fundamentals(q, dt_last).fillna(0).set_index('code') # 获取基本面数据，填充缺失值并设置索引
```

**证据引用：** `local-rule:7e630ea453300795`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 5. 🟡 用 0 填补缺失值可能扭曲收益率

`SVR机器学习上证综指择时中小板财务选股策略.py:223` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
df = df.fillna(0)  # 填充缺失值
```

**证据引用：** `local-rule:6cc058c5b055258d`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

