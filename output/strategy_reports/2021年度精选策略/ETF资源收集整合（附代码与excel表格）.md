# EvoAgent 量化代码审查

**Repository:** `聚宽2021/ETF资源收集整合（附代码与excel表格）`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 3 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `156 ms`

## 审查发现

### 1. 🔴 策略逻辑使用了真实当前时间

`ETF资源收集整合（附代码与excel表格）.py:25` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
trade_date = get_trade_days(end_date=datetime.datetime.now(), count=10)
```

**证据引用：** `local-rule:63389849edbc2632`, `diff-ast:98c8f3cccd8331da`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 2. 🔴 策略逻辑使用了真实当前时间

`ETF资源收集整合（附代码与excel表格）.py:133` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
trade_date = get_trade_days(end_date=datetime.datetime.now(), count=10)
```

**证据引用：** `local-rule:690b9438728c052e`, `diff-ast:ff7181c0a89c7d9c`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 3. 🟠 裸异常吞掉错误

`ETF资源收集整合（附代码与excel表格）.py:100` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except:
```

**证据引用：** `local-rule:49af756515f3f2c5`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

