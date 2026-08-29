# EvoAgent 量化代码审查

**Repository:** `聚宽2025/BiLSTM for ETF`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 4 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `194 ms`

## 审查发现

### 1. 🔴 策略代码中出现 eval/exec

`BiLSTM for ETF.py:67` · **HIGH** · `QUANT-CQ-UNSAFE-EVAL`

在量化脚本里执行动态代码存在注入与不可复现风险，且难以做静态审查。

**证据**

```text
model_t1.eval()
```

**证据引用：** `scanner:QUANT-CQ-UNSAFE-EVAL:BiLSTM for ETF.py:67`, `diff-ast:587577e1f94708e3`

**修复建议：** 改为显式函数与配置驱动的参数解析。

**测试建议：** 验证移除 eval/exec 后策略逻辑等价且可静态审查。

### 2. 🔴 在全样本上 fit_transform 造成数据泄露

`BiLSTM for ETF.py:85` · **HIGH** · `QUANT-LK-FULL-NORM`

在训练/测试切分之前对整个数据集 fit_transform，会让测试集的统计信息泄漏进训练。

**证据**

```text
normalized_data = scaler.fit_transform(df)
```

**证据引用：** `local-rule:c18bc8203a2dd2f3`, `diff-ast:d76aaee1fc3e463d`

**修复建议：** 先切分再分别在训练集 fit，并用同一 scaler 仅 transform 测试集。

**测试建议：** 对比全样本缩放与时序切分缩放下的测试集指标，断言两者不同且后者更保守。

### 3. 🟠 set_order_cost 佣金/税费设为 0，回测收益虚高

`BiLSTM for ETF.py:26` · **MEDIUM** · `QUANT-EX-ZERO-ORDERCOST`

聚宽 set_order_cost 将佣金或税费设为 0 会高估策略真实收益，实盘存在成本。

**证据**

```text
set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
```

**证据引用：** `local-rule:3bc0e16af1e80d20`

**修复建议：** 按真实券商费率设置 open_commission/close_commission/close_tax。

**测试建议：** 对比零成本与真实成本下的收益与回撤差异。

### 4. 🟠 假设零手续费（set_commission 缺失/为 0）

`BiLSTM for ETF.py:27` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
close_today_commission=0, min_commission=5), type='stock')
```

**证据引用：** `local-rule:52817c155decc203`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

