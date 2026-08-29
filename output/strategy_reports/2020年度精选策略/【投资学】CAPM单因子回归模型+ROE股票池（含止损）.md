# EvoAgent 量化代码审查

**Repository:** `聚宽2020/【投资学】CAPM单因子回归模型+ROE股票池（含止损）`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `171 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`【投资学】CAPM单因子回归模型+ROE股票池（含止损）.py:81` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
suspened_info_df = get_price(list(stock_list), start_date=context.current_dt, end_date=context.current_dt, frequency='daily', fields='paused')['paused'].T
```

**证据引用：** `local-rule:22f1c1c70e9f6b99`, `diff-ast:225dc825c7261927`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

