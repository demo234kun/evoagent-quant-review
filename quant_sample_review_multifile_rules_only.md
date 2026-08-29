# EvoAgent 量化代码审查 — #7

**Repository:** `demo/quant-strategy`  
**Risk:** `high`  
**Reviewer:** `mode-router`

已审查 3 个文件；发现 19 个可处理问题。整体风险：高。

## 执行概况

- 模式：请求 `rules-only`，实际 `rules-only`
- 模型调用: `0`；工具调用: `13`
- Token：输入 `0`、输出 `0`、合计 `0`
- Token 成本: `$0.00000000`；延迟: `297 ms`

## 审查发现

### 1. 🚨 回测使用未来数据 (shift(-N))

`strategy/factors.py:47` · **CRITICAL** · `QUANT-FF-SHIFT-NEG`

用 df.shift(-1) 等把下一根 bar 的数据对齐到当前行，会让信号偷看到未发生的价格，回测收益虚高。

**证据**

```text
df["fwd_ret"] = df["close"].shift(-1) / df["close"] - 1            # QUANT-FF-SHIFT-NEG
```

**证据引用：** `local-rule:3486f0305a2918cb`, `diff-ast:52b11ab03be2215f`

**修复建议：** 需要用到未来信息时改为 shift(正数) 或显式构造下一根标签；因子与信号必须只用当前及之前的数据。

**测试建议：** 构造一个已知结果的DataFrame，断言信号行不会引用其后的价格。

### 2. 🚨 公式引用未来数据 (ref(x, -N))

`strategy/factors.py:48` · **CRITICAL** · `QUANT-FF-REF-NEG`

配方语言里 ref(x, -N) 表示向后引用，等同于把未来数据搬到了当前，属于典型未来函数。

**证据**

```text
df["lead"] = ref(close, -1)                                         # QUANT-FF-REF-NEG
```

**证据引用：** `local-rule:1264e392ba425aa9`, `diff-ast:52a97dd81ac63d51`

**修复建议：** 把负偏移改为正偏移；确认指标平台对 ref 的语义，避免误用负周期。

**测试建议：** 用一张手算对照表断言指标在 t 时刻只用 t 及之前的值。

### 3. 🔴 使用后复权 (post) 做历史决策，含未来除权信息

`strategy/execution.py:14` · **HIGH** · `QUANT-DQ-ADJUST-POST`

后复权价格把未来分红/除权折算进历史价，用其回测等于前视。

**证据**

```text
prices = get_price('000001.XSHE', fq='post')         # QUANT-DQ-ADJUST-POST
```

**证据引用：** `local-rule:4b310b8fd0404699`, `diff-ast:f43aa84869a0c90b`

**修复建议：** 历史决策使用不复权或前复权；后复权仅用于展示。

**测试建议：** 断言因子计算所用价格口径不含未来除权信息。

### 4. 🔴 策略逻辑使用了真实当前时间

`strategy/factors.py:49` · **HIGH** · `QUANT-FF-DATETIME-NOW`

datetime.now()/today() 返回实盘运行时刻，在回测里会变成未来时刻，造成前视偏差。

**证据**

```text
now = datetime.now()                                               # QUANT-FF-DATETIME-NOW
```

**证据引用：** `local-rule:5b6c118425290477`, `diff-ast:30f2b97014844005`

**修复建议：** 改用回测框架提供的当前 bar 时间（如 context.current_dt / bar.datetime）。

**测试建议：** 断言回测中读取的时间为对应 bar 的时间而非系统当前时间。

### 5. 🔴 行情接口以当前时刻为结束日（包含未发生的 bar）

`strategy/factors.py:50` · **HIGH** · `QUANT-FF-GETPRICE-NOW`

JoinQuant 的 get_price/attribute_history 在 end_date=context.current_dt 时会把当根 bar 也算入，若据此下单即为未来函数。

**证据**

```text
prices = get_price("000001.XSHE", end_date=context.current_dt)     # QUANT-FF-GETPRICE-NOW
```

**证据引用：** `local-rule:9fda79e2d255abb4`, `diff-ast:1c4d1a0067815a18`

**修复建议：** 用 context.previous_date 作为结束日，或改用 history()（默认不含当根）。

**测试建议：** 断言行情查询的结束日早于当前信号 bar。

### 6. 🔴 Backtrader cheat-on-close 导致用当日收盘价成交

`strategy/factors.py:51` · **HIGH** · `QUANT-FF-CHEAT-CLOSE`

set_coc(True) 允许在当前 bar 收盘价下单并成交，若信号又基于该 bar 收盘价，则回测前视。

**证据**

```text
cerebro.broker.set_coc(True)                                       # QUANT-FF-CHEAT-CLOSE
```

**证据引用：** `local-rule:bb1e46be4465c685`, `diff-ast:7bce606712ce7ce9`

**修复建议：** 保持 set_coc(False) 或修改信号使其在下根 bar 才成交。

**测试建议：** 构造一个信号=当日收盘价的用例，断言成交发生在下根而非当根。

### 7. 🔴 在全样本上 fit_transform 造成数据泄露

`strategy/factors.py:52` · **HIGH** · `QUANT-LK-FULL-NORM`

在训练/测试切分之前对整个数据集 fit_transform，会让测试集的统计信息泄漏进训练。

**证据**

```text
Xs = scaler.fit_transform(X)                                       # QUANT-LK-FULL-NORM
```

**证据引用：** `local-rule:bf92f9f0090dadde`, `diff-ast:b9c7bec5885250d7`

**修复建议：** 先切分再分别在训练集 fit，并用同一 scaler 仅 transform 测试集。

**测试建议：** 对比全样本缩放与时序切分缩放下的测试集指标，断言两者不同且后者更保守。

### 8. 🔴 用全样本均值/标准差做标准化（前视泄露）

`strategy/factors.py:53` · **HIGH** · `QUANT-LK-FULL-ZSCORE`

用整段序列的 mean/std 逐行标准化，每行都隐含了未来样本的信息。

**证据**

```text
z = (df["close"] - df["close"].mean()) / df["close"].std()         # QUANT-LK-FULL-ZSCORE
```

**证据引用：** `local-rule:c21ddb54a882ab3f`, `diff-ast:c85e3f6645425803`

**修复建议：** 改为滚动/扩展窗口的标准化，或使用训练集统计量。

**测试建议：** 断言标准化所用的统计量仅来自该行之前的数据。

### 9. 🔴 疑似硬编码交易凭据

`strategy/risk.py:3` · **HIGH** · `QUANT-SEC-HARDCODED-KEY`

交易账号、API Key、token 进入代码仓库后会通过历史记录与构建日志泄露。

**证据**

```text
api_key = "sk-live-abcdef123456"                    # QUANT-SEC-HARDCODED-KEY
```

**证据引用：** `local-rule:56c85a841fcf4e4d`, `diff-ast:50812e26dd248ef6`

**修复建议：** 改为从密钥管理或环境变量读取，并立即轮换已提交的凭据。

**测试建议：** 测试缺失配置时安全失败，且日志不会输出凭据。

### 10. 🟠 假设零滑点（set_slippage 缺失/为 0）

`strategy/execution.py:8` · **MEDIUM** · `QUANT-EX-ZERO-SLIP`

滑点设为 0 会让回测成交价过于理想，实盘滑点会吞噬收益。

**证据**

```text
cerebro.broker.set_slippage(slip_perc=0)        # QUANT-EX-ZERO-SLIP
```

**证据引用：** `local-rule:846c1469a71c18ab`

**修复建议：** 设置合理的滑点模型（百分比或固定），并在参数中显式声明。

**测试建议：** 对比零滑点与真实滑点下的收益与回撤差异。

### 11. 🟠 假设零手续费（set_commission 缺失/为 0）

`strategy/execution.py:9` · **MEDIUM** · `QUANT-EX-ZERO-COMM`

手续费为 0 会高估高频/换手策略收益。

**证据**

```text
cerebro.broker.set_commission(commission=0)     # QUANT-EX-ZERO-COMM
```

**证据引用：** `local-rule:9ce373249dfb3e67`

**修复建议：** 设置与券商一致的佣金、印花税与最低手续费。

**测试建议：** 断言手续费计入后收益曲线符合预期。

### 12. 🟠 参数寻优未做 walk-forward 易过拟合

`strategy/execution.py:11` · **MEDIUM** · `QUANT-OF-OPTSTRATEGY`

对全样本 optstrategy 寻优会把样本内噪声当成规律，样本外失效。

**证据**

```text
cerebro.optstrategy(MyStrategy, period=range(5, 20))  # QUANT-OF-OPTSTRATEGY
```

**证据引用：** `local-rule:d6f5f46641ffc90d`

**修复建议：** 采用 walk-forward / 滚动窗口，并在样本外验证。

**测试建议：** 对比样本内最优参数与样本外表现，断言二者差距在阈值内。

### 13. 🟠 网格寻优需使用时序交叉验证避免数据窥探

`strategy/execution.py:13` · **MEDIUM** · `QUANT-OF-GRIDSEARCH`

对时间序列用普通 K 折会把未来折的信息泄漏给训练折。

**证据**

```text
grid = GridSearchCV(model, {'C': [0.1, 1, 10]})       # QUANT-OF-GRIDSEARCH
```

**证据引用：** `local-rule:340d8886212b04ee`

**修复建议：** 改用 TimeSeriesSplit / Purged K-Fold 等时序交叉验证。

**测试建议：** 断言交叉验证切分保持时间顺序且测试折晚于训练折。

### 14. 🟠 向后填充 (bfill) 用未来值填补缺失，造成泄露

`strategy/factors.py:54` · **MEDIUM** · `QUANT-LK-FORWARD-FILL`

bfill 用后面的有效值回填前面的缺失，使前面的样本窥见未来。

**证据**

```text
df = df.fillna(method="bfill")                                     # QUANT-LK-FORWARD-FILL
```

**证据引用：** `local-rule:01b0f0fd7bcca91a`

**修复建议：** 改用 ffill 或丢弃缺失，且缺失处理必须在切分之后、只用历史信息。

**测试建议：** 构造含缺失序列的用例，断言回填逻辑不使用未来值。

### 15. 🟠 使用 statDate 拉取财报期数据，可能包含未披露数据

`strategy/factors.py:55` · **MEDIUM** · `QUANT-LK-STATDATE`

用 statDate 指定报告期会在报告实际发布前取到数据，形成前视。

**证据**

```text
q = get_fundamentals(query, statDate="2023-03-31")                 # QUANT-LK-STATDATE
```

**证据引用：** `local-rule:dd43c6c7c4fb9e2f`

**修复建议：** 用 point-in-time 的发布日字段，或在回测日之前取最近已披露财报。

**测试建议：** 断言取到的财报披露日不晚于回测当前日。

### 16. 🟠 取指数成分股未指定 date，默认当前成分（幸存者偏差）

`strategy/factors.py:56` · **MEDIUM** · `QUANT-LK-INDEX-NOW`

不传 date 时取到的是当前成分股，已剔除退市/调出股票，回测会幸存者偏差。

**证据**

```text
stocks = get_index_stocks("000300.XSHG")                           # QUANT-LK-INDEX-NOW
```

**证据引用：** `local-rule:044be841d2afd519`

**修复建议：** 传入回测对应的历史 date 参数获取当时成分股。

**测试建议：** 对比传入历史 date 与默认结果的成分股数量与标的差异。

### 17. 🟠 满仓下单且无风险控制

`strategy/risk.py:5` · **MEDIUM** · `QUANT-SEC-NO-RISK`

order_target_percent(..., 1.0) 等满仓操作缺少仓位与止损约束，实盘风险过大。

**证据**

```text
order_target_percent(context.portfolio, 1.0)       # QUANT-SEC-NO-RISK
```

**证据引用：** `local-rule:29707cd3b6294c8b`

**修复建议：** 引入仓位上限、单标的权重与止损逻辑；遵守账户风险预算。

**测试建议：** 断言极端行情下仓位不超过预算上限。

### 18. 🟡 用 0 填补缺失值可能扭曲收益率

`strategy/execution.py:15` · **LOW** · `QUANT-DQ-FILLNA0`

价格/因子缺失填 0 会产生异常收益率并污染信号。

**证据**

```text
df = df.fillna(0)                                    # QUANT-DQ-FILLNA0
```

**证据引用：** `local-rule:0b66d938a096cf49`

**修复建议：** 用 ffill、插值或丢弃缺失，并在缺失处理时只用历史信息。

**测试建议：** 构造含缺失的用例，断言缺失行未被填成不合理数值。

### 19. 🟡 新增调试输出

`strategy/risk.py:6` · **LOW** · `QUANT-REL-DEBUG-PRINT`

直接输出可能污染日志或意外暴露运行数据。

**证据**

```text
print('debug signal', signal)                      # QUANT-REL-DEBUG-PRINT
```

**证据引用：** `local-rule:9799f05c79f22a20`

**修复建议：** 删除调试输出，或改用带级别和脱敏策略的结构化日志。

**测试建议：** 验证正常请求不会产生包含敏感值的非预期输出。

