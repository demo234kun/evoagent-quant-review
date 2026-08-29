# EvoAgent 量化代码审查

**Repository:** `聚宽2024/FScore9因子模型改进——RFScore7因子`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 5 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `8`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `240 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`FScore9因子模型改进——RFScore7因子.py:109` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
paused = get_price(self.securities,end_date=self.watch_date,count=paused_N,fields='paused',panel=False)
```

**证据引用：** `local-rule:d2aa3d861d3c45c5`, `diff-ast:05aca7d2e45609a5`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`FScore9因子模型改进——RFScore7因子.py:128` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
zdt = get_price(self.securities,end_date=self.watch_date,fields=['close','high_limit','low_limit','paused'],count=1,panel=False,fq='post')
```

**证据引用：** `local-rule:42aa4b0cd479e994`, `diff-ast:5a2e75ab104f670a`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 使用后复权 (post) 做历史决策，含未来除权信息

`FScore9因子模型改进——RFScore7因子.py:128` · **HIGH** · `QUANT-DQ-ADJUST-POST`

后复权价格把未来分红/除权折算进历史价，用其回测等于前视。

**证据**

```text
zdt = get_price(self.securities,end_date=self.watch_date,fields=['close','high_limit','low_limit','paused'],count=1,panel=False,fq='post')
```

**证据引用：** `local-rule:a0fe02aa91a563da`, `diff-ast:56011b3c692e0fbf`

**修复建议：** 历史决策使用不复权或前复权；后复权仅用于展示。

**测试建议：** 断言因子计算所用价格口径不含未来除权信息。

### 4. 🔴 使用后复权 (post) 做历史决策，含未来除权信息

`FScore9因子模型改进——RFScore7因子.py:425` · **HIGH** · `QUANT-DQ-ADJUST-POST`

后复权价格把未来分红/除权折算进历史价，用其回测等于前视。

**证据**

```text
fq = 'post',
```

**证据引用：** `local-rule:9f6a5bad425cef02`, `diff-ast:50d4e576916211fa`

**修复建议：** 历史决策使用不复权或前复权；后复权仅用于展示。

**测试建议：** 断言因子计算所用价格口径不含未来除权信息。

### 5. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`FScore9因子模型改进——RFScore7因子.py:94` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
self.securities:List = get_index_stocks(self.symbol,self.watch_date)
```

**证据引用：** `local-rule:3c338304da5eacbb`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

