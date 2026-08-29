# EvoAgent 量化代码审查

**Repository:** `聚宽2021/【复现】RSRS择时改进`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `177 ms`

## 审查发现

### 1. 🚨 回测使用未来数据 (shift(-N))

`【复现】RSRS择时改进.py:394` · **CRITICAL** · `QUANT-FF-SHIFT-NEG`

用 df.shift(-1) 等把下一根 bar 的数据对齐到当前行，会让信号偷看到未发生的价格，回测收益虚高。

**证据**

```text
pct_chg = self.price_df['ret'].shift(-1).loc[self.start_date:]
```

**证据引用：** `local-rule:60838daea4e88c16`, `diff-ast:8d4d06211b4ad15b`

**修复建议：** 需要用到未来信息时改为 shift(正数) 或显式构造下一根标签；因子与信号必须只用当前及之前的数据。

**测试建议：** 构造一个已知结果的DataFrame，断言信号行不会引用其后的价格。

### 2. 🟡 用 0 填补缺失值可能扭曲收益率

`【复现】RSRS择时改进.py:406` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
strategy_cum = (1 + strategy_ret.fillna(0)).cumprod()
```

**证据引用：** `local-rule:35ede0838c608480`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

