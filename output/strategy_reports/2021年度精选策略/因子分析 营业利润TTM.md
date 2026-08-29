# EvoAgent 量化代码审查

**Repository:** `聚宽2021/因子分析 营业利润TTM`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 9 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `6`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `265 ms`

## 审查发现

### 1. 🚨 回测使用未来数据 (shift(-N))

`因子分析 营业利润TTM.py:1052` · **CRITICAL** · `QUANT-FF-SHIFT-NEG`

用 df.shift(-1) 等把下一根 bar 的数据对齐到当前行，会让信号偷看到未发生的价格，回测收益虚高。

**证据**

```text
month_return = price.pct_change().shift(-1)
```

**证据引用：** `local-rule:08c8a00985dcd714`, `diff-ast:94441460bf1c5be5`

**修复建议：** 需要用到未来信息时改为 shift(正数) 或显式构造下一根标签；因子与信号必须只用当前及之前的数据。

**测试建议：** 构造一个已知结果的DataFrame，断言信号行不会引用其后的价格。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`因子分析 营业利润TTM.py:133` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
price=get_price(all_stocks, start_date=date, end_date=date, frequency='1d',fields=['close'])['close']
```

**证据引用：** `local-rule:6f602316ab1d9900`, `diff-ast:3d29db26598f6388`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:518` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
month_return = (group_return.iloc[:, np.sign(direction-1)] - group_return.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:f4f61175f1ae1dbc`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 4. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:537` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
month_return = (group_return.iloc[:, np.sign(direction-1)] - group_return.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:1e8920cc2249e47d`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 5. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:586` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
month_return = (group_return.iloc[:, np.sign(direction-1)] - group_return.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:2833e3d992be2b17`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 6. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:951` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
hs300_excess_returns.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:1426914c689cb495`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 7. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:952` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
zz500_long_short_ret = (zz500_excess_returns.iloc[:, np.sign(direction-1)] - zz500_excess_returns.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:bac2e24f0e5a3478`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 8. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:953` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
a_long_short_ret = (a_excess_returns.iloc[:, np.sign(direction-1)] - a_excess_returns.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:654654e13d4c6609`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 9. 🟡 用 0 填补缺失值可能扭曲收益率

`因子分析 营业利润TTM.py:1010` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
month_return = (group_return.iloc[:, np.sign(direction-1)] - group_return.iloc[:, -np.sign(direction+1)]).fillna(0)
```

**证据引用：** `local-rule:8a3d3d45fad846ae`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

