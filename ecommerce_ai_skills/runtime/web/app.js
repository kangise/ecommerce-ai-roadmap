"use strict";

const state = {
  apiKey: "",
  me: null,
  catalog: null,
  briefing: null,
  imports: [],
  runs: [],
  jobs: [],
  schedules: [],
  mission: null,
  audit: [],
  connectors: [],
  selectedPlatform: "amazon",
  chartMetric: null,
  timer: null,
  noticeTimer: null,
};

const $ = id => document.getElementById(id);
const busyContent = new WeakMap();
const icon = name => `<img src="/app/assets/icons/${name}.svg" alt="">`;
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, character => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
}[character]));
const isoLocal = value => value ? new Date(value).toLocaleString("zh-CN", {hour12: false}) : "—";
const shortDate = value => value ? new Date(value).toLocaleDateString("zh-CN", {month: "numeric", day: "numeric"}) : "—";
const idempotency = prefix => `${prefix}:${crypto.randomUUID()}`;

function notice(message, type = "info") {
  const target = $("notice");
  if (state.noticeTimer) clearTimeout(state.noticeTimer);
  target.textContent = message;
  target.className = `notice show ${type}`;
  if (type !== "error") state.noticeTimer = setTimeout(clearNotice, 3200);
}

function clearNotice() {
  if (state.noticeTimer) clearTimeout(state.noticeTimer);
  state.noticeTimer = null;
  $("notice").className = "notice";
}

function busy(button, value) {
  if (!button) return;
  if (value) {
    busyContent.set(button, button.innerHTML);
    button.disabled = true;
    button.textContent = "处理中…";
  } else {
    button.innerHTML = busyContent.get(button) || button.innerHTML;
    button.disabled = false;
    busyContent.delete(button);
  }
}

async function api(path, options = {}) {
  if (!state.apiKey) throw new Error("请先连接 Runtime");
  const headers = {Authorization: `Bearer ${state.apiKey}`, ...(options.headers || {})};
  if (options.json !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.json);
  }
  const response = await fetch(path, {...options, headers});
  let payload = {};
  try { payload = await response.json(); } catch { payload = {}; }
  if (!response.ok) throw new Error(payload.error?.message || `请求失败 (${response.status})`);
  return payload;
}

function setConnected(connected) {
  const demo = connected && state.me?.tenant_mode === "demo";
  $("connection-dot").classList.toggle("connected", connected);
  $("refresh-btn").disabled = !connected;
  $("disconnect-btn").disabled = !connected;
  $("connect-btn").disabled = connected;
  $("connection-btn").classList.toggle("connected", connected);
  $("demo-badge").hidden = !demo;
  $("demo-banner").hidden = !demo;
  $("connection-btn").querySelector("span").textContent = connected ? "Runtime 已连接" : "连接 Runtime";
  $("account-role").textContent = connected ? `${state.me?.role || "viewer"} · 已连接` : "未连接";
  $("account-name").textContent = connected ? (state.me?.tenant_name || state.me?.email || "Local Runtime") : "Local Runtime";
}

function platformName(platform = state.selectedPlatform) {
  const entry = (state.catalog?.platforms || []).find(item => item.id === platform);
  const defaults = {amazon: "Amazon", shopify: "Shopify", walmart: "Walmart", tiktok_shop: "TikTok Shop"};
  return defaults[platform] || entry?.label?.zh || entry?.label?.en || platform;
}

function updatePlatformChrome() {
  document.querySelectorAll(".platform-tab").forEach(button => {
    const active = button.dataset.platform === state.selectedPlatform;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
  $("briefing-platform-name").textContent = platformName();
}

function navigate(view) {
  document.querySelectorAll("[data-view-panel]").forEach(panel => panel.classList.toggle("active", panel.dataset.viewPanel === view));
  document.querySelectorAll(".nav-item").forEach(button => {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  window.scrollTo({top: 0, behavior: "smooth"});
}

function designedEmpty(target, title, copy, iconName = "database", action = null) {
  target.innerHTML = `<div class="designed-empty compact">${icon(iconName)}<strong>${escapeHtml(title)}</strong><span>${escapeHtml(copy)}</span>${action ? `<button data-action="navigate" data-view="${action.view}" class="text-button">${escapeHtml(action.label)}</button>` : ""}</div>`;
}

function badge(status) {
  return `<span class="badge ${escapeHtml(status)}">${escapeHtml(status)}</span>`;
}

function connectorCanManage() {
  return ["admin", "owner"].includes(state.me?.role);
}

function connectorCanCheck() {
  return ["operator", "admin", "owner"].includes(state.me?.role);
}

function connectorProviderLabel(provider) {
  const entry = (state.catalog?.connector_providers || []).find(item => item.id === provider || item.provider === provider);
  return entry?.label?.zh || entry?.label?.en || entry?.label || entry?.name || (provider === "amazon_spapi" ? "Amazon" : provider === "shopify" ? "Shopify" : provider);
}

function connectorDetails(connector) {
  const details = connector.provider_details || {};
  if (connector.provider === "amazon_spapi") {
    const marketplaces = details.marketplaces || details.marketplace_ids || [];
    const catalog = new Map((state.catalog?.amazon_marketplaces || []).map(item => [item.id, item.name || item.label || item.id]));
    return [details.region, marketplaces.map(item => catalog.get(typeof item === "string" ? item : item.id) || (typeof item === "string" ? item : item.id)).join("、")].filter(Boolean).join(" · ") || "未配置 region 或 marketplace";
  }
  if (connector.provider === "shopify") return details.shop_domain || "未配置 Shopify domain";
  return connector.external_account_id;
}

function renderConnectors() {
  const target = $("connector-list"), note = $("connector-permission"), add = $("add-connector-btn");
  if (!state.apiKey) {
    add.disabled = true;
    add.title = "请先连接 Runtime";
    note.hidden = false; note.textContent = "连接 Runtime 后才能查看或管理租户账户。";
    designedEmpty(target, "尚未连接 Runtime", "账户列表需要已认证的租户会话。", "key");
    return;
  }
  const manage = connectorCanManage(), check = connectorCanCheck();
  add.disabled = !manage;
  add.title = manage ? "" : "需要 admin 或 owner 角色";
  note.hidden = manage;
  note.textContent = manage ? "" : "当前角色只能查看账户。添加或编辑配置需要 admin 或 owner 角色。";
  if (!state.connectors.length) {
    designedEmpty(target, "还没有连接账户", manage ? "添加 Amazon 或 Shopify 账户，并使用环境变量引用授权凭据。" : "当前租户尚未连接账户；需要 admin 或 owner 添加。", "key");
    return;
  }
  target.innerHTML = state.connectors.map(connector => {
    const healthStatus = connector.health_status || "unchecked";
    const edit = manage ? `<button data-action="edit-connector" data-id="${escapeHtml(connector.id)}" class="secondary-button">编辑</button>` : "";
    const healthAction = check ? `<button data-action="health-check-connector" data-id="${escapeHtml(connector.id)}" class="primary-button">健康检查</button>` : `<span class="permission-reason">需要 operator、admin 或 owner 执行健康检查</span>`;
    const failure = connector.health_error_message || connector.health_error_code;
    const refCount = Object.keys(connector.credential_refs || {}).length;
    return `<article class="connector-card"><div class="connector-card-head"><div><p class="kicker">${escapeHtml(connectorProviderLabel(connector.provider))}</p><h2>${escapeHtml(connector.external_account_id)}</h2><p>${escapeHtml(connectorDetails(connector))}</p></div>${badge(healthStatus)}</div><dl class="connector-meta"><div><dt>Last checked</dt><dd>${escapeHtml(isoLocal(connector.health_checked_at))}</dd></div><div><dt>Credential refs</dt><dd>${refCount ? `${refCount} present` : "—"}</dd></div></dl>${failure ? `<p class="connector-error">${escapeHtml(failure)}</p>` : ""}<div class="row-actions">${edit}${healthAction}</div></article>`;
  }).join("");
}

function connectorProviders() {
  return state.catalog?.connector_providers || [{id: "amazon_spapi", name: "Amazon Selling Partner API"}, {id: "shopify", name: "Shopify Admin API"}];
}

function renderConnectorForm(provider = $("connector-provider").value || "amazon_spapi", connector = null) {
  const providerSelect = $("connector-provider");
  providerSelect.innerHTML = connectorProviders().map(item => `<option value="${escapeHtml(item.id || item.provider)}">${escapeHtml(item.label?.zh || item.label?.en || item.label || item.name || item.id || item.provider)}</option>`).join("");
  providerSelect.value = provider;
  const amazon = provider === "amazon_spapi";
  $("amazon-connector-fields").hidden = !amazon;
  $("shopify-connector-fields").hidden = amazon;
  if (!amazon) return;
  const details = connector?.provider_details || {};
  const regions = [...new Set((state.catalog?.amazon_marketplaces || []).map(item => item.region).filter(Boolean))];
  $("connector-region").innerHTML = regions.map(region => `<option value="${escapeHtml(region)}">${escapeHtml(region)}</option>`).join("");
  $("connector-region").value = details.region || regions[0] || "";
  renderConnectorMarketplaces(details.marketplace_ids || []);
}

function renderConnectorMarketplaces(selected = []) {
  const region = $("connector-region").value;
  const selectedIds = new Set(selected.map(item => typeof item === "string" ? item : item.id));
  const markets = (state.catalog?.amazon_marketplaces || []).filter(item => !region || item.region === region);
  $("connector-marketplaces").innerHTML = markets.length ? markets.map(item => `<label><input type="checkbox" name="connector-marketplace" value="${escapeHtml(item.id)}" ${selectedIds.has(item.id) ? "checked" : ""}>${escapeHtml(item.name || item.label || item.id)}</label>`).join("") : "<span class=\"permission-reason\">Catalog 中没有此 region 的 marketplace。</span>";
}

function openConnectorForm(connector = null) {
  if (!connectorCanManage()) { notice("需要 admin 或 owner 角色", "error"); return; }
  $("connector-form").reset();
  $("connector-id").value = connector?.id || "";
  $("connector-dialog-title").textContent = connector ? "编辑账户" : "添加账户";
  $("connector-external-account-id").value = connector?.external_account_id || "";
  const details = connector?.provider_details || {};
  $("amazon-lwa-client-id-ref").value = "";
  $("amazon-lwa-client-secret-ref").value = "";
  $("amazon-refresh-token-ref").value = "";
  $("shopify-domain").value = details.shop_domain || "";
  $("shopify-api-version").value = details.api_version || "";
  $("shopify-access-token-ref").value = "";
  renderConnectorForm(connector?.provider || "amazon_spapi", connector);
  $("connector-provider").disabled = Boolean(connector);
  $("connector-dialog").showModal();
}

function renderCatalog() {
  const platforms = state.catalog?.platforms || [];
  const reports = state.catalog?.report_types || [];
  for (const id of ["evidence-platform", "schedule-platform"]) {
    $(id).innerHTML = platforms.map(platform => `<option value="${escapeHtml(platform.id)}">${escapeHtml(platform.label?.zh || platform.label?.en || platform.id)}</option>`).join("");
  }
  renderReportOptions("evidence-platform", "evidence-type", reports);
  renderReportOptions("schedule-platform", "schedule-report-type", reports);
  updatePlatformChrome();
}

function renderReportOptions(platformId, reportId, reports = state.catalog?.report_types || []) {
  const platform = $(platformId).value || "amazon";
  const compatible = reports.filter(type => type === "platform_generic" || platform === "amazon" && type.startsWith("amazon_"));
  $(reportId).innerHTML = compatible.map(type => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`).join("");
}

function formatMetric(metric, compact = false) {
  const options = metric.format === "integer"
    ? {maximumFractionDigits: 0, notation: compact ? "compact" : "standard"}
    : {maximumFractionDigits: metric.format === "percent" ? 2 : 2, notation: compact ? "compact" : "standard"};
  const value = new Intl.NumberFormat("zh-CN", options).format(metric.value);
  return metric.format === "percent" ? `${value}%` : value;
}

function metricChange(metric) {
  if (metric.change_percent === null || metric.change_percent === undefined) return {label: "首次观测", className: ""};
  const change = Number(metric.change_percent);
  const label = `${change > 0 ? "+" : ""}${change.toFixed(1)}%`;
  if (metric.trend_mode === "context_only" || change === 0) return {label, className: ""};
  const favorable = metric.trend_mode === "higher_is_better" ? change > 0 : change < 0;
  return {label, className: favorable ? "positive" : "negative"};
}

function renderMetrics() {
  const target = $("metric-summary");
  const metrics = state.briefing?.metrics || [];
  if (!metrics.length) {
    target.innerHTML = "";
    return;
  }
  target.innerHTML = metrics.slice(0, 4).map(metric => {
    const change = metricChange(metric);
    const unitNote = metric.format === "amount" ? "原报表币种" : `观测于 ${shortDate(metric.observed_at)}`;
    return `<article class="metric-item"><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(formatMetric(metric))}</strong><small class="${change.className}">${escapeHtml(change.label)} · ${escapeHtml(unitNote)}</small></article>`;
  }).join("");
}

function renderChartControls() {
  const metrics = state.briefing?.metrics || [];
  if (!metrics.length) {
    $("chart-controls").innerHTML = "";
    $("trend-chart").classList.remove("visible");
    $("chart-empty").hidden = false;
    return;
  }
  if (!metrics.some(metric => metric.key === state.chartMetric)) state.chartMetric = metrics[0].key;
  $("chart-controls").innerHTML = metrics.map(metric => `<button data-action="select-metric" data-metric="${escapeHtml(metric.key)}" class="metric-toggle ${metric.key === state.chartMetric ? "active" : ""}">${escapeHtml(metric.label)}</button>`).join("");
  drawChart(metrics.find(metric => metric.key === state.chartMetric));
}

function drawChart(metric) {
  const canvas = $("trend-chart");
  const empty = $("chart-empty");
  const points = metric?.series || [];
  if (!points.length) {
    canvas.classList.remove("visible");
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  canvas.classList.add("visible");
  const width = Math.max(canvas.clientWidth, 320);
  const height = 250;
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const context = canvas.getContext("2d");
  if (!context) return;
  context.scale(ratio, ratio);
  context.clearRect(0, 0, width, height);
  const padding = {left: 54, right: 18, top: 15, bottom: 34};
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const values = points.map(point => Number(point.value));
  let minimum = Math.min(...values);
  let maximum = Math.max(...values);
  if (minimum === maximum) {
    const delta = Math.abs(minimum) * .12 || 1;
    minimum -= delta;
    maximum += delta;
  }
  context.font = '12px Inter, "PingFang SC", sans-serif';
  context.textBaseline = "middle";
  context.lineWidth = 1;
  for (let index = 0; index < 5; index += 1) {
    const y = padding.top + plotHeight * index / 4;
    context.strokeStyle = "#e4e1d9";
    context.beginPath(); context.moveTo(padding.left, y); context.lineTo(width - padding.right, y); context.stroke();
    const value = maximum - (maximum - minimum) * index / 4;
    context.fillStyle = "#8b93a3";
    context.textAlign = "right";
    context.fillText(new Intl.NumberFormat("zh-CN", {notation: "compact", maximumFractionDigits: 1}).format(value), padding.left - 9, y);
  }
  const xAt = index => points.length === 1 ? padding.left + plotWidth / 2 : padding.left + plotWidth * index / (points.length - 1);
  const yAt = value => padding.top + (maximum - value) / (maximum - minimum) * plotHeight;
  context.strokeStyle = "#175ce6";
  context.lineWidth = 2.4;
  context.lineJoin = "round";
  context.lineCap = "round";
  context.beginPath();
  points.forEach((point, index) => {
    const x = xAt(index), y = yAt(Number(point.value));
    if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
  });
  context.stroke();
  points.forEach((point, index) => {
    const x = xAt(index), y = yAt(Number(point.value));
    context.fillStyle = "#fffefa"; context.strokeStyle = "#175ce6"; context.lineWidth = 2.4;
    context.beginPath(); context.arc(x, y, 4.5, 0, Math.PI * 2); context.fill(); context.stroke();
    context.fillStyle = "#657086"; context.textAlign = "center"; context.textBaseline = "top";
    context.fillText(shortDate(point.observed_at), x, height - padding.bottom + 12);
  });
  const tableBody = $("chart-table").querySelector("tbody");
  tableBody.innerHTML = points.map(point => `<tr><td>${escapeHtml(isoLocal(point.observed_at))}</td><td>${escapeHtml(point.value)}</td></tr>`).join("");
}

function renderPriorities() {
  const target = $("priority-list");
  const priorities = state.briefing?.priorities || [];
  if (!priorities.length) {
    designedEmpty(target, "还没有 Agent Brief", "选择 Evidence 完成一次 Weekly Ops 后，这里会显示有证据引用的真实优先事项。", "robot", {view: "agents", label: "开始周度复盘"});
    return;
  }
  target.innerHTML = priorities.map((priority, index) => `<article class="priority-row">
    <span class="priority-rank">${escapeHtml(priority.rank || index + 1)}</span>
    <div class="priority-copy"><strong>${escapeHtml(priority.title)}</strong><p>${escapeHtml(priority.why_now)}</p><div class="priority-meta"><span class="meta-chip">影响：${escapeHtml(priority.expected_impact)}</span><span class="meta-chip">Owner：${escapeHtml(agentDisplayName(priority.recommended_owner))}</span><span class="meta-chip">证据 ${priority.evidence_refs?.length || 0} 条</span></div></div>
    <div class="priority-actions"><button data-action="view-priority" data-index="${index}" class="secondary-button">查看证据</button><span class="confidence ${escapeHtml(priority.confidence)}">${escapeHtml(priority.confidence)} confidence</span></div>
  </article>`).join("");
}

function operationLabel(operation) {
  const labels = {
    "amazon_spapi.import_report": "导入 Amazon SP-API 报表",
    "shopify.sync_products": "同步 Shopify 商品",
    "shopify.update_product": "更新 Shopify 商品",
    "shopify.update_inventory": "更新 Shopify 库存",
  };
  return labels[operation] || operation;
}

function actionContext(action) {
  const payload = action.payload || {};
  const pieces = [payload.evidence_report_type, payload.report_type, payload.report_id, payload.external_account_id, payload.marketplace_id].filter(Boolean);
  return pieces.length ? pieces.join(" · ") : `请求于 ${isoLocal(action.created_at)}`;
}

function canApprove() {
  return ["owner", "admin"].includes(state.me?.role);
}

function approvalCard(action, compact = false) {
  const approveAllowed = canApprove();
  return `<article class="${compact ? "decision-card" : "data-row"}">
    <div class="${compact ? "" : "data-main"}"><strong>${escapeHtml(operationLabel(action.operation))}</strong><p>${escapeHtml(actionContext(action))}</p>${compact ? "" : `<small>${badge(action.status)}${escapeHtml(isoLocal(action.created_at))}</small>`}</div>
    <div class="${compact ? "card-actions" : "row-actions"}"><button data-action="view-action" data-id="${action.id}" class="secondary-button">查看</button><button data-action="approve-action" data-id="${action.id}" class="primary-button" ${approveAllowed ? "" : 'disabled title="需要 admin 或 owner 角色"'}>批准</button></div>
    ${approveAllowed ? "" : '<span class="permission-reason">当前角色只能查看；批准需要 admin 或 owner。</span>'}
  </article>`;
}

function renderBriefingApprovals() {
  const items = state.briefing?.approvals || [];
  $("approval-count").textContent = items.length;
  $("approval-nav-count").textContent = items.length;
  $("approval-nav-count").hidden = items.length === 0;
  const target = $("briefing-approvals");
  if (!items.length) {
    designedEmpty(target, "当前没有待审批动作", "Agent 的外部写入建议会在这里等待另一位授权用户。", "shield-check");
    return;
  }
  target.innerHTML = items.slice(0, 3).map(item => approvalCard(item, true)).join("");
}

function agentIcon(name) {
  const normalized = name.toLowerCase();
  if (normalized.includes("ads") || normalized.includes("promotion")) return "megaphone";
  if (normalized.includes("inventory")) return "package";
  if (normalized.includes("pricing")) return "tag";
  if (normalized.includes("listing")) return "file-text";
  if (normalized.includes("research") || normalized.includes("evidence")) return "magnifying-glass";
  if (normalized.includes("review") || normalized.includes("compliance")) return "shield-check";
  if (normalized.includes("controller") || normalized.includes("manager")) return "users-three";
  return "robot";
}

function agentDisplayName(name) {
  const labels = {
    evidence_analyst: "Evidence Analyst",
    platform_amazon_operator: "Amazon Agent",
    platform_shopify_operator: "Shopify Agent",
    platform_walmart_operator: "Walmart Agent",
    platform_tiktok_shop_operator: "TikTok Shop Agent",
    cross_platform_controller: "Cross-platform Controller",
    store_manager: "Store Manager",
  };
  return labels[name] || String(name || "Agent").replaceAll("_", " ");
}

function renderAgentRoster() {
  const target = $("agent-roster");
  const agents = state.briefing?.agents || [];
  if (!agents.length) {
    designedEmpty(target, "暂无 Agent 活动", "运行 Weekly Ops 后显示各 Agent 的真实任务状态。", "robot", {view: "agents", label: "查看 Agent Runs"});
    return;
  }
  target.innerHTML = agents.slice(0, 7).map(agent => `<div class="agent-person"><span class="agent-icon">${icon(agentIcon(agent.name))}</span><span><strong>${escapeHtml(agentDisplayName(agent.name))}</strong><small>${escapeHtml(isoLocal(agent.updated_at))}</small></span><span class="status-label ${escapeHtml(agent.status)}">${escapeHtml(agent.status)}</span></div>`).join("");
}

function renderBriefing() {
  updatePlatformChrome();
  renderMetrics();
  renderChartControls();
  renderPriorities();
  renderBriefingApprovals();
  renderAgentRoster();
  const evidence = state.briefing?.evidence;
  $("evidence-range").textContent = evidence ? `${evidence.source_count} 个来源 · ${evidence.row_count} 行真实数据` : "尚未连接";
  $("evidence-freshness").textContent = evidence?.latest_observed_at ? `最新观测 ${isoLocal(evidence.latest_observed_at)}` : "等待 Evidence";
  $("briefing-summary").textContent = state.briefing?.executive_summary || (evidence?.source_count ? "Evidence 已连接；完成一次 Weekly Ops 后生成有证据引用的经营结论。" : "还没有该平台的真实 Evidence；导入数据后再生成经营简报。");
}

function renderEvidence() {
  const target = $("evidence-list"), options = $("run-evidence-options");
  if (!state.imports.length) {
    designedEmpty(target, "尚无 Evidence", "上传经过验证的 CSV、TSV 或 XLSX 后显示在这里。", "database");
    designedEmpty(options, "暂无可选 Evidence", "先完成一次真实数据导入。", "database", {view: "evidence", label: "去导入"});
    return;
  }
  target.innerHTML = state.imports.map(item => `<div class="data-row"><div class="data-main"><strong>${escapeHtml(item.filename)}</strong><small>${badge(item.platform)}${escapeHtml(item.report_type)} · ${item.row_count} rows · ${escapeHtml(isoLocal(item.observed_at))}</small></div><div class="row-actions"><button data-action="view-import" data-id="${item.id}" class="secondary-button">查看</button></div></div>`).join("");
  options.innerHTML = state.imports.map(item => `<label><input type="checkbox" name="run-evidence" value="${item.id}">${escapeHtml(item.platform)} · ${escapeHtml(item.filename)}</label>`).join("");
}

function renderRuns() {
  const target = $("run-list");
  if (!state.runs.length) {
    designedEmpty(target, "尚无 Agent Run", "选择 Evidence 创建第一次 Weekly Ops。", "robot");
    return;
  }
  target.innerHTML = state.runs.map(run => {
    const actions = [`<button data-action="view-run" data-id="${run.id}" class="secondary-button">详情</button>`];
    if (["requested", "failed"].includes(run.status)) {
      actions.push(`<button data-action="execute-run" data-id="${run.id}" class="primary-button">执行</button>`);
      actions.push(`<button data-action="queue-run" data-id="${run.id}" class="secondary-button">加入队列</button>`);
    }
    if (run.status === "completed") actions.push(`<button data-action="evaluate-run" data-id="${run.id}" class="secondary-button">评测</button>`);
    return `<div class="data-row"><div class="data-main"><strong>${escapeHtml(run.objective)}</strong><small>${badge(run.status)}${escapeHtml((run.platforms || []).join(", "))} · ${escapeHtml(isoLocal(run.updated_at))}</small></div><div class="row-actions">${actions.join("")}</div></div>`;
  }).join("");
}

function renderJobs() {
  const target = $("job-list");
  if (!state.jobs.length) {
    designedEmpty(target, "暂无后台任务", "排队执行 Agent Run 后显示 Worker 状态。", "pulse");
    return;
  }
  target.innerHTML = state.jobs.map(job => `<div class="data-row"><div class="data-main"><strong>${escapeHtml(job.kind)}</strong><small>${badge(job.status)}attempt ${job.attempt_count}/${job.max_attempts} · ${escapeHtml(isoLocal(job.updated_at))}</small></div><div class="row-actions"><button data-action="view-job" data-id="${job.id}" class="secondary-button">查看</button></div></div>`).join("");
}

function renderSchedules() {
  const target = $("schedule-list");
  if (!state.schedules.length) {
    designedEmpty(target, "暂无 Schedule", "创建后由 Scheduler 使用最新匹配 Evidence 触发周度复盘。", "calendar-dots");
    return;
  }
  target.innerHTML = state.schedules.map(item => `<div class="data-row"><div class="data-main"><strong>${escapeHtml(item.name)}</strong><small>${badge(item.enabled ? "enabled" : "disabled")}${item.interval_minutes} min · next ${escapeHtml(isoLocal(item.next_run_at))}</small></div><div class="row-actions"><button data-action="toggle-schedule" data-id="${item.id}" data-enabled="${!item.enabled}" class="secondary-button">${item.enabled ? "停用" : "启用"}</button></div></div>`).join("");
}

function renderApprovals() {
  const target = $("approval-list"), items = state.mission?.approval_inbox || [];
  if (!items.length) {
    designedEmpty(target, "当前没有待审批动作", "当 Agent 提议外部写入、预算或发布动作时，会在这里等待另一位授权用户。", "shield-check");
    return;
  }
  target.innerHTML = items.map(item => approvalCard(item)).join("");
}

function renderAudit() {
  const target = $("audit-list");
  if (!state.audit.length) {
    designedEmpty(target, "暂无审计事件", "Runtime 中的真实操作记录会按时间倒序显示。", "clipboard-text");
    return;
  }
  target.innerHTML = state.audit.slice(0, 100).map(item => `<div class="data-row"><div class="data-main"><strong>${escapeHtml(item.action)}</strong><small>${badge(item.outcome)}${escapeHtml(item.resource_type)} · ${escapeHtml(isoLocal(item.created_at))}</small></div><div class="row-actions"><button data-action="view-json" data-json="${encodeURIComponent(JSON.stringify(item))}" class="secondary-button">查看</button></div></div>`).join("");
}

function renderAll() {
  renderCatalog();
  renderBriefing();
  renderEvidence();
  renderRuns();
  renderJobs();
  renderSchedules();
  renderApprovals();
  renderAudit();
  renderConnectors();
}

function renderDisconnected() {
  state.briefing = null;
  state.imports = [];
  state.runs = [];
  state.jobs = [];
  state.schedules = [];
  state.mission = null;
  state.audit = [];
  state.connectors = [];
  renderBriefing();
  renderEvidence();
  renderRuns();
  renderJobs();
  renderSchedules();
  renderApprovals();
  renderAudit();
  renderConnectors();
}

async function refreshAll() {
  if (!state.apiKey) return;
  const platform = encodeURIComponent(state.selectedPlatform);
  const [me, catalog, briefing, mission, imports, runs, jobs, schedules, audit, connectors] = await Promise.all([
    api("/v1/me"), api("/v1/catalog"), api(`/v1/briefing?platform=${platform}`), api("/v1/mission-control"),
    api("/v1/evidence-imports?limit=100"), api("/v1/agent-runs?limit=100"), api("/v1/jobs?limit=100"),
    api("/v1/schedules"), api("/v1/audit?limit=100"), api("/v1/connectors"),
  ]);
  Object.assign(state, {
    me, catalog, briefing, mission,
    imports: imports.imports || [], runs: runs.runs || [], jobs: jobs.jobs || [],
    schedules: schedules.schedules || [], audit: audit.events || [], connectors: connectors.connectors || [],
  });
  setConnected(true);
  renderAll();
}

async function tryDemoSession() {
  const response = await fetch("/v1/demo-session", {cache: "no-store"});
  if (response.status === 404) return false;
  let payload = {};
  try { payload = await response.json(); } catch { payload = {}; }
  if (!response.ok || payload.tenant_mode !== "demo" || !payload.api_key) {
    throw new Error(payload.error?.message || "Demo 会话初始化失败");
  }
  state.apiKey = payload.api_key;
  state.me = await api("/v1/me");
  if (state.me.tenant_mode !== "demo") {
    state.apiKey = "";
    state.me = null;
    throw new Error("Demo 会话租户模式校验失败");
  }
  setConnected(true);
  await refreshAll();
  notice("Demo 数据已自动加载。", "success");
  startPolling();
  return true;
}

async function refreshBriefing() {
  if (!state.apiKey) {
    renderBriefing();
    return;
  }
  state.briefing = await api(`/v1/briefing?platform=${encodeURIComponent(state.selectedPlatform)}`);
  renderBriefing();
}

async function act(button, task, success, refresh = true) {
  busy(button, true);
  try {
    await task();
    notice(success, "success");
    if (refresh) await refreshAll();
  } catch (error) {
    notice(error.message, "error");
  } finally {
    busy(button, false);
    setConnected(Boolean(state.apiKey));
  }
}

function showDetail(title, value) {
  $("detail-title").textContent = title;
  $("detail-content").textContent = JSON.stringify(value, null, 2);
  $("detail-dialog").showModal();
}

function latestReport(bundle) {
  return [...(bundle.artifacts || [])].reverse().find(item => item.kind === "weekly_ops_report")?.content;
}

function startPolling() {
  stopPolling();
  state.timer = setInterval(() => refreshAll().catch(error => notice(error.message, "error")), 30000);
}

function stopPolling() {
  if (state.timer) clearInterval(state.timer);
  state.timer = null;
}

document.body.addEventListener("click", event => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.dataset.id;
  switch (button.dataset.action) {
    case "navigate": navigate(button.dataset.view); break;
    case "open-connection": $("connection-dialog").showModal(); break;
    case "close-dialog": $(button.dataset.dialog).close(); break;
    case "refresh": act(button, refreshAll, "今日简报已刷新。", false); break;
    case "connect": connect(button); break;
    case "disconnect": disconnect(); break;
    case "select-platform": selectPlatform(button); break;
    case "select-metric": state.chartMetric = button.dataset.metric; renderChartControls(); break;
    case "view-priority": showDetail("Agent Brief", {run_id: state.briefing?.brief_run_id, priority: state.briefing?.priorities?.[Number(button.dataset.index)]}); break;
    case "view-json": showDetail("审计事件", JSON.parse(decodeURIComponent(button.dataset.json))); break;
    case "view-import": act(button, async () => showDetail("Evidence Import", await api(`/v1/evidence-imports/${id}`)), "Evidence 详情已加载。", false); break;
    case "view-job": act(button, async () => showDetail("Job", await api(`/v1/jobs/${id}`)), "Job 详情已加载。", false); break;
    case "view-action": showDetail("待审批 Action", (state.mission?.approval_inbox || []).find(item => item.id === id) || (state.briefing?.approvals || []).find(item => item.id === id)); break;
    case "view-run": act(button, async () => { const bundle = await api(`/v1/agent-runs/${id}`); showDetail("Agent Run", {run: bundle.run, tasks: bundle.tasks, evaluations: bundle.evaluations, report: latestReport(bundle)}); }, "Agent Run 详情已加载。", false); break;
    case "execute-run": act(button, () => api(`/v1/agent-runs/${id}/execute`, {method: "POST"}), "Agent Run 已完成。"); break;
    case "queue-run": act(button, () => api("/v1/jobs", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-job")}, json: {run_id: id, max_attempts: 3}}), "Run 已加入后台队列。"); break;
    case "evaluate-run": act(button, () => api(`/v1/agent-runs/${id}/evaluate`, {method: "POST"}), "Evaluation 已保存。"); break;
    case "approve-action": act(button, () => api(`/v1/actions/${id}/approve`, {method: "POST"}), "Action 已批准；仍需 Operator 执行。"); break;
    case "toggle-schedule": act(button, () => api(`/v1/schedules/${id}`, {method: "PATCH", json: {enabled: button.dataset.enabled === "true"}}), "Schedule 状态已更新。"); break;
    case "open-connector-form": openConnectorForm(); break;
    case "edit-connector": openConnectorForm(state.connectors.find(item => item.id === id)); break;
    case "health-check-connector": act(button, () => api(`/v1/connectors/${id}/health-check`, {method: "POST"}), "健康检查已完成。"); break;
  }
});

async function connect(button) {
  const key = $("api-key").value.trim();
  if (!key) { notice("请输入 API Key", "error"); return; }
  state.apiKey = key;
  busy(button, true);
  try {
    state.me = await api("/v1/me");
    setConnected(true);
    $("api-key").value = "";
    $("connection-dialog").close();
    await refreshAll();
    notice("已连接。API Key 仅保存在当前页面内存。", "success");
    startPolling();
  } catch (error) {
    state.apiKey = "";
    state.me = null;
    setConnected(false);
    notice(error.message, "error");
  } finally {
    busy(button, false);
    setConnected(Boolean(state.apiKey));
  }
}

function disconnect() {
  state.apiKey = "";
  state.me = null;
  stopPolling();
  setConnected(false);
  renderDisconnected();
  $("connection-dialog").close();
  notice("已断开；页面未保存 API Key。", "info");
}

async function selectPlatform(button) {
  state.selectedPlatform = button.dataset.platform;
  state.chartMetric = null;
  updatePlatformChrome();
  await act(button, refreshBriefing, `${platformName()} 简报已切换。`, false);
}

$("evidence-platform").addEventListener("change", () => renderReportOptions("evidence-platform", "evidence-type"));
$("schedule-platform").addEventListener("change", () => renderReportOptions("schedule-platform", "schedule-report-type"));
$("connector-provider").addEventListener("change", () => renderConnectorForm($("connector-provider").value));
$("connector-region").addEventListener("change", () => renderConnectorMarketplaces());

$("connector-form").addEventListener("submit", event => {
  event.preventDefault();
  const button = event.submitter;
  if (!connectorCanManage()) { notice("需要 admin 或 owner 角色", "error"); return; }
  const provider = $("connector-provider").value;
  const externalAccountId = $("connector-external-account-id").value.trim();
  const config = provider === "amazon_spapi" ? {
    region: $("connector-region").value,
    marketplace_ids: [...document.querySelectorAll('input[name="connector-marketplace"]:checked')].map(node => node.value),
    lwa_client_id_ref: $("amazon-lwa-client-id-ref").value.trim(),
    lwa_client_secret_ref: $("amazon-lwa-client-secret-ref").value.trim(),
    lwa_refresh_token_ref: $("amazon-refresh-token-ref").value.trim(),
  } : {
    shop_domain: $("shopify-domain").value.trim(),
    api_version: $("shopify-api-version").value.trim(),
    credential_ref: $("shopify-access-token-ref").value.trim(),
  };
  if (!externalAccountId || (provider === "amazon_spapi" && (!config.region || !config.marketplace_ids.length || !config.lwa_client_id_ref || !config.lwa_client_secret_ref || !config.lwa_refresh_token_ref)) || (provider === "shopify" && (!config.shop_domain || !config.api_version || !config.credential_ref))) {
    notice("请完成所有必填配置，并只填写环境变量名称。", "error"); return;
  }
  const connectorId = $("connector-id").value;
  act(button, async () => {
    const path = connectorId ? `/v1/connectors/${connectorId}` : "/v1/connectors";
    const json = connectorId ? {external_account_id: externalAccountId, config} : {provider, external_account_id: externalAccountId, config};
    await api(path, {method: connectorId ? "PATCH" : "POST", json});
    $("connector-dialog").close();
  }, connectorId ? "账户配置已更新。" : "账户已添加。");
});

$("evidence-form").addEventListener("submit", event => {
  event.preventDefault();
  const button = event.submitter, file = $("evidence-file").files[0];
  if (!file) { notice("请选择文件", "error"); return; }
  act(button, async () => {
    const observed = new Date($("evidence-observed").value).toISOString();
    const headers = {
      "Content-Type": file.type || (/\.xlsx$/i.test(file.name) ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" : "text/csv"),
      "X-Evidence-Platform": $("evidence-platform").value,
      "X-Evidence-Type": $("evidence-type").value,
      "X-Evidence-Filename": file.name,
      "X-Evidence-Observed-At": observed,
      "Idempotency-Key": idempotency("ui-evidence"),
    };
    const sheet = $("evidence-sheet").value.trim();
    if (sheet) headers["X-Evidence-Sheet"] = sheet;
    await api("/v1/evidence-imports", {method: "POST", headers, body: file});
    $("evidence-form").reset();
    setDefaultTimes();
  }, "Evidence 已导入并通过验证。");
});

$("run-form").addEventListener("submit", event => {
  event.preventDefault();
  const ids = [...document.querySelectorAll('input[name="run-evidence"]:checked')].map(node => node.value);
  if (!ids.length) { notice("至少选择一个 Evidence", "error"); return; }
  act(event.submitter, () => api("/v1/agent-runs", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-run")}, json: {workflow: "weekly_ops", objective: $("run-objective").value.trim(), evidence_import_ids: ids}}), "Agent Run 已创建。");
});

$("schedule-form").addEventListener("submit", event => {
  event.preventDefault();
  act(event.submitter, () => api("/v1/schedules", {method: "POST", json: {
    name: $("schedule-name").value.trim(), objective: $("schedule-objective").value.trim(),
    evidence_selectors: [{platform: $("schedule-platform").value, report_type: $("schedule-report-type").value}],
    interval_minutes: Number($("schedule-interval").value), next_run_at: new Date($("schedule-next-run").value).toISOString(),
  }}), "Schedule 已创建。");
});

function setDefaultTimes() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  $("evidence-observed").value = local;
  const next = new Date(now.getTime() + 5 * 60000);
  $("schedule-next-run").value = new Date(next.getTime() - next.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

window.addEventListener("resize", () => {
  const metric = (state.briefing?.metrics || []).find(item => item.key === state.chartMetric);
  if (metric) requestAnimationFrame(() => drawChart(metric));
});

const now = new Date();
$("today-label").textContent = `今天是 ${now.toLocaleDateString("zh-CN", {year: "numeric", month: "2-digit", day: "2-digit"})}`;
setDefaultTimes();
setConnected(false);
renderDisconnected();
tryDemoSession().catch(error => notice(error.message, "error"));
