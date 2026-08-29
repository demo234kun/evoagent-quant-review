# EvoAgent 量化代码审查 — #1

**Repository:** `demo/quant-strategy`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 6 个可处理问题。整体风险：高。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `8`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `438 ms`

## 审查发现

### 1. 🚨 回测使用未来数据 (shift(-N))

`strategy.py:3` · **CRITICAL** · `QUANT-FF-SHIFT-NEG`

用 df.shift(-1) 等把下一根 bar 的数据对齐到当前行，会让信号偷看到未发生的价格，回测收益虚高。

**证据**

```text
future = df['close'].shift(-1)
```

**证据引用：** `local-rule:414e512b34ce8b9f`, `diff-ast:ab79ac069df7197d`

**修复建议：** 需要用到未来信息时改为 shift(正数) 或显式构造下一根标签；因子与信号必须只用当前及之前的数据。

**测试建议：** 构造一个已知结果的DataFrame，断言信号行不会引用其后的价格。

### 2. 🔴 疑似硬编码交易凭据

`strategy.py:4` · **HIGH** · `QUANT-SEC-HARDCODED-KEY`

交易账号、API Key、token 进入代码仓库后会通过历史记录与构建日志泄露。

**证据**

```text
api_key = "sk-live-abcdef123456"
```

**证据引用：** `local-rule:650e8c1fb25c89ec`, `diff-ast:ff087f92805951ba`

**修复建议：** 改为从密钥管理或环境变量读取，并立即轮换已提交的凭据。

**测试建议：** 测试缺失配置时安全失败，且日志不会输出凭据。

### 3. 🔴 在全样本上 fit_transform 造成数据泄露

`strategy.py:6` · **HIGH** · `QUANT-LK-FULL-NORM`

在训练/测试切分之前对整个数据集 fit_transform，会让测试集的统计信息泄漏进训练。

**证据**

```text
Xs = scaler.fit_transform(X)
```

**证据引用：** `local-rule:f28a3df7c49fd5e5`, `diff-ast:d03fc8bcf2e33d4a`

**修复建议：** 先切分再分别在训练集 fit，并用同一 scaler 仅 transform 测试集。

**测试建议：** 对比全样本缩放与时序切分缩放下的测试集指标，断言两者不同且后者更保守。

### 4. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`strategy.py:8` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
prices = get_price('000001.XSHE', end_date=context.current_dt)
```

**证据引用：** `local-rule:922fd5025fff2de9`, `diff-ast:b65de00da26dca80`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 5. 🟠 假设零滑点（set_slippage 缺失/为 0）

`strategy.py:5` · **MEDIUM** · `QUANT-EX-ZERO-SLIP`

滑点设为 0 会让回测成交价过于理想，实盘滑点会吞噬收益。

**证据**

```text
cerebro.broker.set_slippage(slip_perc=0)
```

**证据引用：** `local-rule:1d5b9e3aac6d0992`

**修复建议：** 设置合理的滑点模型（百分比或固定），并在参数中显式声明。

**测试建议：** 对比零滑点与真实滑点下的收益与回撤差异。

### 6. 🟡 新增调试输出

`strategy.py:7` · **LOW** · `QUANT-REL-DEBUG-PRINT`

直接输出可能污染日志或意外暴露运行数据。

**证据**

```text
print('debug signal', future)
```

**证据引用：** `local-rule:e5ed7c96c573b274`

**修复建议：** 删除调试输出，或改用带级别和脱敏策略的结构化日志。

**测试建议：** 验证正常请求不会产生包含敏感值的非预期输出。

