# EvoAgent 量化代码审查

**Repository:** `聚宽2024/【社区研究】连板龙头策略-wywy：复现与研究`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `171 ms`

## 审查发现

### 1. 🚨 回测使用未来数据 (shift(-N))

`【社区研究】连板龙头策略-wywy：复现与研究.py:88` · **CRITICAL** · `QUANT-FF-SHIFT-NEG`

用 df.shift(-1) 等把下一根 bar 的数据对齐到当前行，会让信号偷看到未发生的价格，回测收益虚高。

**证据**

```text
merge_df['open_valid1'] = merge_df.groupby('code')['open'].shift(-1)
```

**证据引用：** `local-rule:42ac97eaa3c09b9f`, `diff-ast:ddd1312a1574fff3`

**修复建议：** 需要用到未来信息时改为 shift(正数) 或显式构造下一根标签；因子与信号必须只用当前及之前的数据。

**测试建议：** 构造一个已知结果的DataFrame，断言信号行不会引用其后的价格。

