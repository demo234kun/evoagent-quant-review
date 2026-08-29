# EvoAgent 量化代码审查

**Repository:** `聚宽2022/近几年一直有效的股票BOLL择时策略`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `157 ms`

## 审查发现

### 1. 🟠 set_order_cost 佣金/税费设为 0，回测收益虚高

`近几年一直有效的股票BOLL择时策略.py:23` · **MEDIUM** · `QUANT-EX-ZERO-ORDERCOST`

聚宽 set_order_cost 将佣金或税费设为 0 会高估策略真实收益，实盘存在成本。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.00012,\
```

**证据引用：** `local-rule:0ead293a467e03e3`

**修复建议：** 按真实券商费率设置 open_commission/close_commission/close_tax。

**测试建议：** 对比零成本与真实成本下的收益与回撤差异。

### 2. 🟠 假设零手续费（set_commission 缺失/为 0）

`近几年一直有效的股票BOLL择时策略.py:24` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
close_commission=0.0003, close_today_commission=0, min_commission=5),\
```

**证据引用：** `local-rule:a437ad0c6faebcaf`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 3. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`近几年一直有效的股票BOLL择时策略.py:240` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stock_pool = get_index_stocks("399101.XSHE") # 000300.XSHG 399101.XSHE
```

**证据引用：** `local-rule:17728577a9bc3ee7`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

