const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const titles = {
  overview: "运行总览",
  review: "发起审查",
  tasks: "任务中心",
  skills: "Skill 注册中心",
  evolution: "演进实验室",
  backtest: "策略回测",
  bank: "问题记忆库",
};

const stateLabels = {
  PENDING: "等待中",
  PLANNING: "规划中",
  EXECUTING: "执行中",
  REVIEWING: "汇总中",
  SUCCESS: "已完成",
  FAILED: "失败",
  CANCELLED: "已取消",
};

let selectedTask = null;
let selectedTaskData = null;
let accessToken = localStorage.getItem("evoagent_token") || "";
let toastTimer = null;
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function escapeHtml(value) {
  const node = document.createElement("div");
  node.textContent = value ?? "";
  return node.innerHTML;
}

function formatTime(value) {
  if (!value) return "时间未知";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : new Intl.DateTimeFormat("zh-CN", {
        month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit",
      }).format(date);
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  const response = await fetch(path, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("json") ? await response.json() : await response.text();

  if (response.status === 401) {
    $("#login-overlay").classList.remove("hidden");
    $("#logout").classList.add("hidden");
  }
  if (!response.ok) {
    const plainText = typeof data === "string" && !/<[a-z][\s\S]*>/i.test(data) ? data.trim() : "";
    const message = typeof data === "object"
      ? data.error || data.detail
      : plainText || `请求失败 (${response.status})`;
    throw new Error(message || response.statusText || "请求失败");
  }
  return data;
}

function toast(message) {
  const element = $("#toast");
  element.textContent = message;
  element.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => element.classList.remove("show"), 2600);
}

function setButtonBusy(button, busy, busyText) {
  if (!button) return;
  button.setAttribute("aria-busy", String(busy));
  if (busy) {
    button.dataset.label = button.innerHTML;
    button.disabled = true;
    button.textContent = busyText;
  } else {
    button.disabled = false;
    if (button.dataset.label) button.innerHTML = button.dataset.label;
  }
}

function show(view, updateHash = true) {
  if (!titles[view]) {
    view = "overview";
    history.replaceState(null, "", "#overview");
  }
  $$(".view").forEach((element) => element.classList.remove("active"));
  $$(".nav-item").forEach((element) => {
    const active = element.dataset.view === view;
    element.classList.toggle("active", active);
    element.setAttribute("aria-current", active ? "page" : "false");
  });
  $(`#view-${view}`).classList.add("active");
  $("#page-title").textContent = titles[view];
  document.title = `${titles[view]} · EvoAgent`;
  if (updateHash) history.replaceState(null, "", `#${view}`);

  if (view === "tasks") loadTasks();
  if (view === "skills") loadSkills();
  if (view === "evolution") loadFailures();
  if (view === "bank") loadBank();
  window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
}

$$(".nav-item").forEach((button) => button.addEventListener("click", () => show(button.dataset.view)));
$$("[data-jump]").forEach((button) => button.addEventListener("click", () => show(button.dataset.jump)));
window.addEventListener("hashchange", () => show(location.hash.slice(1), false));

function taskRows(tasks) {
  if (!tasks?.length) {
    return '<div class="empty-state"><span><b>还没有审查任务</b>提交一个 Diff 开始首次审查</span></div>';
  }
  return tasks.map((task) => {
    const state = String(task.state || "PENDING").toUpperCase();
    const repository = escapeHtml(task.repository || "未命名仓库");
    const pr = task.pull_request ? `审查 #${escapeHtml(task.pull_request)}` : "手动审查";
    return `
      <button class="task-row" data-task="${escapeHtml(task.id)}" type="button">
        <span class="task-main">
          <span class="task-glyph">审</span>
          <span class="task-copy">
            <span class="task-name">${repository}</span>
            <span class="task-meta"><span>${pr}</span><span>${escapeHtml(formatTime(task.created_at))}</span></span>
          </span>
        </span>
        <span class="status state-${state.toLowerCase()}">${stateLabels[state] || escapeHtml(state)}</span>
      </button>`;
  }).join("");
}

function bindTasks(root) {
  $$("[data-task]", root).forEach((row) => row.addEventListener("click", () => openTask(row.dataset.task)));
}

function statCard(label, value, note, style, icon) {
  return `<article class="stat ${style}">
    <div class="stat-head"><span>${label}</span><i>${icon}</i></div>
    <b>${value}</b><small>${note}</small>
  </article>`;
}

function renderLlmRuntime(llm = {}, runMode = {}) {
  const enabled = Boolean(llm.enabled);
  const failed = Boolean(llm.error);
  const provider = String(llm.provider || "local");
  const model = String(llm.model || "");
  const detail = failed
    ? "暂时无法读取模型配置"
    : enabled
      ? `${provider} / ${model || "默认模型"}，参与上下文审查与风险判断`
      : "未配置模型；仅运行确定性 Tool/Scanner 与 Gate，不会发生 Agent 讨论";
  const state = failed ? "读取失败" : enabled ? "已启用" : "待配置";
  const runtime = failed
    ? "运行时状态未知"
    : enabled
      ? `${provider} / ${model || "模型已配置"}`
      : "rules-only / 0 次模型调用";

  const effective = String(runMode.effective || (enabled ? "hybrid" : "rules-only"));
  const chain = $("#execution-chain");
  if (chain) {
    const scanner = '<div class="agent-step"><b>01</b><span><strong>Tool / Scanner</strong><small>规则、AST 与代码搜索提供事实</small></span><em>事实</em></div>';
    const gate = '<i class="flow-line"></i><div class="agent-step"><b>03</b><span><strong>Gate</strong><small>格式、证据、置信度与发布门禁</small></span><em class="done">门禁</em></div>';
    const llmStep = effective === "rules-only" ? "" : `<i class="flow-line"></i><div class="agent-step is-active" id="llm-agent-step"><b>02</b><span><strong>${effective === "agentic" ? "4-role LLM Agents" : "Single LLM Agent"}</strong><small id="llm-agent-detail">${escapeHtml(detail)}</small></span><em id="llm-agent-state">${escapeHtml(state)}</em></div>`;
    chain.innerHTML = scanner + llmStep + gate;
  }

  const step = $("#llm-agent-step");
  if (step) {
    step.classList.remove("is-pending");
    step.classList.toggle("is-active", enabled);
    step.classList.toggle("is-disabled", !enabled && !failed);
    step.classList.toggle("is-error", failed);
    const detailNode = $("#llm-agent-detail");
    const stateNode = $("#llm-agent-state");
    if (detailNode) detailNode.textContent = detail;
    if (stateNode) stateNode.textContent = state;
  }

  const status = $("#llm-runtime-status");
  status.className = `runtime-status ${failed ? "is-error" : enabled ? "is-active" : "is-disabled"}`;
  status.textContent = state;
  const capability = $("#llm-capability");
  capability.classList.toggle("is-active", enabled);
  capability.classList.toggle("is-disabled", !enabled && !failed);
  capability.classList.toggle("is-error", failed);
  $("#llm-capability-detail").textContent = detail;
  $("#llm-runtime-model").textContent = runtime;
}

async function loadDashboard() {
  try {
    const data = await api("/api/dashboard");
    renderLlmRuntime(data.llm, data.run_mode);
    const modeSelect = $("#review-mode");
    if (modeSelect) {
      modeSelect.value = data.run_mode?.effective || (data.llm?.enabled ? "hybrid" : "rules-only");
      $$('option[value="hybrid"], option[value="agentic"]', modeSelect).forEach((option) => {
        option.disabled = !data.llm?.enabled;
      });
    }
    $("#system-status").textContent = `${data.queue} · ${data.orchestrator}`;
    const stats = data.stats || {};
    const rate = Math.round(Number(stats.success_rate || 0) * 100);
    $("#stats").innerHTML = [
      statCard("总任务", stats.tasks_total ?? 0, "累计审查任务", "", "ALL"),
      statCard("已完成", stats.tasks_success ?? 0, "通过质量门禁", "success", "OK"),
      statCard("失败", stats.tasks_failed ?? 0, "需要进一步处理", "failed", "ERR"),
      statCard("成功率", `${rate}%`, "全部任务成功率", "rate", "RATE"),
      statCard("待处理案例", stats.unresolved_failure_cases ?? 0, "未解决反馈", "feedback", "OPEN"),
      statCard("活跃 Skills", stats.active_skill_versions ?? 0, "当前生效版本", "skills", "SK"),
    ].join("");
    $("#recent-tasks").innerHTML = taskRows((data.tasks || []).slice(0, 5));
    bindTasks($("#recent-tasks"));
  } catch (error) {
    renderLlmRuntime({ error: true }, {});
    $("#system-status").textContent = "服务连接异常";
    $("#stats").innerHTML = '<div class="empty-state"><span><b>暂时无法读取数据</b>请检查服务状态后重试</span></div>';
    $("#recent-tasks").innerHTML = '<div class="empty-state"><span>数据加载失败</span></div>';
    toast(error.message);
  }
}

async function loadTasks() {
  const root = $("#all-tasks");
  root.innerHTML = '<div class="list-loading"></div><div class="list-loading"></div>';
  try {
    const data = await api("/api/tasks");
    root.innerHTML = taskRows(data.tasks || []);
    bindTasks(root);
  } catch (error) {
    root.innerHTML = '<div class="empty-state"><span>任务加载失败</span></div>';
    toast(error.message);
  }
}

async function openTask(id) {
  show("tasks");
  $("#task-report").textContent = "正在加载任务报告…";
  $("#feedback-panel").classList.add("hidden");
  try {
    const task = await api(`/v1/tasks/${encodeURIComponent(id)}`);
    selectedTask = id;
    selectedTaskData = task;
    $("#task-report").textContent = formatJson(task);
    $("#create-fix").classList.toggle("hidden", !(task.report && task.pull_request));
    const feedbackReady = task.state === "SUCCESS" && task.report;
    $("#feedback-panel").classList.toggle("hidden", !feedbackReady);
    if (feedbackReady) {
      populateFeedbackFindings(task.report.findings || []);
      await loadTaskFeedback(id);
    }
  } catch (error) {
    $("#task-report").textContent = error.message;
    selectedTaskData = null;
  }
}

const feedbackLabels = {
  false_positive: "误报",
  missed_issue: "漏报",
  bad_fix: "坏修复",
  accepted: "已接受",
};

function populateFeedbackFindings(findings) {
  const select = $("#feedback-finding");
  select.innerHTML = '<option value="">不关联已有结论</option>' + findings.map((finding, index) => {
    const identity = `${finding.rule_id || "未命名规则"} · ${finding.path || "未知文件"}:${finding.line || "?"}`;
    return `<option value="${index}">${escapeHtml(identity)}</option>`;
  }).join("");
  $("#feedback-result").textContent = "";
}

function renderTaskFeedback(cases) {
  const root = $("#task-feedback-history");
  if (!cases.length) {
    root.innerHTML = '<p class="feedback-empty">尚无反馈。提交后，它会在这里保留并进入后续评测。</p>';
    return;
  }
  root.innerHTML = `<p class="list-section-label">本任务反馈</p>${cases.map((item) => {
    const payload = item.payload || {};
    const finding = payload.finding || {};
    const reference = finding.rule_id
      ? `${finding.rule_id}${finding.path ? ` · ${finding.path}:${finding.line || "?"}` : ""}`
      : "未关联审查结论";
    return `<div class="feedback-case">
      <span class="feedback-case-type">${escapeHtml(feedbackLabels[item.category] || item.category)}</span>
      <span class="feedback-case-copy"><b>${escapeHtml(reference)}</b><small>${escapeHtml(payload.note || "未填写说明")}</small></span>
      <span class="status ${item.resolved ? "state-success" : "state-pending"}">${item.resolved ? "已解决" : "待评测"}</span>
    </div>`;
  }).join("")}`;
}

async function loadTaskFeedback(taskId) {
  const root = $("#task-feedback-history");
  root.innerHTML = '<p class="feedback-empty">正在读取本任务反馈…</p>';
  try {
    const data = await api(`/v1/tasks/${encodeURIComponent(taskId)}/feedback`);
    if (selectedTask === taskId) renderTaskFeedback(data.cases || []);
  } catch (error) {
    root.innerHTML = `<p class="feedback-empty">无法读取反馈历史：${escapeHtml(error.message)}</p>`;
  }
}

async function loadSkills() {
  const root = $("#skill-list");
  root.innerHTML = '<div class="skill-card loading"></div><div class="skill-card loading"></div>';
  try {
    const data = await api("/api/skills");
    renderLlmRuntime(data.llm);
    const skills = (data.skills || []).filter((skill) => skill.name !== "llm-review");
    root.innerHTML = skills.length ? skills.map((skill) => `
      <article class="skill-card">
        <span class="skill-label">${skill.sandboxed ? "SANDBOXED SKILL" : "ACTIVE SKILL"}</span>
        <h3>${escapeHtml(skill.name)}</h3>
        <p>${escapeHtml(skill.description || "暂无能力描述")}</p>
        <span class="skill-meta">v${escapeHtml(skill.version)} · ${escapeHtml(skill.source)}</span>
      </article>`).join("") : '<div class="empty-state"><span><b>尚未加载 Skill</b>扫描目录以加载可用能力</span></div>';
  } catch (error) {
    renderLlmRuntime({ error: true });
    root.innerHTML = '<div class="empty-state"><span>Skills 加载失败</span></div>';
    toast(error.message);
  }
}

async function loadFailures() {
  try {
    const [failuresData, status, runsData] = await Promise.all([
      api("/api/failures"),
      api("/v1/evolution/status"),
      api("/v1/evolution/runs?limit=5"),
    ]);
    $("#evolution-status").textContent = formatJson(status);
    const cases = failuresData.cases || [];
    const runs = runsData.runs || [];
    const failureHtml = cases.length
      ? cases.slice(0, 8).map((item) => `
          <div class="task-row">
            <span class="task-main"><span class="task-glyph">FC</span><span class="task-copy">
              <span class="task-name">${escapeHtml(feedbackLabels[item.category] || item.category)}</span>
              <span class="task-meta"><span>${escapeHtml(item.task_id)}</span><span>${escapeHtml((item.payload || {}).note || "无说明")}</span></span>
            </span></span>
            <span class="status ${item.resolved ? "state-success" : "state-pending"}">${item.resolved ? "已解决" : "待处理"}</span>
          </div>`).join("")
      : '<div class="empty-state"><span><b>暂无失败反馈</b>系统当前没有未处理案例</span></div>';
    const historyHtml = runs.length
      ? `<p class="list-section-label">最近评测</p>${runs.map((run) => `
          <div class="task-row">
            <span class="task-main"><span class="task-glyph">V${escapeHtml(run.candidate_version)}</span><span class="task-copy">
              <span class="task-name">${escapeHtml(run.decision)}</span>
              <span class="task-meta">${Number(run.candidate_score).toFixed(3)} vs ${Number(run.baseline_score).toFixed(3)}</span>
            </span></span>
          </div>`).join("")}`
      : "";
    $("#failure-list").innerHTML = failureHtml + historyHtml;
  } catch (error) {
    $("#evolution-status").textContent = "暂时无法读取评测状态。";
    $("#failure-list").innerHTML = '<div class="empty-state"><span>反馈加载失败</span></div>';
    toast(error.message);
  }
}

$("#review-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  const values = new FormData(form);
  const body = { repository: values.get("repository"), diff: values.get("diff"), mode: values.get("mode") };
  if (values.get("pull_request")) body.pull_request = Number(values.get("pull_request"));
  const asyncQuery = values.get("async") ? "?async=true" : "";
  const output = $("#review-result");
  output.classList.remove("empty");
  output.textContent = "正在提交审查任务…";
  setButtonBusy(button, true, "正在提交…");
  try {
    const data = await api(`/v1/reviews${asyncQuery}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    output.textContent = formatJson(data);
    toast("审查任务已成功提交");
    loadDashboard();
  } catch (error) {
    output.textContent = error.message;
  } finally {
    setButtonBusy(button, false);
  }
});

$("#create-fix").addEventListener("click", async () => {
  if (!selectedTask) return;
  const button = $("#create-fix");
  setButtonBusy(button, true, "正在创建…");
  try {
    const data = await api(`/v1/tasks/${encodeURIComponent(selectedTask)}/fix`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    $("#task-report").textContent = formatJson(data);
    toast("修复分支已创建");
  } catch (error) {
    toast(error.message);
  } finally {
    setButtonBusy(button, false);
  }
});

$("#feedback-category").addEventListener("change", (event) => {
  const missed = event.target.value === "missed_issue";
  $("#feedback-missed-fields").classList.toggle("hidden", !missed);
  $("#feedback-hint").textContent = missed
    ? "补充规则和位置可让候选评测学习更精确的检查点。"
    : "提交后可在本任务和演进实验室查看状态。";
});

$("#feedback-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedTask || !selectedTaskData?.report) return;
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  const values = new FormData(form);
  const category = String(values.get("category"));
  const selectedIndex = values.get("finding_index");
  const findings = selectedTaskData.report.findings || [];
  const finding = selectedIndex === "" ? {} : { ...(findings[Number(selectedIndex)] || {}) };
  if (category === "missed_issue") {
    const ruleId = String(values.get("rule_id") || "").trim();
    const path = String(values.get("path") || "").trim();
    const line = Number(values.get("line"));
    if (ruleId) finding.rule_id = ruleId;
    if (path) finding.path = path;
    if (Number.isInteger(line) && line > 0) finding.line = line;
  }
  const output = $("#feedback-result");
  output.textContent = "正在保存反馈…";
  setButtonBusy(button, true, "正在提交…");
  try {
    const data = await api(`/v1/tasks/${encodeURIComponent(selectedTask)}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category,
        finding: Object.keys(finding).length ? finding : null,
        note: String(values.get("note") || "").trim(),
      }),
    });
    output.textContent = `${feedbackLabels[data.category] || data.category}已记录；可在演进实验室等待候选评测。`;
    form.reset();
    $("#feedback-missed-fields").classList.add("hidden");
    $("#feedback-hint").textContent = "提交后可在本任务和演进实验室查看状态。";
    await Promise.all([loadTaskFeedback(selectedTask), loadDashboard()]);
    toast("反馈已记录");
  } catch (error) {
    output.textContent = `提交失败：${error.message}`;
  } finally {
    setButtonBusy(button, false);
  }
});

$("#reload-skills").addEventListener("click", async () => {
  const button = $("#reload-skills");
  setButtonBusy(button, true, "正在扫描…");
  try {
    await api("/v1/skills/reload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    await loadSkills();
    toast("Skills 已重新加载");
  } catch (error) {
    toast(error.message);
  } finally {
    setButtonBusy(button, false);
  }
});

$("#evolution-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  const values = new FormData(form);
  setButtonBusy(button, true, "正在评测…");
  try {
    const data = await api("/v1/evolution/propose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skill_name: values.get("skill_name"), prompt: values.get("prompt") }),
    });
    $("#evolution-result").classList.remove("empty");
    $("#evolution-result").textContent = formatJson(data);
    toast("新旧版本回放评测已完成");
    loadFailures();
  } catch (error) {
    toast(error.message);
  } finally {
    setButtonBusy(button, false);
  }
});

$("#auto-evolve").addEventListener("click", async () => {
  const button = $("#auto-evolve");
  setButtonBusy(button, true, "正在生成…");
  try {
    const data = await api("/v1/evolution/auto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skill_name: "llm-review" }),
    });
    $("#evolution-result").classList.remove("empty");
    $("#evolution-result").textContent = formatJson(data);
    toast("反馈候选评测已完成");
    loadFailures();
  } catch (error) {
    toast(error.message);
  } finally {
    setButtonBusy(button, false);
  }
});

$("#refresh").addEventListener("click", async () => {
  const view = location.hash.slice(1) || "overview";
  if (view === "overview") await loadDashboard();
  else if (view === "tasks") await loadTasks();
  else if (view === "skills") await loadSkills();
  else if (view === "evolution") await loadFailures();
  else if (view === "bank") await loadBank();
  else await loadDashboard();
  toast("数据已刷新");
});

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  const values = new FormData(form);
  setButtonBusy(button, true, "正在登录…");
  try {
    const data = await api("/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: values.get("username"),
        password: values.get("password"),
        tenant_id: values.get("tenant_id"),
      }),
    });
    accessToken = data.access_token;
    localStorage.setItem("evoagent_token", accessToken);
    $("#login-overlay").classList.add("hidden");
    $("#logout").classList.remove("hidden");
    $("#login-error").textContent = "";
    await loadDashboard();
  } catch (error) {
    $("#login-error").textContent = error.message;
  } finally {
    setButtonBusy(button, false);
  }
});

$("#show-register").addEventListener("click", () => {
  $("#login-form").classList.add("hidden");
  $("#register-form").classList.remove("hidden");
  $("#login-error").textContent = "";
  $("#register-error").textContent = "";
});

$("#show-login").addEventListener("click", () => {
  $("#register-form").classList.add("hidden");
  $("#login-form").classList.remove("hidden");
  $("#login-error").textContent = "";
  $("#register-error").textContent = "";
});

$("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  const values = new FormData(form);
  const username = String(values.get("username") || "").trim();
  const password = String(values.get("password") || "");
  const confirm = String(values.get("confirm") || "");
  const tenantId = String(values.get("tenant_id") || "").trim();
  const errorEl = $("#register-error");
  if (!username) {
    errorEl.textContent = "请输入用户名";
    return;
  }
  if (password.length < 10) {
    errorEl.textContent = "密码至少 10 个字符";
    return;
  }
  if (password !== confirm) {
    errorEl.textContent = "两次输入的密码不一致";
    return;
  }
  setButtonBusy(button, true, "正在创建…");
  try {
    const data = await api("/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, tenant_id: tenantId }),
    });
    accessToken = data.access_token;
    localStorage.setItem("evoagent_token", accessToken);
    $("#login-overlay").classList.add("hidden");
    $("#logout").classList.remove("hidden");
    $("#register-form").classList.add("hidden");
    toast("账号已创建并登录");
    await loadDashboard();
  } catch (error) {
    errorEl.textContent = error.message;
  } finally {
    setButtonBusy(button, false);
  }
});

$("#logout").addEventListener("click", () => {
  accessToken = "";
  localStorage.removeItem("evoagent_token");
  $("#login-overlay").classList.remove("hidden");
  $("#logout").classList.add("hidden");
});

const diffInput = $('textarea[name="diff"]', $("#review-form"));
const diffStats = $("#diff-stats");
function updateDiffStats() {
  const value = diffInput.value;
  const lines = value ? value.split(/\r?\n/).length : 0;
  diffStats.textContent = `${lines} 行，${value.length} 字符`;
}
diffInput.addEventListener("input", updateDiffStats);
updateDiffStats();

const backtestFileInput = $("#strategy-file");
const backtestTextarea = $('textarea[name="strategy_code"]', $("#backtest-form"));
const backtestStats = $("#strategy-stats");

function updateStrategyStats() {
  const value = backtestTextarea.value;
  const lines = value ? value.split(/\r?\n/).length : 0;
  backtestStats.textContent = `${lines} 行，${value.length} 字符`;
}
if (backtestTextarea) {
  backtestTextarea.addEventListener("input", updateStrategyStats);
  updateStrategyStats();
}
if (backtestFileInput) {
  backtestFileInput.addEventListener("change", async () => {
    const file = backtestFileInput.files && backtestFileInput.files[0];
    if (!file) return;
    try {
      backtestTextarea.value = await file.text();
      updateStrategyStats();
      toast("已载入策略文件");
    } catch (error) {
      toast(error.message);
    }
  });
}

$("#backtest-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  const values = new FormData(form);
  const strategyCode = String(values.get("strategy_code") || "").trim();
  if (!strategyCode) {
    toast("请粘贴或上传策略代码");
    return;
  }
  const params = {
    symbol: String(values.get("symbol") || "").trim(),
    start_date: String(values.get("start_date") || "").trim(),
    end_date: String(values.get("end_date") || "").trim(),
    adjust: String(values.get("adjust") || "qfq"),
    initial_capital: Number(values.get("initial_capital") || 10000),
    commission: Number(values.get("commission") || 0.0003),
  };
  const body = { strategy_code: strategyCode, params, repository: "backtest/upload" };
  const output = $("#backtest-result");
  output.classList.remove("empty");
  output.textContent = "正在运行回测（行情下载 + 沙箱回放 + 代码审查）…";
  $("#backtest-report-panel").classList.add("hidden");
  setButtonBusy(button, true, "正在回测…");
  try {
    const data = await api("/v1/backtests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    output.textContent = `回测完成（task_id: ${data.task_id}；状态：${data.state}）`;
    renderBacktestResult(data.report);
    toast("回测已完成");
  } catch (error) {
    output.textContent = `回测失败：${error.message}`;
  } finally {
    setButtonBusy(button, false);
  }
});

function renderBacktestResult(report) {
  const backtest = (report && report.backtest) || {};
  const metrics = backtest.metrics || {};
  const panel = $("#backtest-report-panel");
  if (panel) panel.classList.remove("hidden");
  const metricsRoot = $("#backtest-metrics");
  if (metricsRoot) {
    metricsRoot.innerHTML = [
      statCard("初始资金", formatNumber(metrics.initial_capital), "权益起点", "", "CAP"),
      statCard("最终权益", formatNumber(metrics.final_equity), "回测结束", "success", "EQ"),
      statCard("总收益", `${Number(metrics.total_return || 0).toFixed(2)}%`, "累计收益率", Number(metrics.total_return) >= 0 ? "success" : "failed", "RET"),
      statCard("年化收益", `${Number(metrics.annualized_return || 0).toFixed(2)}%`, "年化收益", "rate", "AR"),
      statCard("Sharpe", Number(metrics.sharpe || 0).toFixed(2), "风险调整收益", "rate", "SH"),
      statCard("最大回撤", `${Number(metrics.max_drawdown || 0).toFixed(2)}%`, "峰谷回撤", "failed", "DD"),
      statCard("胜率", `${Number(metrics.win_rate || 0).toFixed(2)}%`, "盈利交易占比", "rate", "WR"),
      statCard("交易次数", metrics.num_trades ?? 0, "总成交笔数", "skills", "TR"),
    ].join("");
  }
  renderBacktestChart(backtest.equity_curve || []);
  renderBacktestFindings((report && report.findings) || []);
}

function formatNumber(value) {
  if (value === undefined || value === null || value === "") return "—";
  return Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 2 });
}

function renderBacktestChart(equityCurve) {
  const svg = document.getElementById("backtest-chart");
  if (!svg) return;
  if (!equityCurve || equityCurve.length < 2) { svg.innerHTML = ""; return; }
  const W = 600, H = 200, pad = 12;
  const equities = equityCurve.map((p) => Number(p.equity));
  const min = Math.min(...equities), max = Math.max(...equities);
  const range = (max - min) || 1;
  const stepX = (W - pad * 2) / (equities.length - 1);
  const points = equities.map((e, i) => [pad + i * stepX, H - pad - ((e - min) / range) * (H - pad * 2)]);
  const line = points.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
  const area = `M${points[0][0].toFixed(1)} ${(H - pad).toFixed(1)} ` +
    points.map((p) => `L${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ") +
    ` L${points[points.length - 1][0].toFixed(1)} ${(H - pad).toFixed(1)} Z`;
  svg.innerHTML = `<path d="${area}" fill="rgba(79,157,255,0.12)" stroke="none"/><path d="${line}" fill="none" stroke="#4f9dff" stroke-width="2"/>`;
}

function renderBacktestFindings(findings) {
  const root = $("#backtest-findings");
  if (!root) return;
  if (!findings || !findings.length) {
    root.innerHTML = '<p class="feedback-empty">代码审查未发现问题。</p>';
    return;
  }
  root.innerHTML = findings.map((f) => `
    <div class="finding-row">
      <span class="finding-sev sev-${escapeHtml((f.severity || "low").toLowerCase())}">${escapeHtml(f.severity || "LOW")}</span>
      <span class="finding-copy"><b>${escapeHtml(f.rule_id || "未命名规则")}</b> ${escapeHtml(f.title || "")}
        <small>${escapeHtml(f.path || "")}${f.line ? " : " + escapeHtml(String(f.line)) : ""}</small>
        ${f.explanation ? `<span class="finding-exp">${escapeHtml(f.explanation)}</span>` : ""}
      </span>
    </div>`).join("");
}

async function loadBank() {
  const statsRoot = $("#bank-stats");
  const listRoot = $("#bank-list");
  const rulesRoot = $("#bank-rules");
  if (statsRoot) statsRoot.innerHTML = '<div class="stat loading"></div><div class="stat loading"></div><div class="stat loading"></div>';
  if (listRoot) listRoot.innerHTML = '<div class="list-loading"></div>';
  if (rulesRoot) rulesRoot.innerHTML = "";
  try {
    const data = await api("/v1/findings-bank?limit=500");
    const stats = data.stats || {};
    if (statsRoot) {
      statsRoot.innerHTML = [
        statCard("问题总数", stats.total ?? 0, "沉淀到记忆库", "", "ALL"),
        statCard("已扫描策略", stats.strategies_scanned ?? 0, "去重计数", "skills", "SK"),
        statCard("高危", stats.by_severity?.high ?? 0, "high 级别", "failed", "ERR"),
        statCard("中危", stats.by_severity?.medium ?? 0, "medium 级别", "rate", "RATE"),
        statCard("低危", stats.by_severity?.low ?? 0, "low 级别", "feedback", "LOW"),
      ].join("");
    }
    if (rulesRoot) {
      const rules = stats.by_rule || [];
      rulesRoot.innerHTML = rules.length
        ? rules.map((r) => `
          <div class="finding-row">
            <span class="finding-sev sev-low">×${escapeHtml(String(r.count))}</span>
            <span class="finding-copy"><b>${escapeHtml(r.rule_id || "未命名规则")}</b><small>累计出现次数</small></span>
          </div>`).join("")
        : '<p class="feedback-empty">暂无规则分布数据。</p>';
    }
    const findings = data.findings || [];
    if (!listRoot) return;
    if (!findings.length) {
      listRoot.innerHTML = '<p class="feedback-empty">还没有沉淀任何问题。跑一次回测或审查后，这里会自动记录。</p>';
      return;
    }
    // 问题归类去重叠：先按类别(category)分组，类别内按 rule_id 聚合，避免零散刷屏
    const catOrder = ["未来函数", "数据泄露", "交易安全", "执行成本", "过拟合", "数据质量", "代码质量", "未分类"];
    const catMap = {};
    for (const f of findings) {
      const cat = f.category || "未分类";
      (catMap[cat] = catMap[cat] || []).push(f);
    }
    const cats = Object.keys(catMap).sort((a, b) => {
      const ia = catOrder.indexOf(a), ib = catOrder.indexOf(b);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    listRoot.innerHTML = cats.map((cat) => {
      const catItems = catMap[cat];
      const catSeverity = Math.max(...catItems.map((f) => ({ critical: 4, high: 3, medium: 2, low: 1 }[f.severity] || 0)));
      const sevLabel = { 4: "critical", 3: "high", 2: "medium", 1: "low" }[catSeverity] || "low";
      const groups = {};
      for (const f of catItems) {
        const key = f.rule_id || "未命名规则";
        (groups[key] = groups[key] || []).push(f);
      }
      const groupHtml = Object.keys(groups)
        .sort((a, b) => groups[b].length - groups[a].length)
        .map((ruleId) => {
          const items = groups[ruleId];
          const rep = items[0];
          const occHtml = items.map((f) => `
            <li class="occ">
              <span class="occ-loc">${escapeHtml(f.repository || "")}${f.path ? " · " + escapeHtml(f.path) : ""}${f.line ? ":" + escapeHtml(String(f.line)) : ""}</span>
              ${f.explanation ? `<span class="occ-exp">${escapeHtml(f.explanation)}</span>` : ""}
            </li>`).join("");
          return `
            <div class="finding-group">
              <div class="finding-group-head">
                <span class="finding-copy"><b>${escapeHtml(ruleId)}</b> ${escapeHtml(rep.title || "")}</span>
                <span class="group-count">×${escapeHtml(String(items.length))}</span>
              </div>
              <ul class="occ-list">${occHtml}</ul>
            </div>`;
        }).join("");
      return `
        <div class="finding-category">
          <div class="finding-category-head">
            <span class="finding-sev sev-${escapeHtml(sevLabel)}">${escapeHtml(cat)}</span>
            <span class="finding-copy"><b>${escapeHtml(cat)}</b><small>${escapeHtml(String(catItems.length))} 条问题</small></span>
          </div>
          ${groupHtml}
        </div>`;
    }).join("");
  } catch (error) {
    if (listRoot) listRoot.innerHTML = '<p class="feedback-empty">记忆库加载失败</p>';
    toast(error.message);
  }
}

if (accessToken) $("#logout").classList.remove("hidden");
show(location.hash.slice(1) || "overview", false);
loadDashboard();
