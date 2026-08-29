# EvoAgent 量化代码审查

**Repository:** `聚宽2025/回馈社区顺便搞积分《一个完整的机器学习pipeline》`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `208 ms`

## 审查发现

### 1. 🟠 set_order_cost 佣金/税费设为 0，回测收益虚高

`回馈社区顺便搞积分《一个完整的机器学习pipeline》.py:24` · **MEDIUM** · `QUANT-EX-ZERO-ORDERCOST`

聚宽 set_order_cost 将佣金或税费设为 0 会高估策略真实收益，实盘存在成本。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
```

**证据引用：** `local-rule:6e41474409ee4a23`

**修复建议：** 按真实券商费率设置 open_commission/close_commission/close_tax。

**测试建议：** 对比零成本与真实成本下的收益与回撤差异。

### 2. 🟠 假设零手续费（set_commission 缺失/为 0）

`回馈社区顺便搞积分《一个完整的机器学习pipeline》.py:25` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
close_today_commission=0, min_commission=5), type='stock')
```

**证据引用：** `local-rule:ba9393419e59a0e1`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

