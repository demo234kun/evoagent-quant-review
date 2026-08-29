# EvoAgent 量化代码审查

**Repository:** `聚宽2020/因子分析——利用JoinQuant因子分析模块选取因子并封装为策略`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `153 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`因子分析——利用JoinQuant因子分析模块选取因子并封装为策略.py:21` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(stock_list,end_date=dt,count=1,fields=['money'])
```

**证据引用：** `local-rule:5f1ccd53bdbc0950`, `diff-ast:31ca2efdb052151b`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🟠 假设零手续费（set_commission 缺失/为 0）

`因子分析——利用JoinQuant因子分析模块选取因子并封装为策略.py:15` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0, open_commission=0, close_commission=0, close_today_commission=0, min_commission=0), type='stock')
```

**证据引用：** `local-rule:241bc7c8f9a35c83`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 3. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`因子分析——利用JoinQuant因子分析模块选取因子并封装为策略.py:19` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stock_list=get_index_stocks(g.index)
```

**证据引用：** `local-rule:5770f20286b88e04`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

