# EvoAgent 量化代码审查

**Repository:** `聚宽2021/根据北上资金买A股策略Python3版（北向、港资、外资）`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `175 ms`

## 审查发现

### 1. 🟠 set_order_cost 佣金/税费设为 0，回测收益虚高

`根据北上资金买A股策略Python3版（北向、港资、外资）.py:25` · **MEDIUM** · `QUANT-EX-ZERO-ORDERCOST`

聚宽 set_order_cost 将佣金或税费设为 0 会高估策略真实收益，实盘存在成本。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
```

**证据引用：** `local-rule:9daad2898ba468d1`

**修复建议：** 按真实券商费率设置 open_commission/close_commission/close_tax。

**测试建议：** 对比零成本与真实成本下的收益与回撤差异。

