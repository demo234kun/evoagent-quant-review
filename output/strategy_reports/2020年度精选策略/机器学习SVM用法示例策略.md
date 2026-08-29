# EvoAgent 量化代码审查

**Repository:** `聚宽2020/机器学习SVM用法示例策略`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `196 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`机器学习SVM用法示例策略.py:53` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
stock_data = get_price(g.stock, frequency='1d',end_date=context.previous_date,count=252)
```

**证据引用：** `local-rule:6097b59e9bf877d3`, `diff-ast:893aa4a43a309d3e`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`机器学习SVM用法示例策略.py:88` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df_price = get_price(g.stock,end_date=date,count=count,fields=['open','close','low','high','volume','money','avg','pre_close'])
```

**证据引用：** `local-rule:465de9f315821895`, `diff-ast:53ebeb30df7a2947`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

