# EvoAgent 量化代码审查

**Repository:** `聚宽2022/计算每日全A市场个股创新高比例(改)`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `182 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`计算每日全A市场个股创新高比例(改).py:24` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
get_ipython().run_cell_magic('time', '', "by_date = get_trade_days(end_date=end_date, count=window+check_days)[0]   \n# 确保end_date之前的window+check_days个交易日已经上市，从而确保get_price取数的正确性\nstock_list = get_all_securities(date=by_date).index.tolist()
```

**证据引用：** `local-rule:fa75c232204e3c5e`, `diff-ast:55ba1afc6875f1a1`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

