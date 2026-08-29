# EvoAgent 量化代码审查

**Repository:** `聚宽2021/XGBoost模型多因子策略分享`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 1 个文件；发现 12 个可处理问题。整体风险：high。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `9`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `181 ms`

## 审查发现

### 1. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`XGBoost模型多因子策略分享.py:329` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
stock_close=get_price(stock, count = 60*20+1, end_date=date, frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:cfb1d3b742912d93`, `diff-ast:d8ec27d32a03994b`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 2. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`XGBoost模型多因子策略分享.py:330` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
SZ_close=get_price('000001.XSHG', count = 60*20+1, end_date=date, frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:eb3c9542b1e93e94`, `diff-ast:9c7e5b6a91b9ec24`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 3. 🔴 get_price 未指定结束日期，默认拉取当前时刻数据

`XGBoost模型多因子策略分享.py:401` · **HIGH** · `QUANT-FF-GETPRICE-NO-ENDDATE`

get_price 不传 end_date 时默认取到当前时刻，回测中等于使用了尚未发生的 bar，属于前视。

**证据**

```text
dp=get_price('000300.XSHG',count=12*20+1,end_date=date,frequency='daily', fields=['close'])['close']
```

**证据引用：** `local-rule:07fc94960066612b`, `diff-ast:a3e3018f1c893657`

**修复建议：** 显式传 end_date=context.previous_date 或使用 history()。

**测试建议：** 断言行情查询始终带有明确的结束日期且不晚于当前信号 bar。

### 4. 🔴 策略逻辑使用了真实当前时间

`XGBoost模型多因子策略分享.py:458` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
starttime = datetime.datetime.now()
```

**证据引用：** `local-rule:9703fcea8c601ab4`, `diff-ast:2309a94fe2624cc1`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 5. 🔴 策略逻辑使用了真实当前时间

`XGBoost模型多因子策略分享.py:471` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
endtime = datetime.datetime.now()
```

**证据引用：** `local-rule:1c26ff6786779ec0`, `diff-ast:054250197d9cc9f2`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 6. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:98` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
lst_000905 = get_index_stocks(g.index) # 指数成分股
```

**证据引用：** `local-rule:1c11a6b9456b63b4`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 7. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:147` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stockList=get_index_stocks('000300.XSHG',begin_date)
```

**证据引用：** `local-rule:0bdb63b87df1068a`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 8. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:149` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stockList=get_index_stocks('399905.XSHE',begin_date)
```

**证据引用：** `local-rule:5527977275f4a7d1`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 9. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:151` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stockList=get_index_stocks('399906.XSHE',begin_date)
```

**证据引用：** `local-rule:68da913568c099d1`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 10. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:153` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stockList=get_index_stocks('399006.XSHE',begin_date)
```

**证据引用：** `local-rule:ec218a482ebc34b0`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 11. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:155` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stockList=get_index_stocks('399005.XSHE',begin_date)
```

**证据引用：** `local-rule:4578065bffc493e8`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 12. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`XGBoost模型多因子策略分享.py:157` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stockList=get_index_stocks('000002.XSHG',begin_date)+get_index_stocks('399107.XSHE',begin_date)
```

**证据引用：** `local-rule:edf0322824aaa671`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

