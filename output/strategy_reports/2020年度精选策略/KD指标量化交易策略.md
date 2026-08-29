# EvoAgent 量化代码审查

**Repository:** `聚宽2020/KD指标量化交易策略`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `169 ms`

## 审查发现

### 1. 🟠 假设零手续费（set_commission 缺失/为 0）

`KD指标量化交易策略.py:34` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
close_today_commission=0,
```

**证据引用：** `local-rule:1348f5bc7e1a090e`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

