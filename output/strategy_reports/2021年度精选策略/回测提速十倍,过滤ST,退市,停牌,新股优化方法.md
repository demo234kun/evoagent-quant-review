# EvoAgent 量化代码审查

**Repository:** `聚宽2021/回测提速十倍,过滤ST,退市,停牌,新股优化方法`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 2 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `168 ms`

## 审查发现

### 1. 🔴 策略逻辑使用了真实当前时间

`回测提速十倍,过滤ST,退市,停牌,新股优化方法.py:64` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
start=datetime.now()
```

**证据引用：** `local-rule:e1c0ba9768a714df`, `diff-ast:10693102f59bfed6`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 2. 🔴 策略逻辑使用了真实当前时间

`回测提速十倍,过滤ST,退市,停牌,新股优化方法.py:66` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
g.total_time+=(datetime.now()-start).microseconds
```

**证据引用：** `local-rule:b98eebdd14910fb1`, `diff-ast:2b15a500daaeac0b`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

