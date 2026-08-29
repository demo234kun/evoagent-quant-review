# EvoAgent 量化代码审查

**Repository:** `聚宽2024/基于XGBoost6m滚动选股策略`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 20 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `17`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `198 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:88` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price(g.hold_list, end_date=yesterday, frequency='daily', fields=['close','high_limit'], count=1, panel=False, fill_paused=False)
```

**证据引用：** `local-rule:dcdea9558181912d`, `diff-ast:cd1d969d5b1de0b0`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 策略逻辑使用了真实当前时间

`基于XGBoost6m滚动选股策略.py:100` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
start = datetime.datetime.now()
```

**证据引用：** `local-rule:9eac1c77dde84666`, `diff-ast:c9c5a3b92cd0b1ef`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 3. 🔴 策略逻辑使用了真实当前时间

`基于XGBoost6m滚动选股策略.py:114` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
end = datetime.datetime.now()
```

**证据引用：** `local-rule:28c4cfbd28aec069`, `diff-ast:4494e9fb4f8e617a`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 4. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:174` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
data_close[stock] = get_price(stock, date, date_list[date_list.index(date)+1], '1d', 'close')['close']
```

**证据引用：** `local-rule:6ebd306220d78d74`, `diff-ast:1d45299fc98140b2`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 5. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:197` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
data_close[stock] = get_price(stock, date, date_list[-1], '1d', 'close')['close']
```

**证据引用：** `local-rule:f2bd494d79a314fd`, `diff-ast:31e092b1bf44f714`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 6. 🔴 策略逻辑使用了真实当前时间

`基于XGBoost6m滚动选股策略.py:227` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
start = datetime.datetime.now()
```

**证据引用：** `local-rule:daead98f227e5550`, `diff-ast:5a741454b1a37cf8`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 7. 🔴 策略逻辑使用了真实当前时间

`基于XGBoost6m滚动选股策略.py:233` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
print('交叉验证时长：', datetime.datetime.now()-start)
```

**证据引用：** `local-rule:e16f34e05c91653f`, `diff-ast:8034f9beac756f52`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 8. 🔴 策略逻辑使用了真实当前时间

`基于XGBoost6m滚动选股策略.py:246` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
starttime = datetime.datetime.now()
```

**证据引用：** `local-rule:dd7824fa1779e160`, `diff-ast:28b7ea8c0a8676d5`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 9. 🔴 策略逻辑使用了真实当前时间

`基于XGBoost6m滚动选股策略.py:249` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
endtime = datetime.datetime.now()
```

**证据引用：** `local-rule:62aa89e57acd22f4`, `diff-ast:8ff05119b4779382`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 10. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:374` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
df = get_price('000001.XSHE', start_date, end_date, fields=['close'])
```

**证据引用：** `local-rule:fb063417b03e28f3`, `diff-ast:c417e46d40448fec`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 11. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:552` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
SZ_close = get_price('000001.XSHG', count = 60*20+1, end_date=date, frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:9a9e4422c7974eec`, `diff-ast:9b3c19578b6419a4`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 12. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:628` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
dp = get_price('000300.XSHG', count=12*20+1, end_date=date, frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:2208eb174f46cf2c`, `diff-ast:ae8548d0ae1b81e8`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 13. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`基于XGBoost6m滚动选股策略.py:696` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
current_data = get_price(stock, end_date=now_time, frequency='1m', fields=['close','high_limit'], skip_paused=False, fq='pre', count=1, panel=False, fill_paused=True)
```

**证据引用：** `local-rule:d9db6db5a704d191`, `diff-ast:649ac0911f5a30c0`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 14. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`基于XGBoost6m滚动选股策略.py:106` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
curr_stock_list = get_index_stocks('000002.XSHG', today) + get_index_stocks('399107.XSHE', today)
```

**证据引用：** `local-rule:b98fc46bf1155990`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 15. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`基于XGBoost6m滚动选股策略.py:108` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
# curr_stock_list = get_index_stocks('000300.XSHG', today) + get_index_stocks('000852.XSHG', today) + get_index_stocks('399905.XSHE', today)
```

**证据引用：** `local-rule:1d53ad73682f7b14`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 16. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`基于XGBoost6m滚动选股策略.py:111` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
curr_stock_list = get_index_stocks(g.benchmark, today)
```

**证据引用：** `local-rule:9afb45704afba9b3`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 17. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`基于XGBoost6m滚动选股策略.py:142` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stock_list = get_index_stocks('000002.XSHG', date) + get_index_stocks('399107.XSHE', date)
```

**证据引用：** `local-rule:6e983da9b86ec7b7`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 18. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`基于XGBoost6m滚动选股策略.py:144` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
# stock_list = get_index_stocks('000300.XSHG', date) + get_index_stocks('000852.XSHG', date) + get_index_stocks('399905.XSHE', date)
```

**证据引用：** `local-rule:5043a9112c9274b6`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 19. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`基于XGBoost6m滚动选股策略.py:147` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stock_list = get_index_stocks(g.benchmark, date)
```

**证据引用：** `local-rule:8829eac364a9da26`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 20. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`基于XGBoost6m滚动选股策略.py:229` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
clf = GridSearchCV(g.regressor, g.parameters, scoring='roc_auc',
```

**证据引用：** `local-rule:2e4be0bc497f2a3b`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

