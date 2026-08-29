# EvoAgent 量化代码审查

**Repository:** `聚宽2024/大周期顶底判断：FED指标+格雷厄姆指数一次搞定`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 5 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `7`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `161 ms`

## 审查发现

### 1. 🔴 策略逻辑使用了真实当前时间

`大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:29` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
my_start_time=(datetime.datetime.now()-datetime.timedelta(days=my_days)).strftime("%Y-%m-%d")#根据my_days动态调整
```

**证据引用：** `local-rule:ca1deb615c6bcabf`, `diff-ast:5107307bc171525e`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 2. 🔴 策略逻辑使用了真实当前时间

`大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:30` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
my_end_time=datetime.datetime.now().strftime("%Y-%m-%d")#【注意，这里用datetime.datetime.now()不是根据回测动态，而是实际动态】
```

**证据引用：** `local-rule:057b930ac5ef00c1`, `diff-ast:e75eec10e8f80ae4`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:158` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
re=get_price("510300.XSHG", start_date=my_start_time, end_date=my_end_time, frequency='daily', fields=["close"], fq='pre', panel=False)
```

**证据引用：** `local-rule:bdd9788c2d68ab9d`, `diff-ast:9e118f01643b580b`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🟡 非交互式回测中调用 plt.show()

`大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:208` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:208`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 5. 🟡 非交互式回测中调用 plt.show()

`大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:238` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:大周期顶底判断：FED指标+格雷厄姆指数一次搞定.py:238`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

