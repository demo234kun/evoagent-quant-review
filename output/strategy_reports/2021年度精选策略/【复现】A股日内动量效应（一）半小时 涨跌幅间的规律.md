# EvoAgent 量化代码审查

**Repository:** `聚宽2021/【复现】A股日内动量效应（一）半小时 涨跌幅间的规律`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 5 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `5`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `150 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:238` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
index_price = get_price(symbol, start, end, fields='close', panel=False)
```

**证据引用：** `local-rule:e2c7894cdf285b19`, `diff-ast:d845fdf0d2cfa815`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🟡 非交互式回测中调用 plt.show()

`【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:159` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:159`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 3. 🟡 非交互式回测中调用 plt.show()

`【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:180` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:180`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 4. 🟡 非交互式回测中调用 plt.show()

`【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:219` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:219`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 5. 🟡 非交互式回测中调用 plt.show()

`【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:249` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:【复现】A股日内动量效应（一）半小时 涨跌幅间的规律.py:249`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

