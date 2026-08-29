# EvoAgent 量化代码审查

**Repository:** `聚宽2023/lightGBM`  
**Risk:** `medium`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 10 个可处理问题。整体风险：medium。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `4`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `213 ms`

## 审查发现

### 1. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`lightGBM.py:202` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
```

**证据引用：** `local-rule:8d794824c7abbe68`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 2. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`lightGBM.py:240` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
```

**证据引用：** `local-rule:4c4ea75f1fb7da30`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 3. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`lightGBM.py:273` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
```

**证据引用：** `local-rule:c7a54d0647a37e9b`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 4. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`lightGBM.py:306` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
```

**证据引用：** `local-rule:b3f3323e1d7e1c06`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 5. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`lightGBM.py:341` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
```

**证据引用：** `local-rule:24c2c006ea5772b1`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 6. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`lightGBM.py:374` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
gsearch = GridSearchCV(gbm, param_grid=parameters, scoring='roc_auc', cv=3)
```

**证据引用：** `local-rule:4fe868f83a2b863e`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 7. 🟡 非交互式回测中调用 plt.show()

`lightGBM.py:496` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:lightGBM.py:496`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 8. 🟡 非交互式回测中调用 plt.show()

`lightGBM.py:574` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:lightGBM.py:574`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 9. 🟡 非交互式回测中调用 plt.show()

`lightGBM.py:650` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:lightGBM.py:650`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

### 10. 🟡 非交互式回测中调用 plt.show()

`lightGBM.py:709` · **LOW** · `QUANT-CQ-DEBUG-PLOT`

plt.show() 在无人值守的回测/调度环境会阻塞等待窗口关闭，使任务挂起。

**证据**

```text
plt.show()
```

**证据引用：** `scanner:QUANT-CQ-DEBUG-PLOT:lightGBM.py:709`

**修复建议：** 改用 plt.savefig 或将绘图移到独立的可视化脚本。

**测试建议：** 验证批处理模式下不会弹出窗口或阻塞进程。

