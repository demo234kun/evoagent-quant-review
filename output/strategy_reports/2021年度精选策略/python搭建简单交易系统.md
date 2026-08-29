# EvoAgent 量化代码审查

**Repository:** `聚宽2021/python搭建简单交易系统`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 7 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `7`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `193 ms`

## 审查发现

### 1. 🟠 裸异常吞掉错误

`python搭建简单交易系统.py:136` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except Exception:
```

**证据引用：** `local-rule:67bfea2948aa7283`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

### 2. 🟠 裸异常吞掉错误

`python搭建简单交易系统.py:161` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except Exception:
```

**证据引用：** `local-rule:83e0d14eee564d81`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

### 3. 🟠 裸异常吞掉错误

`python搭建简单交易系统.py:398` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except Exception:
```

**证据引用：** `local-rule:36bef2951e32c624`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

### 4. 🟠 裸异常吞掉错误

`python搭建简单交易系统.py:549` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except:
```

**证据引用：** `local-rule:2555193b03665ee8`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

### 5. 🟠 裸异常吞掉错误

`python搭建简单交易系统.py:716` · **MEDIUM** · `QUANT-REL-NO-EXCEPTION`

裸 except 或 except Exception 后不处理、不记录，会掩盖数据或交易接口的真实错误，难以排查。

**证据**

```text
except:
```

**证据引用：** `local-rule:87c8eded5b7ac5e7`

**修复建议：** 捕获具体异常类型并记录错误上下文，或至少 log.exception。

**测试建议：** 构造异常输入，断言错误被记录且任务状态可见。

### 6. 🟡 非交互式回测中调用 plt.show()

`python搭建简单交易系统.py:345` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:python搭建简单交易系统.py:345`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 7. 🟡 非交互式回测中调用 plt.show()

`python搭建简单交易系统.py:796` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:python搭建简单交易系统.py:796`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

