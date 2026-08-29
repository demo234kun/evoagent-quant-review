# EvoAgent 量化代码审查

**Repository:** `聚宽2021/基于期权PCR与标的波动率价差的股指期货套利`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 6 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `9`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `152 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于期权PCR与标的波动率价差的股指期货套利.py:134` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
call_money = get_price(call,end_date=today ,fields='money',count=1,panel=False)
```

**证据引用：** `local-rule:1e9c4e30db2e5b7d`, `diff-ast:29f320f5ef4b2377`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于期权PCR与标的波动率价差的股指期货套利.py:135` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
call_volume = get_price(call,end_date=today ,fields='volume',count=1,panel=False)
```

**证据引用：** `local-rule:4a28ff3602e90955`, `diff-ast:21dcd0148bc79861`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于期权PCR与标的波动率价差的股指期货套利.py:136` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
put_money = get_price(put,end_date=today,fields='money',count=1,panel=False)
```

**证据引用：** `local-rule:8aa048d361697ea5`, `diff-ast:66a563b077f8b63c`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于期权PCR与标的波动率价差的股指期货套利.py:137` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
put_volume = get_price(put,end_date=today,fields='volume',count=1,panel=False)
```

**证据引用：** `local-rule:36781e6e2d67171d`, `diff-ast:bea0ae4dca3ead64`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于期权PCR与标的波动率价差的股指期货套利.py:142` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
etf_return = get_price(g.code,end_date=today,fields='close',count=21,panel=False).close.pct_change().dropna().tolist()
```

**证据引用：** `local-rule:941ecba2c90cc702`, `diff-ast:6ee9385bccfd9251`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 6. 🟠 裸异常吞掉错误

`基于期权PCR与标的波动率价差的股指期货套利.py:157` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except:
```

**证据引用：** `local-rule:ba18bb1aff083beb`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

