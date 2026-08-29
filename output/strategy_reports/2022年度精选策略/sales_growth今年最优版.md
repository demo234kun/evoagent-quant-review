# EvoAgent 量化代码审查

**Repository:** `聚宽2022/sales_growth今年最优版`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `151 ms`

## 审查发现

### 1. 🔴 策略代码中出现 eval/exec

`sales_growth今年最优版.py:50` · **HIGH** · `QUANT-CQ-UNSAFE-EVAL`

在量化脚本里执行动态代码存在注入与不可复现风险，且难以做静态审查。

**证据**

```text
exec('g.idx3_%s=idx3'%i)
```

**证据引用：** `scanner:QUANT-CQ-UNSAFE-EVAL:sales_growth今年最优版.py:50`, `diff-ast:689ad0f3642a0f29`

**修复建议：** 改为显式函数与配置驱动的参数解析。

**测试建议：** 验证移除 eval/exec 后策略逻辑等价且可静态审查。

### 2. 🔴 策略代码中出现 eval/exec

`sales_growth今年最优版.py:51` · **HIGH** · `QUANT-CQ-UNSAFE-EVAL`

在量化脚本里执行动态代码存在注入与不可复现风险，且难以做静态审查。

**证据**

```text
exec('g.idx2_%s=idx2'%i)
```

**证据引用：** `scanner:QUANT-CQ-UNSAFE-EVAL:sales_growth今年最优版.py:51`, `diff-ast:70991dcb2d86e8d2`

**修复建议：** 改为显式函数与配置驱动的参数解析。

**测试建议：** 验证移除 eval/exec 后策略逻辑等价且可静态审查。

### 3. 🟠 假设零手续费（set_commission 缺失/为 0）

`sales_growth今年最优版.py:26` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, close_today_commission=0, min_commission=5),type='fund')
```

**证据引用：** `local-rule:c78d1954a81f47dd`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

