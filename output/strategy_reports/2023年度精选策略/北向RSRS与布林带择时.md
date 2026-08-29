# EvoAgent 量化代码审查

**Repository:** `聚宽2023/北向RSRS与布林带择时`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 5 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `186 ms`

## 审查发现

### 1. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`北向RSRS与布林带择时.py:54` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
prices = get_price(g.security, context.current_dt - timedelta(g.M+1), context.previous_date, '1d', ['high', 'low'])
```

**证据引用：** `local-rule:3aca671d1175904d`, `diff-ast:93aa6098ba806dcb`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 2. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`北向RSRS与布林带择时.py:115` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
# stock_universe = get_up_stock(get_index_stocks(g.security))
```

**证据引用：** `local-rule:4ef72b67879b486a`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 3. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`北向RSRS与布林带择时.py:116` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
# stock_universe = get_index_stocks(g.security)
```

**证据引用：** `local-rule:8f5784b4a56c13b2`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 4. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`北向RSRS与布林带择时.py:118` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
# s_change_rank=get_up_stock(calc_change(context,get_index_stocks(g.security)))
```

**证据引用：** `local-rule:ec42111d92f371dc`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 5. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`北向RSRS与布林带择时.py:121` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
s_change_rank = calc_change(context,get_index_stocks(g.security))
```

**证据引用：** `local-rule:b820110046d3fc67`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

