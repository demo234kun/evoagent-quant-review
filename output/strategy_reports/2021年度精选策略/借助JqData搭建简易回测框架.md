# EvoAgent 量化代码审查

**Repository:** `聚宽2021/借助JqData搭建简易回测框架`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 6 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `7`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `205 ms`

## 审查发现

### 1. 🔴 策略逻辑使用了真实当前时间

`借助JqData搭建简易回测框架.py:123` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
time_start = datetime.datetime.now()
```

**证据引用：** `local-rule:fb0607d4065b52a4`, `diff-ast:a05ef11578b548c1`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 2. 🔴 策略逻辑使用了真实当前时间

`借助JqData搭建简易回测框架.py:138` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
time_end = datetime.datetime.now()
```

**证据引用：** `local-rule:b9185a53c245d1d0`, `diff-ast:3fe45c35bb9a613b`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 3. 🔴 策略逻辑使用了真实当前时间

`借助JqData搭建简易回测框架.py:140` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
print('End Time : {0}, Elapsed Time: {1}'.format(datetime.datetime.now(), time_end - time_start))
```

**证据引用：** `local-rule:34600fcf209ac7b9`, `diff-ast:7a4adfd86e906e7d`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 4. 🟡 非交互式回测中调用 plt.show()

`借助JqData搭建简易回测框架.py:348` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:借助JqData搭建简易回测框架.py:348`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 5. 🟡 非交互式回测中调用 plt.show()

`借助JqData搭建简易回测框架.py:379` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:借助JqData搭建简易回测框架.py:379`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 6. 🟡 非交互式回测中调用 plt.show()

`借助JqData搭建简易回测框架.py:392` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:借助JqData搭建简易回测框架.py:392`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

