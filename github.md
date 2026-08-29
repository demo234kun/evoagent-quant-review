# EvoAgent 量化代码审查平台

EvoAgent 是一个面向量化策略代码的自动化审查平台：接收代码 diff，用量化专属规则做确定性扫描，可选接入 DeepSeek 做 LLM 辅助审查，输出带证据链的结构化问题报告，并基于真实策略数据持续迭代规则。

## 目录

- [背景与定位](#背景与定位)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [运行模式](#运行模式)
- [规则引擎](#规则引擎)
- [问题记忆库](#问题记忆库)
- [Skill 插件机制](#skill-插件机制)
- [批量策略审查](#批量策略审查)
- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [配置项](#配置项)
- [API 参考](#api-参考)
- [测试](#测试)
- [目录结构](#目录结构)

## 背景与定位

量化策略代码存在未来函数、数据泄露、过拟合等专业问题，这些 bug 需要领域知识才能识别：

- 通用代码审查工具（SonarQube 等）不认识 `df.shift(-1)` 是偷看未来价格；
- LLM 直接审查会幻觉，编造不存在的代码问题；
- 人工审查慢、标准不一、经验不沉淀。

EvoAgent 的解法是三层组合：**确定性规则扫描（可信） + LLM 辅助审查（覆盖面） + 记忆库沉淀（经验复用）**。

## 核心功能

1. **量化规则审查引擎**：22 条量化专属规则，覆盖未来函数、数据泄露、交易安全、执行成本、过拟合、数据质量、代码质量七类；每条命中强制引用 diff 真实代码行作为证据，输出严重级别、路径行号、证据、修复建议与测试建议。
2. **问题归类去重**：问题按类别分组展示，同一位置同类问题只保留最高严重级别一条，消除重复噪音。
3. **三档运行模式**：`rules-only` 纯规则扫描 / `hybrid` 规则 + 单个 LLM / `agentic` 多角色 LLM 审查；无模型或模型失灵时自动降级，报告如实标注降级原因。
4. **LLM 多角色编排**（agentic）：Planner / Security / Correctness-Re<liability / Critic 四个角色协同审查，自研 Agent Runtime 支持工具调用、参数 Schema 校验、Token 预算、断点续跑；Critic 盲审 + 证据门禁防止幻觉。
5. **问题记忆库**：审查结果按策略名与类别持久化入库，成为后续审查的经验参照，可跨任务检索复用。
6. **规则进化闭环**：基于全量真实命中数据迭代规则——先扫描建立基线，统计命中分布定位误报，收敛误报规则、新增实战规则，再重跑验证效果。
7. **Skill 插件机制**：规则可打包为带清单与校验的插件，经 SHA-256 完整性校验、危险模块黑名单与沙箱隔离后动态加载，无需发版即可扩展规则。

## 系统架构

```text
HTTP / GitHub Webhook
        │
        ▼
 ReviewService ── TaskStore(SQLite / PostgreSQL)
        │
        ▼
 ReviewHarness (Agent Runtime / checkpoint / resume / budget / trace)
        │
        ├── DiffParser
        ├── Redis Streams / ACK / lease / retry / DLQ
        ├── ContextManager (unified token budget / iterative context compression)
        ├── MemoryManager (working / episodic / semantic / consolidation / expiry)
        └── ModeRouter
              ├── rules-only：规则/声明式 Scanner → Gates
              ├── hybrid：Scanner + 单 LLM Agent → Gates
              └── agentic：Planner / Security / Correctness / Critic → Gates
```

Harness 状态流转：`PENDING → PLANNING → EXECUTING → REVIEWING → SUCCESS`。只有 `hybrid` 和 `agentic` 会进入模型决策循环，`rules-only` 完全离线确定性执行。

## 运行模式

| 模式 | 说明 | 模型调用 | 适用场景 |
|---|---|---|---|
| `rules-only` | 纯规则扫描 + 门禁 | 无 | 零成本 CI 门禁、大批量扫描 |
| `hybrid` | 规则扫描 + 单个 LLM 综合审查 | 1 个 | 常规 PR 审查 |
| `agentic` | 四个角色协同 + 证据链验证 | 多角色 | 高价值/高风险代码深度审查 |

无模型或模型调用失败时自动降级到 `rules-only`，报告中的 `run_mode.fallback_reason` 如实标注原因，不假装调用过大模型。

## 规则引擎

内置 22 条规则，按类别组织：

| 类别 | 示例规则 | 说明 |
|---|---|---|
| 未来函数 | `QUANT-FF-SHIFT-NEG` | `df.shift(-1)` 偷看未来价格 |
| | `QUANT-FF-REF-NEG` | `ref(x, -1)` 公式后向引用 |
| | `QUANT-FF-DATETIME-NOW` | `datetime.now()` 在回测中成为未来时刻 |
| | `QUANT-FF-GETPRICE-NOW` | 行情查询以当前时刻为结束日 |
| | `QUANT-FF-GETPRICE-NO-ENDDATE` | `get_price` 未指定结束日期 |
| | `QUANT-FF-CHEAT-CLOSE` | `set_coc(True)` 用当日收盘价成交 |
| 数据泄露 | `QUANT-LK-FULL-NORM` | 全样本 `fit_transform` |
| | `QUANT-LK-FULL-ZSCORE` | 全样本 mean/std 标准化 |
| | `QUANT-LK-FORWARD-FILL` | `bfill` 用未来值回填 |
| | `QUANT-LK-STATDATE` | `statDate` 取未披露财报 |
| | `QUANT-LK-INDEX-NOW` | 成分股未指定历史 date |
| 交易安全 | `QUANT-SEC-HARDCODED-KEY` | 硬编码凭据 |
| | `QUANT-SEC-NO-RISK` | 满仓无风险控制 |
| 执行成本 | `QUANT-EX-ZERO-SLIP` | 零滑点假设 |
| | `QUANT-EX-ZERO-COMM` | 零手续费假设 |
| | `QUANT-EX-ZERO-ORDERCOST` | `set_order_cost` 佣金/税费为 0 |
| 过拟合 | `QUANT-OF-OPTSTRATEGY` | 无 walk-forward 寻优 |
| | `QUANT-OF-GRIDSEARCH` | 普通 K 折网格搜索 |
| 数据质量 | `QUANT-DQ-ADJUST-POST` | 后复权做历史决策 |
| | `QUANT-DQ-FILLNA0` | `fillna(0)` 扭曲收益率 |
| 代码质量 | `QUANT-REL-DEBUG-PRINT` | 打印敏感数据 |
| | `QUANT-REL-NO-EXCEPTION` | 裸 except 吞错误 |
| | `QUANT-CQ-BLOCKING-SLEEP` | 阻塞式 sleep（skill） |
| | `QUANT-CQ-DEBUG-PLOT` | 无人值守环境 `plt.show`（skill） |
| | `QUANT-CQ-UNSAFE-EVAL` | `eval/exec` 动态执行（skill） |

每条命中强制引用 diff 真实代码行（`evidence_refs`），防 LLM 幻觉也防规则误报。同一位置同类问题只保留最高严重级别。

## 问题记忆库

- 审查结果按 `repository`（策略名）与 `category`（问题类别）持久化到 `findings_bank` 表；
- 支持按 `rule_id` / `severity` / `repository` 过滤查询，附统计接口（总数、严重级别分布、规则分布）；
- Web 管理台按类别分组展示，展开可看每条命中位置与证据；
- 记忆库即"经验沉淀"：同一类问题在不同策略中的反复出现，为规则迭代提供数据支撑。

## Skill 插件机制

Skill 是运行时热插拔的规则包，每个 Skill 一个目录：

```text
skills/code-quality/
├── skill.json    # 清单：name / version / entrypoint / sha256 / permissions
└── skill.py      # 规则实现（继承 Reviewer，返回 Finding）
```

加载链路三道安全闸门：

1. **完整性校验**：`sha256` checksum 对比 + 可选 HMAC 签名；
2. **静态黑名单**：AST 解析禁止导入 `ctypes / socket / subprocess / urllib` 等危险模块；
3. **沙箱隔离**：子进程运行；配置容器镜像时升级为 Docker 沙箱（`--network none --read-only --cap-drop ALL --pids-limit --memory --cpus` 全限制）。

Skill 与内置规则并列参与审查，命中结果一样进入 findings 与记忆库。

## 批量策略审查

`batch_review_strategies.py` 支持对本地策略库按年份目录批量审查：

```powershell
# 全部年份
python -X utf8 batch_review_strategies.py

# 只测某一年（试跑前 5 个）
python -X utf8 batch_review_strategies.py -Year 2020 -Limit 5

# 指向远程服务（VPS，自签名证书需 -NoVerify）
python -X utf8 batch_review_strategies.py -Server https://1.2.3.4 -NoVerify -Password <密码>
```

行为：

- 遍历年份目录，按文件名提取策略名（去除序号前缀、`-Clone` 后缀）；
- 兼容 GBK / UTF-8 混合编码；
- 每个策略一个 diff 提交审查，`repository` 记为 `聚宽YYYY/策略名`；
- 逐策略生成独立 Markdown 报告（`output/strategy_reports/<年份>/<策略名>.md`）；
- 输出汇总表 `_summary.md`（含各策略问题数与严重级别分布）与规则命中分布。

## 快速开始

### 本地运行（SQLite 模式）

```powershell
python -m pip install -r requirements.txt

$env:EVOAGENT_AUTH_REQUIRED = 'true'
$env:EVOAGENT_AUTH_SECRET = [Convert]::ToBase64String((New-Object byte[] 32))
$env:EVOAGENT_BOOTSTRAP_ADMIN_USERNAME = 'admin'
$env:EVOAGENT_BOOTSTRAP_ADMIN_PASSWORD = '<至少10位强密码>'

python -m evoagent
```

服务默认监听 `127.0.0.1:8080`，打开 `http://127.0.0.1:8080/` 使用管理台。

### 提交一次审查

```powershell
$session = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8080/v1/auth/login `
  -ContentType 'application/json' -Body '{"username":"admin","password":"<密码>"}'
$headers = @{Authorization="Bearer $($session.access_token)"}
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8080/v1/reviews `
  -Headers $headers -ContentType 'application/json' -Body (@{
    repository = 'demo/api'; mode = 'rules-only'
    diff = "diff --git a/strategy.py b/strategy.py`n--- a/strategy.py`n+++ b/strategy.py`n@@ -1 +1,2 @@`n+df['ret'] = df['close'].shift(-1)"
  } | ConvertTo-Json)
```

### 启用 DeepSeek

```powershell
$env:EVOAGENT_LLM_PROVIDER = 'deepseek'
$env:EVOAGENT_DEEPSEEK_API_KEY = '<key>'
python -m evoagent
```

模型默认 `deepseek-chat`。未配置模型时自动降级为 `rules-only`。

## Docker 部署

### 本地 Compose（PostgreSQL + Redis）

```powershell
Copy-Item .env.example .env   # 然后编辑 .env 填入真实值
docker compose up --build
```

### 生产部署（VPS）

仓库提供生产部署包：

- `docker-compose.prod.yml`：生产 compose（含 PostgreSQL + Redis + EvoAgent）
- `Caddyfile`：Caddy 反向代理 + 自动 HTTPS
- `.env.prod.example`：生产环境变量模板
- `push_image.ps1`：推送镜像到 Docker Hub
- `deploy.ps1`：VPS 一键部署脚本
- `部署手册.md`：详细部署步骤

## 配置项

完整配置见 `.env.example`，核心项：

| 变量 | 说明 |
|---|---|
| `EVOAGENT_LLM_PROVIDER` | `local` / `deepseek` / `openrouter-deepseek-free` / `custom` |
| `EVOAGENT_DEEPSEEK_API_KEY` | DeepSeek API Key |
| `EVOAGENT_DEFAULT_RUN_MODE` | `rules-only` / `hybrid` / `agentic`，留空按模型可用性自动降级 |
| `EVOAGENT_DATABASE_URL` | PostgreSQL URL，留空用 SQLite |
| `EVOAGENT_REDIS_URL` | Redis URL，留空用进程内队列 |
| `EVOAGENT_AUTH_REQUIRED` | 暴露到公网必须 `true` |
| `EVOAGENT_SKILLS_DIR` | Skill 插件目录 |
| `EVOAGENT_MAX_DIFF_BYTES` | diff 大小上限（默认 1 MiB） |

密钥只通过环境变量读取，**不要提交 `.env`**（已在 `.gitignore` 中排除）。

## API 参考

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/health` | 健康检查 |
| `POST` | `/v1/auth/login` | 登录获取 Bearer Token |
| `POST` | `/v1/reviews` | 创建审查任务（同步，`?async=true` 异步） |
| `GET` | `/v1/tasks/{id}` | 任务状态、轨迹与报告 |
| `GET` | `/v1/tasks/{id}/report` | Markdown 报告 |
| `POST` | `/v1/tasks/{id}/feedback` | 回流误报/漏报反馈 |
| `GET` | `/v1/findings-bank` | 问题记忆库（含统计） |
| `POST` | `/v1/backtests` | 策略回测 |
| `POST` | `/webhooks/github` | GitHub PR webhook |
| `GET` | `/metrics` | Prometheus 指标 |
| `GET` | `/api/audit` | 审计日志 |
| `GET` | `/api/alerts` | 告警 |

## 测试

```powershell
python -m pytest tests/ -q
```

## 目录结构

```text
coding/
├── evoagent/               # 核心包
│   ├── reviewer.py         # 规则引擎（22 条内置规则）
│   ├── agentic_core.py     # 多角色 LLM 编排
│   ├── agents.py           # 多智能体协作协议
│   ├── runtime.py          # Agent Runtime / checkpoint / resume
│   ├── service.py          # 业务编排（审查/回测/反馈）
│   ├── api.py              # HTTP 服务
│   ├── store.py            # SQLite 存储
│   ├── postgres_store.py   # PostgreSQL 存储
│   ├── task_queue.py       # Redis Streams 队列
│   ├── report.py           # Markdown 报告生成
│   ├── modes.py            # 运行模式与降级
│   └── skills.py           # Skill 注册表与沙箱
├── web/                    # Web 管理台（原生 JS/CSS/HTML）
├── skills/                 # Skill 插件
├── scripts/                # 工具脚本（PDF 渲染、评测等）
├── tests/                  # 单元测试
├── batch_review_strategies.py  # 批量策略审查脚本
├── docker-compose.yml      # 本地 Compose
├── docker-compose.prod.yml # 生产 Compose
├── Dockerfile
└── README.md
```

## 免责声明

本项目用于量化策略代码的质量审查研究。审查结论为辅助参考，不构成投资建议。批量审查脚本仅处理本地策略文件，不抓取、不传播第三方内容。
