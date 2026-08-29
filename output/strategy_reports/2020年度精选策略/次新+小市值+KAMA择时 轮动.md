# EvoAgent 量化代码审查

**Repository:** `聚宽2020/次新+小市值+KAMA择时 轮动`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 1 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `148 ms`

## 审查发现

### 1. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`次新+小市值+KAMA择时 轮动.py:122` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
close_long = get_price(security, end_date=context.current_dt, frequency='10m', fields=['close'], count= period +2*4*6 )['close'].values;
```

**证据引用：** `local-rule:d1485b12ec446c67`, `diff-ast:32d3a6b6c3fada68`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

