# EvoAgent 量化代码审查

**Repository:** `聚宽2023/韶华研究之五-ETF轮动，躺赚，夏普2`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `172 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`韶华研究之五-ETF轮动，躺赚，夏普2.py:294` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df_close = get_price(g.available_indexs,end_date=lastd_date,count =g.check_unit,frequency='daily')  #间接判断对应指数的日行情
```

**证据引用：** `local-rule:090c86b62ba7db2c`, `diff-ast:216a18d69d746e35`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

