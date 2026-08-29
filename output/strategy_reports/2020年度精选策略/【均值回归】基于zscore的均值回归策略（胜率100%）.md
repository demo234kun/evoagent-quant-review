# EvoAgent 量化代码审查

**Repository:** `聚宽2020/【均值回归】基于zscore的均值回归策略（胜率100%）`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `178 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`【均值回归】基于zscore的均值回归策略（胜率100%）.py:44` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price_df = get_price(g.stock_list, end_date=yesterday, fields='close', count=count).close
```

**证据引用：** `local-rule:52bf0220a074b61d`, `diff-ast:d42e683e1b04e7c7`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`【均值回归】基于zscore的均值回归策略（胜率100%）.py:41` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
#stock_list = get_index_stocks('000016.XSHG')[:10]
```

**证据引用：** `local-rule:54f216b80d7dd2f6`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

