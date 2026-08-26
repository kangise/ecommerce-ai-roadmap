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
  dailyOpsSchedules: [],
  dailyOpsRuns: [],
  dailyOpsLoading: false,
  dailyOpsScheduleError: null,
  dailyOpsRunError: null,
  mission: null,
  audit: [],
  connectors: [],
  reportRecipes: [],
  recipeLoading: false,
  recipeError: null,
  reportSyncs: [],
  syncLoading: false,
  syncError: null,
  metricObservations: [],
  metricMaterializations: [],
  metricLoading: false,
  metricError: null,
  materializationLoading: false,
  materializationError: null,
  adsCapabilityGates: [],
  adsCapabilityLoading: false,
  adsCapabilityError: null,
  adsAdapterStatus: null,
  adsAdapterLoading: false,
  adsAdapterError: null,
  proposals: [], proposalsLoading: false, proposalsError: null, proposalExecutions: [],
  missionEvents: [],
  liveStatus: "disconnected",
  liveError: null,
  liveCursor: null,
  liveLastAt: null,
  liveAbort: null,
  liveRetryTimer: null,
  liveRefreshTimer: null,
  liveServerRetryMs: null,
  liveAttempt: 0,
  liveStopped: true,
  pilotStatus: null,
  pilotLoading: false,
  pilotError: null,
  assuranceRuns: [],
  assuranceLoading: false,
  assuranceError: null,
  agentGraphs: [],
  agentGraphsLoading: false,
  agentGraphsError: null,
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
  return entry?.label?.zh || entry?.label?.en || entry?.label || entry?.name || (provider === "amazon_spapi" ? "Amazon" : provider === "amazon_ads" ? "Amazon Ads" : provider === "shopify" ? "Shopify" : provider);
}

function connectorDetails(connector) {
  const details = connector.provider_details || {};
  if (connector.provider === "amazon_spapi") {
    const marketplaces = details.marketplaces || details.marketplace_ids || [];
    const catalog = new Map((state.catalog?.amazon_marketplaces || []).map(item => [item.id, item.name || item.label || item.id]));
    return [details.region, marketplaces.map(item => catalog.get(typeof item === "string" ? item : item.id) || (typeof item === "string" ? item : item.id)).join("、")].filter(Boolean).join(" · ") || "未配置 region 或 marketplace";
  }
  if (connector.provider === "shopify") return details.shop_domain || "未配置 Shopify domain";
  if (connector.provider === "amazon_ads") return [details.region, details.profile_id ? `Profile ${details.profile_id}` : "未配置 profile"].filter(Boolean).join(" · ");
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
    designedEmpty(target, "还没有连接账户", manage ? "添加 Amazon SP-API、Amazon Ads 或 Shopify 账户，并使用环境变量引用授权凭据。" : "当前租户尚未连接账户；需要 admin 或 owner 添加。", "key");
    return;
  }
  target.innerHTML = state.connectors.map(connector => {
    const healthStatus = connector.health_status || "unchecked";
    const edit = manage ? `<button data-action="edit-connector" data-id="${escapeHtml(connector.id)}" class="secondary-button">编辑</button>` : "";
    const healthAction = check ? `<button data-action="health-check-connector" data-id="${escapeHtml(connector.id)}" class="primary-button">健康检查</button>` : `<span class="permission-reason">需要 operator、admin 或 owner 执行健康检查</span>`;
    const adsGateAction = connector.provider === "amazon_ads" ? (connectorCanManage() ? `<button data-action="open-ads-capability-form" data-id="${escapeHtml(connector.id)}" class="secondary-button">运行准入检查</button>` : `<span class="permission-reason">需要 admin 或 owner 运行 Ads 准入检查</span>`) : "";
    const failure = connector.health_error_message || connector.health_error_code;
    const refCount = Object.keys(connector.credential_refs || {}).length;
    return `<article class="connector-card"><div class="connector-card-head"><div><p class="kicker">${escapeHtml(connectorProviderLabel(connector.provider))}</p><h2>${escapeHtml(connector.external_account_id)}</h2><p>${escapeHtml(connectorDetails(connector))}</p></div>${badge(healthStatus)}</div><dl class="connector-meta"><div><dt>Last checked</dt><dd>${escapeHtml(isoLocal(connector.health_checked_at))}</dd></div><div><dt>Credential refs</dt><dd>${refCount ? `${refCount} present` : "—"}</dd></div></dl>${failure ? `<p class="connector-error">${escapeHtml(failure)}</p>` : ""}<div class="row-actions">${edit}${healthAction}${adsGateAction}</div></article>`;
  }).join("");
}

function renderAdsAdapterStatus() {
  const target = $("ads-adapter-status");
  if (!target) return;
  if (!state.apiKey) { designedEmpty(target, "尚未连接 Runtime", "连接后读取真实 Amazon Ads Adapter 状态。", "key"); return; }
  if (state.adsAdapterLoading) { designedEmpty(target, "正在读取 Adapter 状态", "正在获取当前构建的真实注册与写入能力。", "database"); return; }
  if (state.adsAdapterError) { target.innerHTML = `<div class="ads-adapter-failure" role="alert"><strong>无法加载 Adapter 状态</strong><span>${escapeHtml(state.adsAdapterError)}</span></div>`; return; }
  const value = state.adsAdapterStatus || {};
  const status = value.status || "blocked";
  const reasonLabels = {no_amazon_ads_account: "尚无 Amazon Ads 账户", no_capability_gate: "尚无 L5 准入记录", gate_not_passed: "L5 Gate 未通过", required_capabilities_missing: "必需能力不完整", gate_account_config_mismatch: "账户 region 或 Profile 已变化", gate_not_checked: "Gate 尚未完成", gate_stale_account_changed: "账户在 Gate 后已更新", gate_expired: "Gate 已超过 24 小时", gate_checked_in_future: "Gate 时间异常", adapter_not_installed: "Adapter 未安装", write_surface_disabled: "写入面已关闭"};
  const reasons = (value.reason_codes || []).map(item => typeof item === "string" ? (reasonLabels[item] || item) : item.code || item.message).filter(Boolean);
  const label = status === "eligible_not_installed" ? "Eligible · 未安装" : "Blocked";
  target.innerHTML = `<article class="ads-adapter-card"><div class="ads-adapter-head"><div><p class="kicker">Adapter Lock</p><h3>Amazon Ads 写入适配器</h3><p>${escapeHtml(value.evaluated_at ? `检查于 ${isoLocal(value.evaluated_at)}` : "当前租户的真实准入评估")}</p></div>${badge(status)}</div><dl class="ads-adapter-meta"><div><dt>状态</dt><dd>${escapeHtml(label)}</dd></div><div><dt>Adapter registered</dt><dd>${value.adapter_registered === true ? "是" : "否"}</dd></div><div><dt>写操作</dt><dd>${escapeHtml((value.write_operations || []).join("、") || "无")}</dd></div><div><dt>原因</dt><dd>${escapeHtml(reasons.join(" · ") || "未提供原因")}</dd></div></dl><p class="ads-adapter-lock-note">当前构建未注册 Amazon Ads 写操作。此区域仅展示准入锁状态，不提供执行、解锁或写入按钮。</p></article>`;
}

function connectorProviders() {
  return state.catalog?.connector_providers || [{id: "amazon_spapi", name: "Amazon Selling Partner API"}, {id: "amazon_ads", name: "Amazon Ads API"}, {id: "shopify", name: "Shopify Admin API"}];
}

function renderConnectorForm(provider = $("connector-provider").value || "amazon_spapi", connector = null) {
  const providerSelect = $("connector-provider");
  providerSelect.innerHTML = connectorProviders().map(item => `<option value="${escapeHtml(item.id || item.provider)}">${escapeHtml(item.label?.zh || item.label?.en || item.label || item.name || item.id || item.provider)}</option>`).join("");
  providerSelect.value = provider;
  const amazon = provider === "amazon_spapi";
  const ads = provider === "amazon_ads";
  $("amazon-connector-fields").hidden = !amazon;
  $("amazon-ads-connector-fields").hidden = !ads;
  $("shopify-connector-fields").hidden = amazon || ads;
  if (ads) {
    const details = connector?.provider_details || {};
    $("amazon-ads-region").value = details.region || "";
    $("amazon-ads-profile-id").value = details.profile_id || "";
    return;
  }
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
  $("amazon-ads-lwa-client-id-ref").value = "";
  $("amazon-ads-lwa-client-secret-ref").value = "";
  $("amazon-ads-refresh-token-ref").value = "";
  $("shopify-domain").value = details.shop_domain || "";
  $("shopify-api-version").value = details.api_version || "";
  $("shopify-access-token-ref").value = "";
  renderConnectorForm(connector?.provider || "amazon_spapi", connector);
  $("connector-provider").disabled = Boolean(connector);
  $("connector-dialog").showModal();
}

function adsCapabilityCanRun() {
  return ["admin", "owner"].includes(state.me?.role);
}

function amazonAdsAccounts() {
  return state.connectors.filter(connector => connector.provider === "amazon_ads");
}

function adsCheckList(gate) {
  const checks = gate.checks || gate.check_results || gate.results || {};
  const normalized = Array.isArray(checks) ? checks : Object.entries(checks).map(([key, value]) => ({key, ...(typeof value === "object" ? value : {status: value})}));
  if (!normalized.length) return "<span class=\"permission-reason\">检查详情将在请求完成后显示。</span>";
  const labels = {lwa: "LWA 授权", profiles_read: "Ads Profiles", target_profile: "Profile 匹配", campaigns_list_read: "Sponsored Products 只读", external_attestation: "外部批准证明"};
  return `<ul class="ads-check-list">${normalized.map(check => `<li>${badge(check.status || check.outcome || "checking")}<span>${escapeHtml(check.label || labels[check.name || check.key] || check.name || check.key || "check")}</span>${check.detail || check.message ? `<small>${escapeHtml(check.detail || check.message)}</small>` : ""}</li>`).join("")}</ul>`;
}

function renderAdsCapabilityGates() {
  const target = $("ads-capability-list"), note = $("ads-capability-permission"), add = $("add-ads-capability-btn");
  if (!state.apiKey) {
    add.disabled = true; add.title = "请先连接 Runtime";
    note.hidden = false; note.textContent = "连接 Runtime 后才能读取或运行 Amazon Ads 准入检查。";
    designedEmpty(target, "尚未连接 Runtime", "准入状态需要已认证的租户会话。", "key");
    return;
  }
  const canRun = adsCapabilityCanRun(), accounts = amazonAdsAccounts();
  add.disabled = !canRun || !accounts.length;
  add.title = !canRun ? "需要 admin 或 owner 角色" : !accounts.length ? "请先添加 Amazon Ads 账户" : "";
  note.hidden = canRun;
  note.textContent = canRun ? "" : "当前角色可查看准入结果；只有 admin 或 owner 可以运行检查。";
  if (state.adsCapabilityLoading) { designedEmpty(target, "正在读取 Ads 准入状态", "正在获取此租户最近的真实检查结果。", "database"); return; }
  if (state.adsCapabilityError) { target.innerHTML = `<div class="ads-capability-failure" role="alert"><strong>无法加载 Amazon Ads 准入状态</strong><span>${escapeHtml(state.adsCapabilityError)}</span></div>`; return; }
  if (!accounts.length) {
    designedEmpty(target, "还没有 Amazon Ads 账户", "请使用页面上方“添加账户”，配置 region、Profile ID 和 LWA 环境变量引用后再验证。", "key");
    return;
  }
  if (!state.adsCapabilityGates.length) { designedEmpty(target, "尚未运行准入检查", canRun ? "选择一个 Amazon Ads 账户，运行真实授权与读取能力检查。" : "等待 admin 或 owner 运行首次检查。", "database"); return; }
  target.innerHTML = state.adsCapabilityGates.map(gate => {
    const account = state.connectors.find(item => item.id === gate.connector_account_id);
    const status = gate.overall_status || gate.status || "checking";
    const blockers = gate.blockers || gate.safe_blockers || (gate.status === "blocked" || gate.status === "failed" ? [gate.error_message || gate.error_code].filter(Boolean) : []);
    const requestId = Array.isArray(gate.request_ids) ? gate.request_ids.join(" · ") : gate.request_id || gate.external_request_id;
    return `<article class="ads-capability-card"><div class="ads-capability-head"><div><p class="kicker">${escapeHtml(account?.external_account_id || "Amazon Ads account")}</p><h3>${escapeHtml(account ? connectorDetails(account) : gate.connector_account_id)}</h3><p>${escapeHtml(isoLocal(gate.checked_at || gate.created_at || gate.updated_at))}</p></div>${badge(status)}</div><div class="ads-checks">${adsCheckList(gate)}</div>${blockers.length ? `<p class="ads-blockers"><strong>阻塞原因</strong>${escapeHtml(blockers.map(item => typeof item === "string" ? item : item.message || item.code).join(" · "))}</p>` : ""}<dl class="ads-capability-meta"><div><dt>Request ID</dt><dd>${escapeHtml(requestId || "—")}</dd></div><div><dt>外部证明</dt><dd>${escapeHtml(gate.attestation_reference || "—")}</dd></div></dl><div class="row-actions"><button data-action="view-ads-capability-gate" data-id="${escapeHtml(gate.id)}" class="secondary-button">查看详情</button></div></article>`;
  }).join("");
}

function openAdsCapabilityForm(accountId = "") {
  if (!adsCapabilityCanRun()) { notice("需要 admin 或 owner 角色", "error"); return; }
  const accounts = amazonAdsAccounts();
  if (!accounts.length) { notice("请先添加 Amazon Ads 账户。", "error"); return; }
  $("ads-capability-form").reset();
  $("ads-capability-account").innerHTML = accounts.map(account => `<option value="${escapeHtml(account.id)}">${escapeHtml(account.external_account_id)} · ${escapeHtml(connectorDetails(account))}</option>`).join("");
  $("ads-capability-account").value = accountId || accounts[0].id;
  $("ads-capability-dialog").showModal();
}

function recipeCanManage() {
  return ["operator", "admin", "owner"].includes(state.me?.role);
}

function amazonRecipeAccounts() {
  return state.connectors.filter(connector => connector.provider === "amazon_spapi");
}

function reportRecipeTypes() {
  return state.catalog?.report_recipe_types || [];
}

function recipeType(recipe) {
  return reportRecipeTypes().find(type => type.key === recipe.recipe_key) || {
    key: recipe.recipe_key,
    label: recipe.recipe_key,
    amazon_report_type: recipe.amazon_report_type,
    evidence_report_type: recipe.evidence_report_type,
  };
}

function recipeMarketplaceLabel(id) {
  const marketplace = (state.catalog?.amazon_marketplaces || []).find(item => item.id === id);
  return marketplace?.name || marketplace?.label || id;
}

function recipeAccountLabel(account) {
  return `${account.external_account_id}${connectorDetails(account) ? ` · ${connectorDetails(account)}` : ""}`;
}

function toDatetimeLocal(value, fallback = null) {
  const date = value ? new Date(value) : fallback || new Date(Date.now() + 5 * 60000);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function recipeSyncAvailability(recipe) {
  if (!recipeCanManage()) return {enabled: false, reason: "需要 operator、admin 或 owner 角色才能排队同步。"};
  const account = state.connectors.find(item => item.id === recipe.connector_account_id);
  if (!account) return {enabled: false, reason: "关联的 Amazon account 不可用，无法排队同步。"};
  if (account.health_status !== "healthy") {
    return {enabled: false, reason: `账户健康状态为 ${account.health_status || "unchecked"}；通过健康检查后才能排队同步。`};
  }
  return {enabled: true, reason: ""};
}

function renderReportRecipes() {
  const target = $("recipe-list"), note = $("recipe-permission"), add = $("add-recipe-btn");
  if (!state.apiKey) {
    add.disabled = true;
    add.title = "请先连接 Runtime";
    note.hidden = false;
    note.textContent = "连接 Runtime 后才能查看或管理 Report Recipes。";
    designedEmpty(target, "尚未连接 Runtime", "Recipe 列表需要已认证的租户会话。", "database");
    return;
  }
  const manage = recipeCanManage();
  const accounts = amazonRecipeAccounts();
  const types = reportRecipeTypes();
  add.disabled = !manage || !accounts.length || !types.length;
  add.title = !manage ? "需要 operator、admin 或 owner 角色" : !accounts.length ? "请先添加 Amazon SP-API 账户" : !types.length ? "Catalog 未提供 Recipe 类型" : "";
  note.hidden = manage;
  note.textContent = manage ? "" : "当前角色只能查看 Report Recipes。创建或编辑需要 operator、admin 或 owner 角色。";
  if (state.recipeLoading) {
    designedEmpty(target, "正在加载 Report Recipes", "正在读取此租户保存的采集规则。", "database");
    return;
  }
  if (state.recipeError) {
    target.innerHTML = `<div class="recipe-failure" role="alert"><strong>无法加载 Report Recipes</strong><span>${escapeHtml(state.recipeError)}</span></div>`;
    return;
  }
  if (!state.reportRecipes.length) {
    const copy = !accounts.length ? "先添加 Amazon SP-API 账户，才能创建 Recipe。" : manage ? "添加 Recipe 后，L3 Worker 会按保存规则异步采集。" : "当前租户还没有保存的 Recipe；需要具备权限的用户创建。";
    designedEmpty(target, "还没有 Report Recipes", copy, "database");
    return;
  }
  target.innerHTML = state.reportRecipes.map(recipe => {
    const account = state.connectors.find(item => item.id === recipe.connector_account_id);
    const type = recipeType(recipe);
    const edit = manage ? `<button data-action="edit-recipe" data-id="${escapeHtml(recipe.id)}" class="secondary-button">编辑</button>` : "";
    const sync = recipeSyncAvailability(recipe);
    const enqueue = `<button data-action="enqueue-report-sync" data-id="${escapeHtml(recipe.id)}" class="primary-button" ${sync.enabled ? "" : `disabled title="${escapeHtml(sync.reason)}"`}>运行同步</button>`;
    return `<article class="recipe-card"><div class="recipe-card-head"><div><p class="kicker">${escapeHtml(type.label || type.key)}</p><h3>${escapeHtml(recipe.name)}</h3><p>${escapeHtml(account ? recipeAccountLabel(account) : "Amazon account unavailable")}</p></div>${badge(recipe.enabled ? "enabled" : "disabled")}</div><dl class="recipe-meta"><div><dt>Report type</dt><dd>${escapeHtml(recipe.amazon_report_type)} → ${escapeHtml(recipe.evidence_report_type)}</dd></div><div><dt>Marketplaces</dt><dd>${escapeHtml((recipe.marketplace_ids || []).map(recipeMarketplaceLabel).join("、") || "—")}</dd></div><div><dt>Cadence / lookback</dt><dd>${escapeHtml(`${recipe.interval_minutes} min · ${recipe.lookback_days} days`)}</dd></div><div><dt>Next run</dt><dd>${escapeHtml(isoLocal(recipe.next_run_at))}</dd></div></dl><div class="row-actions">${enqueue}${edit}</div>${sync.reason ? `<span class="permission-reason">${escapeHtml(sync.reason)}</span>` : ""}<span class="sync-async-note">L3 Worker 将异步执行和轮询，不会在此页面即时完成。</span></article>`;
  }).join("");
}

function reportSyncStage(sync) {
  return sync.status || sync.processing_status || "queued";
}

function renderReportSyncs() {
  const target = $("sync-list");
  if (!state.apiKey) {
    designedEmpty(target, "尚未连接 Runtime", "Sync Activity 需要已认证的租户会话。", "pulse");
    return;
  }
  if (state.syncLoading) {
    designedEmpty(target, "正在加载 Sync Activity", "正在读取 L3 Worker 的异步任务状态。", "pulse");
    return;
  }
  if (state.syncError) {
    target.innerHTML = `<div class="sync-failure" role="alert"><strong>无法加载 Sync Activity</strong><span>${escapeHtml(state.syncError)}</span></div>`;
    return;
  }
  if (!state.reportSyncs.length) {
    designedEmpty(target, "暂无同步活动", "通过健康检查的 Amazon account 可从 Recipe 排队；L3 Worker 会在后台执行。", "pulse");
    return;
  }
  target.innerHTML = state.reportSyncs.map(sync => {
    const recipe = state.reportRecipes.find(item => item.id === sync.recipe_id);
    const stage = reportSyncStage(sync);
    const processing = sync.processing_status && sync.processing_status !== stage ? `${badge(sync.processing_status)}<span class="sync-lifecycle">processing</span>` : "";
    const error = sync.error_message || sync.error_code;
    return `<article class="sync-card"><div class="sync-card-head"><div><p class="kicker">L3 Worker</p><h3>${escapeHtml(recipe?.name || sync.recipe_id)}</h3><p>${escapeHtml(recipe ? "Report Recipe sync" : "Report Recipe unavailable")}</p></div><div class="sync-status">${badge(stage)}${processing}</div></div><dl class="sync-meta"><div><dt>Attempt</dt><dd>${escapeHtml(`${sync.attempt_count ?? 0}/${sync.max_attempts ?? "—"}`)}</dd></div><div><dt>Next poll</dt><dd>${escapeHtml(isoLocal(sync.available_at))}</dd></div><div><dt>Evidence</dt><dd>${escapeHtml(sync.evidence_import_id || "—")}</dd></div><div><dt>Completed</dt><dd>${escapeHtml(isoLocal(sync.completed_at))}</dd></div></dl>${error ? `<p class="sync-error">${escapeHtml(error)}</p>` : ""}<div class="row-actions"><button data-action="view-report-sync" data-id="${escapeHtml(sync.id)}" class="secondary-button">详情</button></div></article>`;
  }).join("");
}

function renderRecipeAccountOptions(selectedId = "") {
  const accounts = amazonRecipeAccounts();
  $("recipe-connector-account").innerHTML = accounts.map(account => `<option value="${escapeHtml(account.id)}">${escapeHtml(recipeAccountLabel(account))}</option>`).join("");
  $("recipe-connector-account").value = selectedId || accounts[0]?.id || "";
}

function renderRecipeTypeOptions(selectedKey = "") {
  const types = reportRecipeTypes();
  $("recipe-type").innerHTML = types.map(type => `<option value="${escapeHtml(type.key)}">${escapeHtml(type.label || type.key)}</option>`).join("");
  $("recipe-type").value = selectedKey || types[0]?.key || "";
}

function recipeAccountMarketplaces(account) {
  const details = account?.provider_details || {};
  const accountIds = details.marketplace_ids || details.marketplaces || [];
  const permitted = new Set(accountIds.map(item => typeof item === "string" ? item : item.id));
  return (state.catalog?.amazon_marketplaces || []).filter(item => permitted.has(item.id));
}

function renderRecipeMarketplaces(selected = []) {
  const account = state.connectors.find(item => item.id === $("recipe-connector-account").value);
  const selectedIds = new Set(selected.map(item => typeof item === "string" ? item : item.id));
  const marketplaces = recipeAccountMarketplaces(account);
  $("recipe-marketplaces").innerHTML = marketplaces.length ? marketplaces.map(item => `<label><input type="checkbox" name="recipe-marketplace" value="${escapeHtml(item.id)}" ${selectedIds.has(item.id) ? "checked" : ""}>${escapeHtml(item.name || item.label || item.id)}</label>`).join("") : "<span class=\"permission-reason\">该 Amazon account 没有可用的已配置 marketplace。</span>";
}

function openRecipeForm(recipe = null) {
  if (!recipeCanManage()) { notice("需要 operator、admin 或 owner 角色", "error"); return; }
  if (!amazonRecipeAccounts().length || !reportRecipeTypes().length) { notice("需要已配置的 Amazon SP-API 账户和 Catalog Recipe 类型。", "error"); return; }
  $("recipe-form").reset();
  $("recipe-id").value = recipe?.id || "";
  $("recipe-dialog-title").textContent = recipe ? "编辑 Recipe" : "添加 Recipe";
  $("recipe-name").value = recipe?.name || "";
  $("recipe-interval").value = recipe?.interval_minutes || 1440;
  $("recipe-lookback").value = recipe?.lookback_days || 7;
  $("recipe-next-run").value = toDatetimeLocal(recipe?.next_run_at);
  $("recipe-enabled").checked = recipe?.enabled ?? true;
  renderRecipeAccountOptions(recipe?.connector_account_id || "");
  $("recipe-connector-account").disabled = Boolean(recipe);
  $("recipe-connector-account").title = recipe ? "已创建的 Recipe 不能更换 Amazon account" : "";
  renderRecipeTypeOptions(recipe?.recipe_key || "");
  renderRecipeMarketplaces(recipe?.marketplace_ids || []);
  $("recipe-dialog").showModal();
}

function renderCatalog() {
  const platforms = state.catalog?.platforms || [];
  const reports = state.catalog?.report_types || [];
  for (const id of ["evidence-platform", "schedule-platform"]) {
    $(id).innerHTML = platforms.map(platform => `<option value="${escapeHtml(platform.id)}">${escapeHtml(platform.label?.zh || platform.label?.en || platform.id)}</option>`).join("");
    if (platforms.some(platform => platform.id === state.selectedPlatform)) $(id).value = state.selectedPlatform;
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
    const unitNote = metric.format === "amount" ? (metric.currency || "币种未知") : `观测于 ${shortDate(metric.observed_at)}`;
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
  const identity = metric => metric.series_id || metric.key;
  if (!metrics.some(metric => identity(metric) === state.chartMetric)) state.chartMetric = identity(metrics[0]);
  $("chart-controls").innerHTML = metrics.map(metric => {
    const label = [metric.label, metric.currency, metric.time_grain].filter(Boolean).join(" · ");
    return `<button data-action="select-metric" data-metric="${escapeHtml(identity(metric))}" class="metric-toggle ${identity(metric) === state.chartMetric ? "active" : ""}">${escapeHtml(label)}</button>`;
  }).join("");
  drawChart(metrics.find(metric => identity(metric) === state.chartMetric));
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
    "human.review": "人工复核记录",
    "amazon_spapi.import_report": "导入 Amazon SP-API 报表",
    "amazon_ads.campaign_update": "更新 Amazon Ads Campaign",
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
  const canMaterialize = metricCanMaterialize();
  target.innerHTML = state.imports.map(item => {
    const supported = (state.catalog?.metric_materialization_report_types || []).includes(item.report_type);
    const enabled = canMaterialize && supported;
    const disabledReason = supported ? "需要 operator、admin 或 owner 角色" : "该报告类型尚无指标映射";
    const materialize = `<button data-action="materialize-evidence-metrics" data-id="${escapeHtml(item.id)}" class="primary-button" ${enabled ? "" : `disabled title="${escapeHtml(disabledReason)}"`}>物化指标</button>`;
    const reason = enabled ? "" : `<span class="permission-reason">${escapeHtml(supported ? "当前角色只能查看；物化指标需要 operator、admin 或 owner。" : "该报告类型尚无指标映射；当前不会生成指标观测。")}</span>`;
    return `<div class="data-row"><div class="data-main"><strong>${escapeHtml(item.filename)}</strong><small>${badge(item.platform)}${escapeHtml(item.report_type)} · ${item.row_count} rows · ${escapeHtml(isoLocal(item.observed_at))}</small></div><div class="row-actions"><button data-action="view-import" data-id="${escapeHtml(item.id)}" class="secondary-button">查看</button>${materialize}</div>${reason}</div>`;
  }).join("");
  options.innerHTML = state.imports.map(item => `<label><input type="checkbox" name="run-evidence" value="${item.id}">${escapeHtml(item.platform)} · ${escapeHtml(item.filename)}</label>`).join("");
}

function runCanCreate() {
  return ["operator", "admin", "owner"].includes(state.me?.role);
}

function graphVersions(graph) {
  return graph.versions || graph.published_versions || (graph.version ? [graph.version] : []);
}

function publishedGraphVersion(graph) {
  const versions = graphVersions(graph);
  return graph.published_version || graph.current_version || versions.find(item => item.id === graph.published_version_id || item.version_id === graph.published_version_id) || versions.find(item => item.status === "published") || {};
}

function graphVersionId(graph) {
  const version = publishedGraphVersion(graph);
  return version.id || version.version_id || graph.published_version_id || graph.version_id || "";
}

function graphVersionLabel(graph) {
  const version = publishedGraphVersion(graph);
  return version.version || version.version_number || graph.version || "published";
}

function graphNodes(graph) {
  const version = publishedGraphVersion(graph);
  return version.nodes || graph.nodes || version.definition?.nodes || graph.definition?.nodes || [];
}

function graphEdges(graph) {
  const version = publishedGraphVersion(graph);
  return version.edges || graph.edges || version.definition?.edges || graph.definition?.edges || [];
}

function graphHash(graph) {
    const version = publishedGraphVersion(graph);
    return version.content_hash || version.definition_hash || graph.content_hash || graph.definition_hash || "—";
}

function graphExecutionHash(graph) {
  const version = publishedGraphVersion(graph);
  return version.execution_contract_hash || graph.execution_contract_hash || "—";
}

function graphNodeLabel(node) {
  const name = typeof node === "string" ? node : node.role || node.key || node.label || node.name || node.agent || node.id || "Agent";
  const labels = {evidence_analyst: "Evidence Analyst", platform_specialist: "平台专家 × 输入市场", cross_controller: "跨平台 Controller（多平台时）", manager: "Manager", reviewer: "Reviewer"};
  return labels[name] || String(name).replaceAll("_", " ");
}

function renderAgentGraphs() {
  const target = $("agent-graph-list"), options = $("run-graph-options"), reason = $("run-permission-reason"), submit = document.querySelector('#run-form button[type="submit"]');
  const operator = runCanCreate();
  if (!state.apiKey) {
    designedEmpty(target, "尚未连接 Runtime", "连接后读取当前租户已发布的协作图。", "robot");
    designedEmpty(options, "尚未连接", "连接 Runtime 后才能选择已发布协作图。", "robot");
    reason.hidden = false; reason.textContent = "请先连接 Runtime。"; submit.disabled = true; submit.title = reason.textContent;
    return;
  }
  if (state.agentGraphsLoading) {
    designedEmpty(target, "正在加载协作图", "正在读取已发布版本与节点拓扑。", "robot");
    designedEmpty(options, "正在加载协作图", "等待已发布版本返回。", "robot");
    reason.hidden = false; reason.textContent = "协作图加载中。"; submit.disabled = true; submit.title = reason.textContent;
    return;
  }
  if (state.agentGraphsError) {
    target.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>无法加载协作图</strong><span>${escapeHtml(state.agentGraphsError)}</span></div>`;
    designedEmpty(options, "协作图不可用", "加载失败时不能创建新的 Agent Run。", "robot");
    reason.hidden = false; reason.textContent = "协作图加载失败，无法运行。"; submit.disabled = true; submit.title = reason.textContent;
    return;
  }
  const published = state.agentGraphs.filter(graph => graphVersionId(graph));
  if (!published.length) {
    designedEmpty(target, "尚无已发布协作图", "管理员需要先通过 Agent Graph API 发布版本；这里不会创建未持久化的图。", "robot");
    designedEmpty(options, "暂无可选协作图", "没有已发布版本时，不能创建 Agent Run。", "robot");
    reason.hidden = false; reason.textContent = "当前租户没有已发布协作图。"; submit.disabled = true; submit.title = reason.textContent;
    return;
  }
  target.innerHTML = published.map(graph => {
    const nodes = graphNodes(graph), edges = graphEdges(graph), versionId = graphVersionId(graph);
    const byRole = role => nodes.find(node => (node.role || node.key) === role);
    const stages = nodes.length
      ? [[byRole("evidence_analyst"), byRole("platform_specialist")].filter(Boolean), [byRole("cross_controller")].filter(Boolean), [byRole("manager")].filter(Boolean), [byRole("reviewer")].filter(Boolean)].filter(stage => stage.length)
      : [["evidence_analyst", "platform_specialist"], ["cross_controller"], ["manager"], ["reviewer"]];
    const nodeMarkup = stages.map(stage => `<span class="graph-stage">${stage.map(node => `<span class="graph-node">${escapeHtml(graphNodeLabel(node))}</span>`).join('<span class="graph-plus" aria-hidden="true">＋</span>')}</span>`).join('<span class="graph-arrow" aria-hidden="true">→</span>');
    return `<article class="agent-graph-card"><div class="agent-graph-head"><div><p class="kicker">Published graph</p><h3>${escapeHtml(graph.name || graph.slug || graph.id || "Agent Graph")}</h3><p>Version ${escapeHtml(graphVersionLabel(graph))} · tool policy: none</p></div>${badge("published")}</div><div class="graph-topology" aria-label="${escapeHtml(graph.name || "Agent Graph")} 拓扑">${nodeMarkup}</div><dl class="agent-graph-meta"><div><dt>Version ID</dt><dd>${escapeHtml(versionId)}</dd></div><div><dt>Definition hash</dt><dd>${escapeHtml(graphHash(graph))}</dd></div><div><dt>Execution hash</dt><dd>${escapeHtml(graphExecutionHash(graph))}</dd></div><div><dt>Edges</dt><dd>${escapeHtml(String(edges.length))}</dd></div><div><dt>Tool policy</dt><dd>none</dd></div></dl></article>`;
  }).join("");
  options.innerHTML = published.map((graph, index) => `<label><input type="radio" name="run-graph-version" value="${escapeHtml(graphVersionId(graph))}" ${index === 0 ? "checked" : ""}>${escapeHtml(graph.name || graph.slug || graph.id || "Agent Graph")} · v${escapeHtml(graphVersionLabel(graph))}</label>`).join("");
  reason.hidden = operator;
  reason.textContent = operator ? "" : "当前角色只能查看协作图；创建 Agent Run 需要 operator、admin 或 owner。";
  submit.disabled = !operator;
  submit.title = operator ? "" : reason.textContent;
}

function renderRunMetricOptions() {
  const target = $("run-metric-options");
  if (!state.apiKey) { designedEmpty(target, "尚未连接", "连接后选择真实指标观测。", "chart-line-up"); return; }
  if (state.metricLoading) { designedEmpty(target, "正在加载指标观测", "正在读取可作为 Agent 输入的真实数值。", "chart-line-up"); return; }
  if (state.metricError) { target.innerHTML = `<div class="metric-failure" role="alert"><strong>无法加载指标观测</strong><span>${escapeHtml(state.metricError)}</span></div>`; return; }
  if (!state.metricObservations.length) { designedEmpty(target, "暂无可选 Metric Observation", "可以只选择 Evidence；指标物化完成后可在这里附加。", "chart-line-up"); return; }
  target.innerHTML = state.metricObservations.slice(0, 100).map(observation => `<label><input type="checkbox" name="run-metric-observation" value="${escapeHtml(observation.id)}">${escapeHtml(observation.metric_key || observation.metric_name || observation.name || observation.id)} · ${escapeHtml(metricDisplayValue(observation))}</label>`).join("");
}

function metricCanMaterialize() {
  return ["operator", "admin", "owner"].includes(state.me?.role);
}

function metricDisplayValue(observation) {
  const value = observation.value_decimal ?? observation.value ?? observation.metric_value ?? observation.numeric_value;
  if (value === null || value === undefined || value === "") return "—";
  const numeric = Number(value);
  if (observation.unit === "ratio" && Number.isFinite(numeric)) return `${new Intl.NumberFormat("zh-CN", {maximumFractionDigits: 4}).format(numeric * 100)}%`;
  const rendered = Number.isFinite(numeric) ? new Intl.NumberFormat("zh-CN", {maximumFractionDigits: 4}).format(numeric) : String(value);
  const currency = observation.currency || observation.currency_code;
  const unit = observation.unit || observation.value_unit;
  return [rendered, currency, unit].filter(Boolean).join(" ");
}

function metricPeriod(observation) {
  const start = observation.period_start || observation.period_start_at;
  const end = observation.period_end || observation.period_end_at;
  const grain = observation.grain || observation.period_grain || observation.time_grain;
  const range = start || end ? `${shortDate(start)} — ${shortDate(end)}` : "未提供周期";
  return grain ? `${range} · ${grain}` : range;
}

function metricFlags(observation) {
  const flags = observation.quality?.flags || observation.quality_flags || observation.quality_flag_codes || [];
  const values = Array.isArray(flags) ? flags : Object.entries(flags).filter(([, enabled]) => Boolean(enabled)).map(([key]) => key);
  return values.length ? values.map(flag => `<span class="quality-flag">${escapeHtml(typeof flag === "string" ? flag : flag.code || flag.label || JSON.stringify(flag))}</span>`).join("") : '<span class="quality-clear">未报告质量警告</span>';
}

function materializationStatus(materialization) {
  return materialization.status || materialization.state || materialization.processing_status || "unknown";
}

function materializationEvidenceId(materialization) {
  return materialization.evidence_import_id || materialization.import_id || materialization.source_evidence_import_id;
}

function renderMetricObservations() {
  const target = $("metric-observation-list");
  if (!state.apiKey) {
    designedEmpty(target, "尚未连接 Runtime", "指标观测需要已认证的租户会话。", "chart-line-up");
    return;
  }
  if (state.metricLoading) {
    designedEmpty(target, "正在加载指标观测", "正在读取由真实 Evidence 物化的标准化数值。", "chart-line-up");
    return;
  }
  if (state.metricError) {
    target.innerHTML = `<div class="metric-failure" role="alert"><strong>无法加载指标观测</strong><span>${escapeHtml(state.metricError)}</span></div>`;
    return;
  }
  if (!state.metricObservations.length) {
    designedEmpty(target, "还没有指标观测", "导入 Evidence 后运行物化，才会生成可追溯的经营指标。", "chart-line-up");
    return;
  }
  const visible = state.metricObservations.slice(0, 8);
  const summary = state.metricObservations.length > visible.length
    ? `<p class="result-count">显示最近 ${visible.length} 条，共 ${state.metricObservations.length} 条；完整历史可通过 API 分页查看。</p>`
    : "";
  target.innerHTML = summary + visible.map(observation => {
    const name = observation.metric_key || observation.metric_name || observation.name || "未命名指标";
    const source = observation.evidence_import_id || observation.source_evidence_import_id || "—";
    return `<article class="metric-observation-card"><div class="metric-observation-head"><div><p class="kicker">${escapeHtml(observation.platform || "Evidence")}</p><h3>${escapeHtml(name)}</h3></div><strong>${escapeHtml(metricDisplayValue(observation))}</strong></div><dl class="metric-observation-meta"><div><dt>Period / grain</dt><dd>${escapeHtml(metricPeriod(observation))}</dd></div><div><dt>Observed</dt><dd>${escapeHtml(isoLocal(observation.observed_at || observation.created_at))}</dd></div><div><dt>Evidence</dt><dd>${escapeHtml(source)}</dd></div></dl><div class="quality-flags"><span>质量</span>${metricFlags(observation)}</div><div class="row-actions"><button data-action="view-metric-observation" data-id="${escapeHtml(observation.id)}" class="secondary-button">查看来源</button></div></article>`;
  }).join("");
}

function renderMetricMaterializations() {
  const target = $("metric-materialization-list");
  if (!state.apiKey) {
    designedEmpty(target, "尚未连接 Runtime", "物化任务需要已认证的租户会话。", "pulse");
    return;
  }
  if (state.materializationLoading) {
    designedEmpty(target, "正在加载物化任务", "正在读取 Evidence 到指标观测的处理状态。", "pulse");
    return;
  }
  if (state.materializationError) {
    target.innerHTML = `<div class="metric-failure" role="alert"><strong>无法加载物化任务</strong><span>${escapeHtml(state.materializationError)}</span></div>`;
    return;
  }
  if (!state.metricMaterializations.length) {
    designedEmpty(target, "暂无物化任务", "当 Evidence 被送入指标标准化流程后，处理状态会显示在这里。", "pulse");
    return;
  }
  const operator = metricCanMaterialize();
  target.innerHTML = state.metricMaterializations.map(materialization => {
    const status = materializationStatus(materialization);
    const evidenceId = materializationEvidenceId(materialization);
    const error = materialization.error_message || materialization.error_code;
    const retry = status === "failed" ? `<button data-action="retry-metric-materialization" data-evidence-id="${escapeHtml(evidenceId)}" class="primary-button" ${operator && evidenceId ? "" : `disabled title="${escapeHtml(operator ? "缺少 Evidence 标识，无法重试" : "需要 operator、admin 或 owner 角色" )}"`}>重试物化</button>` : "";
    const reason = status === "failed" && !operator ? '<span class="permission-reason">当前角色只能查看；重试物化需要 operator、admin 或 owner。</span>' : "";
    return `<article class="materialization-card"><div class="materialization-head"><div><p class="kicker">Evidence materialization</p><h3>${escapeHtml(evidenceId || "Evidence unavailable")}</h3></div>${badge(status)}</div><dl class="metric-observation-meta"><div><dt>Observations</dt><dd>${escapeHtml(String(materialization.observation_count ?? 0))}</dd></div><div><dt>Quarantined</dt><dd>${escapeHtml(String(materialization.quarantined_count ?? materialization.quarantine_count ?? 0))}</dd></div><div><dt>Updated</dt><dd>${escapeHtml(isoLocal(materialization.updated_at || materialization.completed_at || materialization.created_at))}</dd></div></dl>${error ? `<p class="metric-error">${escapeHtml(error)}</p>` : ""}<div class="row-actions">${retry}</div>${reason}</article>`;
  }).join("");
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
    const review = run.review_status || run.reviewer_status || "pending";
    const reviewerTask = run.reviewer_task || run.reviewer_task_id || (
      run.status === "completed"
        ? `operations_reviewer · completed · ${review}`
        : run.status === "failed"
          ? "Reviewer 未完成；查看详情了解失败阶段"
          : "等待 Reviewer 任务"
    );
    const downstream = review === "approved" ? "" : '<span class="review-guard">未获批准：不可进入下游动作</span>';
    return `<div class="data-row agent-run-row"><div class="data-main"><strong>${escapeHtml(run.objective)}</strong><small>${badge(run.status)}${escapeHtml((run.platforms || []).join(", "))} · Graph ${escapeHtml(run.graph_version_id || "default")} · Review ${escapeHtml(review)} · ${escapeHtml(isoLocal(run.updated_at))}</small><span class="reviewer-task">Reviewer task: ${escapeHtml(reviewerTask)}</span>${downstream}</div><div class="row-actions">${actions.join("")}</div></div>`;
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

function dailyOpsCanManage() { return ["operator", "admin", "owner"].includes(state.me?.role); }
function publishedGraphs() { return state.agentGraphs.flatMap(graph => (graph.versions || []).filter(version => version.status === "published").map(version => ({...version, graph_name: graph.name || graph.id}))); }
function renderDailyOpsOptions() {
  const graph = $("daily-ops-graph"), evidence = $("daily-ops-evidence"), reason = $("daily-ops-permission-reason");
  if (!graph || !evidence) return;
  const versions = publishedGraphs();
  graph.innerHTML = versions.length ? versions.map(item => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.graph_name)} · ${escapeHtml(item.id)}</option>`).join("") : `<option value="">暂无已发布 Graph</option>`;
  const catalogTypes = (state.catalog?.report_types || []).filter(reportType => (
    state.selectedPlatform === "amazon"
      ? reportType === "platform_generic" || reportType.startsWith("amazon_")
      : reportType === "platform_generic"
  ));
  const observedTypes = state.imports.filter(item => (item.platform || item.source_platform) === state.selectedPlatform).map(item => item.report_type).filter(Boolean);
  const reportTypes = [...new Set([...catalogTypes, ...observedTypes])].sort();
  evidence.innerHTML = reportTypes.length ? reportTypes.map(reportType => `<option value="${escapeHtml(reportType)}">${escapeHtml(state.selectedPlatform)} · ${escapeHtml(reportType)}</option>`).join("") : `<option value="">当前平台暂无 Evidence report type</option>`;
  const can = dailyOpsCanManage() && versions.length && reportTypes.length && !state.dailyOpsLoading;
  document.querySelectorAll("#daily-ops-form input, #daily-ops-form select, #daily-ops-form textarea, #daily-ops-form button").forEach(node => { node.disabled = !can; });
  if (!dailyOpsCanManage()) { reason.hidden = false; reason.textContent = "当前角色只能查看；创建 Daily Ops 需要 operator、admin 或 owner。"; }
  else if (state.dailyOpsLoading) { reason.hidden = false; reason.textContent = "Daily Ops 数据加载中。"; }
  else if (!versions.length || !reportTypes.length) { reason.hidden = false; reason.textContent = "需要至少一个已发布 Agent Graph 和当前平台支持的 Evidence report type。"; }
  else reason.hidden = true;
}
function renderDailyOpsSchedules() {
  const target = $("daily-ops-schedule-list"); if (!target) return;
  if (state.dailyOpsLoading) { designedEmpty(target, "正在加载 Daily Ops 计划", "正在读取租户内持久化日历计划。", "calendar-dots"); return; }
  if (state.dailyOpsScheduleError) { target.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>无法加载 Daily Ops 计划</strong><span>${escapeHtml(state.dailyOpsScheduleError)}</span></div>`; return; }
  if (!state.dailyOpsSchedules.length) { designedEmpty(target, "暂无 Daily Ops 计划", "创建后按本地时区触发真实 Daily Ops。", "calendar-dots"); return; }
  const canManage = dailyOpsCanManage();
  target.innerHTML = state.dailyOpsSchedules.map(item => { const disabled = !canManage ? 'disabled title="需要 operator、admin 或 owner 角色"' : ""; const trigger = item.enabled === false ? '<span class="permission-reason">计划已停用</span>' : `<button data-action="trigger-daily-ops" data-id="${escapeHtml(item.id)}" class="secondary-button" ${disabled}>立即触发</button>`; const toggle = `<button data-action="toggle-daily-ops-schedule" data-id="${escapeHtml(item.id)}" data-enabled="${item.enabled ? "false" : "true"}" class="secondary-button" ${disabled}>${item.enabled ? "停用" : "启用"}</button>`; return `<div class="data-row"><div class="data-main"><strong>${escapeHtml(item.name || item.id)}</strong><small>${badge(item.enabled === false ? "disabled" : "enabled")} · ${escapeHtml(item.local_time || "—")} · ${escapeHtml(item.timezone || "—")} · ${escapeHtml(item.platform || "—")} · cursor ${escapeHtml(item.next_local_date || "—")} · max age ${escapeHtml(String(item.max_source_age_hours || "—"))}h</small></div><div class="row-actions">${trigger}${toggle}</div></div>`; }).join("");
}
function renderDailyOpsRuns() {
  const target = $("daily-ops-run-list"); if (!target) return;
  if (state.dailyOpsLoading) { designedEmpty(target, "正在加载 Daily Ops 运行", "正在读取每日运行与持久化 Brief。", "pulse"); return; }
  if (state.dailyOpsRunError) { target.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>无法加载 Daily Ops 运行</strong><span>${escapeHtml(state.dailyOpsRunError)}</span></div>`; return; }
  if (!state.dailyOpsRuns.length) { designedEmpty(target, "暂无 Daily Ops 运行", "计划触发或立即运行后，持久化结果会显示在这里。", "pulse"); return; }
  const canManage = dailyOpsCanManage();
  target.innerHTML = state.dailyOpsRuns.map(run => { const status = run.status || "scheduled"; const review = run.brief?.review_status || (status === "completed" ? "approved" : "pending"); const evidenceCount = Array.isArray(run.selected_evidence_import_ids) ? run.selected_evidence_import_ids.length : 0; const metricCount = Array.isArray(run.selected_metric_observation_ids) ? run.selected_metric_observation_ids.length : 0; const roleDisabled = !canManage ? 'disabled title="需要 operator、admin 或 owner 角色"' : ""; const future = run.scheduled_for && new Date(run.scheduled_for).getTime() > Date.now(); const executeDisabled = !canManage || future ? `disabled title="${escapeHtml(!canManage ? "需要 operator、admin 或 owner 角色" : "尚未到计划执行时间")}"` : ""; const actions = [`<button data-action="view-daily-ops-run" data-id="${escapeHtml(run.id)}" class="secondary-button">详情</button>`]; if (run.brief) actions.push(`<button data-action="view-daily-ops-brief" data-id="${escapeHtml(run.id)}" class="secondary-button">查看 Brief</button>`); if (status === "scheduled") actions.push(`<button data-action="execute-daily-ops" data-id="${escapeHtml(run.id)}" class="primary-button" ${executeDisabled}>执行</button>`); if (["failed", "empty", "blocked"].includes(status)) actions.push(`<button data-action="retry-daily-ops" data-id="${escapeHtml(run.id)}" class="secondary-button" ${roleDisabled}>重试</button>`); const error = run.error_message ? `<span class="review-guard">${escapeHtml(run.error_message)}</span>` : ""; return `<div class="data-row"><div class="data-main"><strong>${escapeHtml(run.local_date || "Daily Ops")}</strong><small>${badge(status)} · ${escapeHtml(run.timezone || "—")} · ${escapeHtml(isoLocal(run.scheduled_for))} · sources ${evidenceCount + metricCount} · Graph ${escapeHtml(run.graph_version_id || "—")} · Reviewer ${escapeHtml(review)}</small>${run.brief ? `<span class="reviewer-task">已持久化 ${escapeHtml(run.brief.status || status)} Brief</span>` : ""}${error}</div><div class="row-actions">${actions.join("")}</div></div>`; }).join("");
}
function renderDailyOps() { renderDailyOpsOptions(); renderDailyOpsSchedules(); renderDailyOpsRuns(); }

function renderApprovals() {
  const target = $("approval-list"), items = state.mission?.approval_inbox || [];
  if (!items.length) {
    designedEmpty(target, "当前没有待审批动作", "当 Agent 提议外部写入、预算或发布动作时，会在这里等待另一位授权用户。", "shield-check");
    return;
  }
  target.innerHTML = items.map(item => approvalCard(item)).join("");
}

function liveStatusCopy() {
  const copies = {
    disconnected: ["未连接", "连接 Runtime 后开始接收租户内的实时状态。"],
    connecting: ["正在连接", "正在建立经过身份验证的实时事件流。"],
    empty: ["实时已连接", "当前还没有新的任务状态事件。"],
    live: ["实时已连接", state.liveLastAt ? `最近更新 ${isoLocal(state.liveLastAt)}` : "正在接收真实任务状态。"],
    reconnecting: ["正在重连", state.liveError || "连接已中断，将从最后游标继续。"],
    error: ["实时连接异常", state.liveError || "无法建立实时事件流。"],
    auth_failed: ["认证已失效", "API Key 已从页面内存清除，请重新连接 Runtime。"],
  };
  return copies[state.liveStatus] || copies.disconnected;
}

function renderLiveMissionControl() {
  const indicator = $("live-indicator"), label = $("live-status-label"), copy = $("live-status-copy");
  const list = $("live-event-list"), retry = $("live-retry-btn");
  const [title, detail] = liveStatusCopy();
  if (indicator) {
    indicator.dataset.status = state.liveStatus;
    indicator.textContent = title;
  }
  if (label) label.textContent = title;
  if (copy) copy.textContent = detail;
  if (retry) retry.hidden = !["error", "reconnecting"].includes(state.liveStatus) || !state.apiKey;
  if (!list) return;
  if (["connecting", "reconnecting"].includes(state.liveStatus) && !state.missionEvents.length) {
    designedEmpty(list, title, detail, "pulse");
    return;
  }
  if (state.liveStatus === "error" && !state.missionEvents.length) {
    list.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>${escapeHtml(title)}</strong><span>${escapeHtml(detail)}</span></div>`;
    return;
  }
  if (!state.missionEvents.length) {
    designedEmpty(list, state.apiKey ? "暂无实时活动" : "Runtime 未连接", detail, "pulse");
    return;
  }
  list.innerHTML = state.missionEvents.slice(0, 20).map(event => `<div class="live-event-row"><span class="live-event-dot ${escapeHtml(event.status || "updated")}"></span><div><strong>${escapeHtml(event.event_type || "mission.update")}</strong><small>${escapeHtml(event.resource_type || "resource")} · ${escapeHtml(event.resource_id || "—")} · ${escapeHtml(event.status || "updated")} · ${escapeHtml(isoLocal(event.occurred_at || event.created_at))}</small></div></div>`).join("");
}

const pilotWorkerLabels = {
  scheduler: "Schedule 调度器",
  job_worker: "Agent Job Worker",
  report_worker: "Amazon Report Worker",
  daily_scheduler: "Daily Ops 调度器",
  daily_worker: "Daily Ops Worker",
  proposal_worker: "Proposal Worker",
};
const pilotComponentLabels = {
  schema: "Runtime Schema",
  amazon_spapi: "Amazon SP-API",
  agent_graph: "Agent Graph",
  daily_ops: "Daily Ops",
  openai: "OpenAI Agent Provider",
  amazon_ads_l5: "Amazon Ads L5（可选）",
};
const pilotBlockerLabels = {
  AMAZON_ACCOUNT_MISSING: "尚未配置 Amazon SP-API 账户",
  AMAZON_ACCOUNT_UNHEALTHY: "Amazon SP-API 账户健康检查未通过",
  AMAZON_ACCOUNT_HEALTH_STALE: "Amazon SP-API 健康检查已过期",
  AMAZON_HEALTH_STALE: "Amazon SP-API 健康检查已过期",
  AMAZON_CREDENTIALS_MISSING: "Amazon 凭证环境变量尚未就绪",
  PUBLISHED_GRAPH_MISSING: "尚无已发布 Agent Graph",
  DAILY_SCHEDULE_MISSING: "尚无启用的 Daily Ops 计划",
  OPENAI_API_KEY_MISSING: "OpenAI API Key 环境变量尚未就绪",
  OPENAI_MODEL_MISSING: "尚未配置 OpenAI 模型",
  PILOT_RUNTIME_NOT_HEALTHY: "Pilot Runtime 当前未健康运行",
  PILOT_RUNTIME_DEGRADED: "至少一个 Pilot Worker 正在降级运行",
  PILOT_RUNTIME_ATTENTION: "Pilot Runtime 正在启动或需要关注",
};

function renderPilotStatus() {
  const summary = $("pilot-runtime-summary"), workersTarget = $("pilot-worker-list"), checksTarget = $("pilot-readiness-list");
  if (!summary || !workersTarget || !checksTarget) return;
  if (state.pilotLoading) {
    designedEmpty(summary, "正在读取 Pilot Runtime", "正在检查持久化心跳与当前租户准备度。", "pulse");
    workersTarget.innerHTML = ""; checksTarget.innerHTML = ""; return;
  }
  if (state.pilotError) {
    summary.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>无法读取 Pilot Runtime</strong><span>${escapeHtml(state.pilotError)}</span></div>`;
    workersTarget.innerHTML = ""; checksTarget.innerHTML = ""; return;
  }
  if (!state.pilotStatus) {
    designedEmpty(summary, "尚无 Pilot 状态", "通过一条 pilot 命令启动后，这里显示真实 Worker 心跳。", "gear-six");
    workersTarget.innerHTML = ""; checksTarget.innerHTML = ""; return;
  }
  const overall = state.pilotStatus.status || "blocked";
  const runtime = state.pilotStatus.runtime || {status: "stopped", workers: []};
  const tenant = state.pilotStatus.tenant || {};
  const blockers = state.pilotStatus.blockers || tenant.blockers || [];
  const warnings = state.pilotStatus.warnings || [];
  const issues = [...blockers, ...warnings];
  summary.innerHTML = `<div class="pilot-summary-head"><div><strong>Commerce Agent Pilot</strong><span>${escapeHtml(tenant.tenant_name || state.me?.tenant_name || "当前租户")}</span></div>${badge(overall)}</div><div class="pilot-summary-meta"><span>Runtime ${escapeHtml(runtime.status || "stopped")}</span><span>Generation ${escapeHtml(runtime.generation ?? "—")}</span><span>Heartbeat ${escapeHtml(isoLocal(runtime.last_heartbeat_at))}</span></div>${issues.length ? `<div class="pilot-blockers">${issues.map(item => `<span>${escapeHtml(pilotBlockerLabels[item.code] || item.code || "未知阻塞")}</span>`).join("")}</div>` : '<div class="pilot-ready-note">运行环境与当前租户已通过 Pilot 检查。</div>'}`;
  const workers = Array.isArray(runtime.workers) ? runtime.workers : [];
  if (!workers.length) designedEmpty(workersTarget, "Pilot Workers 未运行", "启动 `opc-ecommerce pilot` 后，六个 Worker 会在此持续报告心跳。", "gear-six");
  else workersTarget.innerHTML = workers.map(worker => `<div class="pilot-worker-row"><div><strong>${escapeHtml(pilotWorkerLabels[worker.name] || worker.name)}</strong><small>tick ${escapeHtml(worker.iteration_count ?? 0)} · heartbeat ${escapeHtml(isoLocal(worker.last_heartbeat_at))}${worker.last_error_type ? ` · ${escapeHtml(worker.last_error_type)}` : ""}</small></div>${badge(worker.status || "starting")}</div>`).join("");
  const components = tenant.components || {};
  const entries = Object.entries(components);
  if (!entries.length) designedEmpty(checksTarget, "暂无租户检查", "Pilot 会在不读取密钥值的前提下检查真实依赖。", "shield-check");
  else checksTarget.innerHTML = entries.map(([key, component]) => `<div class="pilot-check-row"><div><strong>${escapeHtml(pilotComponentLabels[key] || key)}</strong><small>${component.required === false ? "可选能力" : "Pilot 必需"}</small></div>${badge(component.status || "unknown")}</div>`).join("");
}

function proposalCanCreate() { return ["operator", "admin", "owner"].includes(state.me?.role); }
function proposalCanApprove(item) { return ["admin", "owner"].includes(state.me?.role) && item.created_by !== state.me?.user_id && item.created_by !== state.me?.id; }
const proposalPayloadTemplates = {
  "human.review": {instructions: "复核该 Daily Ops 优先事项，并记录最终经营决定。"},
  "shopify.sync_products": {external_account_id: "", limit: 100},
  "amazon_spapi.import_report": {external_account_id: "", report_id: "", evidence_report_type: "amazon_business_report"},
  "amazon_ads.campaign_update": {external_account_id: "", campaign_id: "", changes: {state: "paused"}},
};
function proposalPayloadTemplate(operation) { return JSON.stringify(proposalPayloadTemplates[operation] || {}, null, 2); }
function setProposalPayloadTemplate() { $("proposal-payload").value = proposalPayloadTemplate($("proposal-operation").value); }
function localDateTimeValue(value) {
  const instant = value ? new Date(value) : new Date();
  return new Date(instant.getTime() - instant.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}
function proposalPriorities(run) { return run?.brief?.report?.priorities || run?.brief?.priorities || []; }
function populateProposalPriorities() {
  const prioritySelect = $("proposal-priority");
  if (!prioritySelect) return;
  const run = state.dailyOpsRuns.find(item => item.id === $("proposal-run")?.value);
  const priorities = proposalPriorities(run);
  prioritySelect.innerHTML = priorities.length
    ? priorities.map((priority, index) => `<option value="${index}">${escapeHtml(priority.title || `Priority ${index + 1}`)}</option>`).join("")
    : '<option value="">暂无优先事项</option>';
}
function renderProposals() {
  const runs = state.dailyOpsRuns.filter(run => ["completed", "approved"].includes(run.status) && proposalPriorities(run).length);
  const runSelect = $("proposal-run"), prioritySelect = $("proposal-priority"), form = $("proposal-form"), reason = $("proposal-permission");
  if (runSelect) {
    const previous = runSelect.value;
    runSelect.innerHTML = runs.length ? runs.map(run => `<option value="${escapeHtml(run.id)}">${escapeHtml(run.local_date || run.id)} · ${escapeHtml(run.id)}</option>`).join("") : '<option value="">暂无已完成 Daily Ops</option>';
    if (runs.some(run => run.id === previous)) runSelect.value = previous;
  }
  if (prioritySelect) populateProposalPriorities();
  const can = proposalCanCreate() && runs.length;
  if (form) form.querySelector("button[type=submit]").disabled = !can;
  if (reason) { reason.hidden = can; reason.textContent = !proposalCanCreate() ? "当前角色只能查看；创建提案需要 operator、admin 或 owner。" : "需要一个已完成且有 priorities 的 Daily Ops 运行。"; }
  const target = $("proposal-list"); if (!target) return;
  if (state.proposalsLoading) { designedEmpty(target, "正在加载提案", "正在读取租户内持久化提案。", "pulse"); return; }
  if (state.proposalsError) { target.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>无法加载提案</strong><span>${escapeHtml(state.proposalsError)}</span></div>`; return; }
  if (!state.proposals.length) { designedEmpty(target, "暂无行动提案", "从已完成的 Daily Ops 优先事项创建第一项提案。", "shield-check"); return; }
  target.innerHTML = state.proposals.map(item => {
    const approval = item.required_approvals ?? 1;
    const current = item.approval_count ?? 0;
    const isCreator = item.created_by === state.me?.user_id || item.created_by === state.me?.id;
    const canDecide = proposalCanApprove(item) && item.status === "submitted";
    const expired = item.status === "expired";
    const capabilityUnavailable = item.capability_status !== "available";
    const canExecute = item.status === "approved" && proposalCanCreate() && !expired && !capabilityUnavailable;
    const canRevise = isCreator && ["draft", "rejected", "revision_required"].includes(item.status);
    const version = Number(item.version || 1);
    const execution = state.proposalExecutions.find(entry => entry.proposal_id === item.id);
    const capabilityNote = capabilityUnavailable
      ? `<span class="review-guard">${escapeHtml(item.capability_reason || "当前平台能力不可用；执行已禁用。")}</span>`
      : expired ? '<span class="review-guard">提案已过期。</span>' : "";
    let decisionControl = "";
    if (item.status === "submitted") {
      decisionControl = canDecide
        ? `<button class="primary-button" data-action="approve-proposal" data-id="${escapeHtml(item.id)}" data-version="${version}">审批</button>`
        : '<button class="primary-button" disabled title="需要 admin/owner，且创建者不能审批自己的提案">审批</button>';
    }
    let executionControl = "";
    if (item.status === "approved") {
      executionControl = canExecute
        ? `<button class="primary-button" data-action="execute-proposal" data-id="${escapeHtml(item.id)}" data-version="${version}">执行</button>`
        : `<button class="primary-button" disabled title="${escapeHtml(item.capability_reason || "当前角色或平台能力不允许执行")}">执行</button>`;
    }
    let retryControl = "";
    if (execution?.status === "failed") {
      retryControl = proposalCanCreate() && !expired && !capabilityUnavailable
        ? `<button class="secondary-button" data-action="retry-proposal" data-id="${escapeHtml(item.id)}" data-version="${version}">重试</button>`
        : `<button class="secondary-button" disabled title="${escapeHtml(expired ? "提案已过期" : item.capability_reason || "重试需要 operator、admin 或 owner")}">重试</button>`;
    }
    return `<article class="data-row proposal-row"><div class="data-main"><strong>${escapeHtml(item.title || operationLabel(item.operation))}</strong><small>${badge(item.status || "draft")} · ${escapeHtml(operationLabel(item.operation))} · 风险 ${escapeHtml(item.risk || "—")} · approvals ${current}/${approval} · expires ${escapeHtml(isoLocal(item.expires_at))}</small><span class="reviewer-task">content ${escapeHtml(item.content_hash || "—")} · payload ${escapeHtml(item.payload_hash || "—")} · Daily ${escapeHtml(item.daily_ops_run_id || "—")} · Agent ${escapeHtml(item.agent_run_id || "—")} · Graph ${escapeHtml(item.graph_version_hash || "—")}</span>${capabilityNote}${execution ? `<span class="reviewer-task">Execution ${escapeHtml(execution.status || "—")} · attempt ${escapeHtml(execution.attempt_count ?? 0)}/${escapeHtml(execution.max_attempts ?? "—")}</span>` : ""}</div><div class="row-actions"><button class="secondary-button" data-action="view-proposal" data-id="${escapeHtml(item.id)}">详情</button>${canRevise ? `<button class="secondary-button" data-action="revise-proposal" data-id="${escapeHtml(item.id)}" data-version="${version}">修订</button>` : ""}${item.status === "draft" && isCreator ? `<button class="primary-button" data-action="submit-proposal" data-id="${escapeHtml(item.id)}" data-version="${version}">提交审批</button>` : ""}${decisionControl}${executionControl}${retryControl}</div></article>`;
  }).join("");
}

function assuranceCanRun() { return ["admin", "owner"].includes(state.me?.role); }
function renderAssurance() {
  const target = $("assurance-list"), reason = $("assurance-permission");
  if (!target) return;
  document.querySelectorAll('[data-action="run-assurance"]').forEach(button => {
    button.disabled = !assuranceCanRun() || state.assuranceLoading;
    button.title = button.disabled ? "需要 admin 或 owner 角色" : "";
  });
  if (reason) {
    reason.hidden = assuranceCanRun();
    reason.textContent = "当前角色只能查看；运行 Assurance 需要 admin 或 owner。";
  }
  if (state.assuranceLoading) { designedEmpty(target, "正在运行 Assurance", "正在执行真实评测与安全完整性检查。", "shield-check"); return; }
  if (state.assuranceError) { target.innerHTML = `<div class="agent-graph-failure" role="alert"><strong>无法读取 Assurance</strong><span>${escapeHtml(state.assuranceError)}</span></div>`; return; }
  if (!state.assuranceRuns.length) { designedEmpty(target, "尚无 Assurance 记录", "运行 Eval 或 Security 后，结果与检查项会持久保留。", "shield-check"); return; }
  target.innerHTML = state.assuranceRuns.map(run => {
    const checks = Array.isArray(run.checks) ? run.checks : [];
    const passed = checks.filter(check => check.status === "passed").length;
    const failure = checks.find(check => ["failed", "blocked"].includes(check.status));
    return `<article class="assurance-card"><div class="assurance-card-head"><div><p class="kicker">${escapeHtml(run.kind || "assurance")}</p><strong>${escapeHtml(run.kind === "restore" ? "恢复演练" : run.kind === "security" ? "安全检查" : "工作流评测")}</strong></div>${badge(run.status || "running")}</div><div class="assurance-meta"><span>${passed}/${checks.length} checks passed</span><span>${escapeHtml(isoLocal(run.completed_at || run.created_at))}</span></div>${failure ? `<div class="review-guard">${escapeHtml(failure.code || "检查未通过")}</div>` : ""}<div class="row-actions"><button data-action="view-assurance" data-id="${escapeHtml(run.id)}" class="secondary-button">查看检查项</button></div></article>`;
  }).join("");
}

function renderAudit() {
  const target = $("audit-list");
  if (!state.audit.length) {
    designedEmpty(target, "暂无审计事件", "Runtime 中的真实操作记录会按时间倒序显示。", "clipboard-text");
    return;
  }
  target.innerHTML = state.audit.slice(0, 100).map(item => `<div class="data-row"><div class="data-main"><strong>${escapeHtml(item.action)}</strong><small>${badge(item.outcome)}${escapeHtml(item.resource_type)} · ${escapeHtml(isoLocal(item.created_at))}</small>${item.event_hash ? `<span class="reviewer-task">chain ${escapeHtml(item.event_hash.slice(0, 16))}… · previous ${escapeHtml((item.previous_hash || "").slice(0, 16))}…</span>` : ""}</div><div class="row-actions"><button data-action="view-json" data-json="${encodeURIComponent(JSON.stringify(item))}" class="secondary-button">查看</button></div></div>`).join("");
}

function renderAll() {
  renderCatalog();
  renderBriefing();
  renderEvidence();
  renderAgentGraphs();
  renderRunMetricOptions();
  renderRuns();
  renderJobs();
  renderSchedules();
  renderDailyOps();
  renderPilotStatus();
  renderLiveMissionControl();
  renderApprovals();
  renderProposals();
  renderAssurance();
  renderAudit();
  renderConnectors();
  renderReportRecipes();
  renderReportSyncs();
  renderMetricObservations();
  renderMetricMaterializations();
  renderAdsCapabilityGates();
  renderAdsAdapterStatus();
}

function renderDisconnected() {
  state.briefing = null;
  state.imports = [];
  state.runs = [];
  state.jobs = [];
  state.schedules = [];
  state.dailyOpsSchedules = []; state.dailyOpsRuns = []; state.dailyOpsLoading = false;
  state.dailyOpsScheduleError = null; state.dailyOpsRunError = null;
  state.mission = null;
  state.audit = [];
  state.connectors = [];
  state.reportRecipes = [];
  state.recipeLoading = false;
  state.recipeError = null;
  state.reportSyncs = [];
  state.syncLoading = false;
  state.syncError = null;
  state.metricObservations = [];
  state.metricMaterializations = [];
  state.metricLoading = false;
  state.metricError = null;
  state.materializationLoading = false;
  state.materializationError = null;
  state.adsCapabilityGates = [];
  state.adsCapabilityLoading = false;
  state.adsCapabilityError = null;
  state.adsAdapterStatus = null; state.adsAdapterLoading = false; state.adsAdapterError = null;
  state.proposals = []; state.proposalExecutions = []; state.proposalsLoading = false; state.proposalsError = null;
  state.missionEvents = []; state.liveCursor = null; state.liveLastAt = null;
  state.pilotStatus = null; state.pilotLoading = false; state.pilotError = null;
  state.assuranceRuns = []; state.assuranceLoading = false; state.assuranceError = null;
  if (state.liveStatus !== "auth_failed") { state.liveStatus = "disconnected"; state.liveError = null; }
  state.agentGraphs = []; state.agentGraphsLoading = false; state.agentGraphsError = null;
  renderBriefing();
  renderDailyOps();
  renderPilotStatus();
  renderLiveMissionControl();
  renderProposals();
  renderAssurance();
  renderEvidence();
  renderAgentGraphs();
  renderRunMetricOptions();
  renderRuns();
  renderJobs();
  renderSchedules();
  renderApprovals();
  renderAudit();
  renderConnectors();
  renderReportRecipes();
  renderReportSyncs();
  renderMetricObservations();
  renderMetricMaterializations();
  renderAdsCapabilityGates();
  renderAdsAdapterStatus();
}

async function refreshAll() {
  if (!state.apiKey) return;
  state.recipeLoading = true;
  state.recipeError = null;
  state.syncLoading = true;
  state.syncError = null;
  state.metricLoading = true;
  state.metricError = null;
  state.materializationLoading = true;
  state.materializationError = null;
  state.adsCapabilityLoading = true;
  state.adsCapabilityError = null;
  state.adsAdapterLoading = true; state.adsAdapterError = null;
  state.agentGraphsLoading = true; state.agentGraphsError = null;
  state.dailyOpsLoading = true; state.dailyOpsScheduleError = null; state.dailyOpsRunError = null;
  state.proposalsLoading = true; state.proposalsError = null;
  state.pilotLoading = true; state.pilotError = null;
  state.assuranceLoading = true; state.assuranceError = null;
  renderReportRecipes();
  renderReportSyncs();
  renderMetricObservations();
  renderMetricMaterializations();
  renderAdsCapabilityGates();
  renderAdsAdapterStatus();
  renderAgentGraphs();
  renderRunMetricOptions();
  renderDailyOps();
  renderPilotStatus();
  renderProposals();
  renderAssurance();
  const platform = encodeURIComponent(state.selectedPlatform);
  const recipes = api("/v1/report-recipes").then(value => ({value})).catch(error => ({error}));
  const syncs = api("/v1/report-syncs").then(value => ({value})).catch(error => ({error}));
  const observations = api("/v1/metric-observations").then(value => ({value})).catch(error => ({error}));
  const materializations = api("/v1/metric-materializations").then(value => ({value})).catch(error => ({error}));
  const adsGates = api("/v1/ads-capability-gates").then(value => ({value})).catch(error => ({error}));
  const adsAdapter = api("/v1/ads-adapter-status").then(value => ({value})).catch(error => ({error}));
  const dailyOpsSchedules = api("/v1/daily-ops-schedules").then(value => ({value})).catch(error => ({error}));
  const dailyOpsRuns = api("/v1/daily-ops-runs?limit=100").then(value => ({value})).catch(error => ({error}));
  const proposals = api("/v1/proposals?limit=100").then(value => ({value})).catch(error => ({error}));
  const proposalExecutions = api("/v1/proposal-executions?limit=100").then(value => ({value})).catch(error => ({error}));
  const pilot = api("/v1/pilot-status").then(value => ({value})).catch(error => ({error}));
  const assurance = api("/v1/assurance-runs?limit=100").then(value => ({value})).catch(error => ({error}));
  const graphs = api("/v1/agent-graphs").then(async value => {
    const listed = Array.isArray(value) ? value : value?.graphs || [];
    const detailed = await Promise.all(listed.map(async graph => {
      const id = graph.id || graph.graph_id;
      if (!id) return graph;
      try {
        const bundle = await api(`/v1/agent-graphs/${id}`);
        return bundle.graph ? {...graph, ...bundle.graph, versions: bundle.versions || []} : bundle;
      } catch (error) {
        console.error("Agent Graph 详情加载失败", error);
        return graph;
      }
    }));
    return {graphs: detailed};
  }).then(value => ({value})).catch(error => ({error}));
  const [me, catalog, briefing, mission, imports, runs, jobs, schedules, audit, connectors, recipeResult, syncResult, observationResult, materializationResult, adsGateResult, adsAdapterResult, graphResult, dailyScheduleResult, dailyRunResult, proposalResult, executionResult, pilotResult, assuranceResult] = await Promise.all([
    api("/v1/me"), api("/v1/catalog"), api(`/v1/briefing?platform=${platform}`), api("/v1/mission-control"),
    api("/v1/evidence-imports?limit=100"), api("/v1/agent-runs?limit=100"), api("/v1/jobs?limit=100"),
    api("/v1/schedules"), api("/v1/audit?limit=100"), api("/v1/connectors"), recipes, syncs, observations, materializations, adsGates, adsAdapter, graphs, dailyOpsSchedules, dailyOpsRuns, proposals, proposalExecutions, pilot, assurance,
  ]);
  if (recipeResult.error) console.error("Report Recipes 加载失败", recipeResult.error);
  if (syncResult.error) console.error("Sync Activity 加载失败", syncResult.error);
  if (observationResult.error) console.error("Metric Observations 加载失败", observationResult.error);
  if (materializationResult.error) console.error("Metric materializations 加载失败", materializationResult.error);
  if (adsGateResult.error) console.error("Amazon Ads 准入状态加载失败", adsGateResult.error);
  if (graphResult.error) console.error("Agent Graphs 加载失败", graphResult.error);
  if (dailyScheduleResult.error) console.error("Daily Ops 计划加载失败", dailyScheduleResult.error);
  if (dailyRunResult.error) console.error("Daily Ops 运行加载失败", dailyRunResult.error);
  if (proposalResult.error) console.error("行动提案加载失败", proposalResult.error);
  if (executionResult.error) console.error("提案执行记录加载失败", executionResult.error);
  if (pilotResult.error) console.error("Pilot Runtime 状态加载失败", pilotResult.error);
  if (assuranceResult.error) console.error("Assurance 状态加载失败", assuranceResult.error);
  Object.assign(state, {
    me, catalog, briefing, mission,
    imports: imports.imports || [], runs: runs.runs || [], jobs: jobs.jobs || [],
    schedules: schedules.schedules || [], audit: audit.events || [], connectors: connectors.connectors || [],
    reportRecipes: Array.isArray(recipeResult.value) ? recipeResult.value : recipeResult.value?.report_recipes || recipeResult.value?.recipes || [],
    recipeLoading: false, recipeError: recipeResult.error?.message || null,
    reportSyncs: Array.isArray(syncResult.value) ? syncResult.value : syncResult.value?.report_syncs || syncResult.value?.syncs || [],
    syncLoading: false, syncError: syncResult.error?.message || null,
    metricObservations: Array.isArray(observationResult.value) ? observationResult.value : observationResult.value?.metric_observations || observationResult.value?.observations || [],
    metricLoading: false, metricError: observationResult.error?.message || null,
    metricMaterializations: Array.isArray(materializationResult.value) ? materializationResult.value : materializationResult.value?.metric_materializations || materializationResult.value?.materializations || [],
    materializationLoading: false, materializationError: materializationResult.error?.message || null,
    adsCapabilityGates: Array.isArray(adsGateResult.value) ? adsGateResult.value : adsGateResult.value?.ads_capability_gates || adsGateResult.value?.gates || [],
    adsCapabilityLoading: false, adsCapabilityError: adsGateResult.error?.message || null,
    adsAdapterStatus: adsAdapterResult?.value || null, adsAdapterLoading: false, adsAdapterError: adsAdapterResult?.error?.message || null,
    agentGraphs: Array.isArray(graphResult.value) ? graphResult.value : graphResult.value?.graphs || [], agentGraphsLoading: false, agentGraphsError: graphResult.error?.message || null,
    dailyOpsSchedules: Array.isArray(dailyScheduleResult.value) ? dailyScheduleResult.value : dailyScheduleResult.value?.daily_ops_schedules || dailyScheduleResult.value?.schedules || [],
    dailyOpsRuns: Array.isArray(dailyRunResult.value) ? dailyRunResult.value : dailyRunResult.value?.daily_ops_runs || dailyRunResult.value?.runs || [], dailyOpsLoading: false,
    dailyOpsScheduleError: dailyScheduleResult.error?.message || null,
    dailyOpsRunError: dailyRunResult.error?.message || null,
    proposals: Array.isArray(proposalResult.value) ? proposalResult.value : proposalResult.value?.proposals || [], proposalsLoading: false, proposalsError: proposalResult.error?.message || executionResult.error?.message || null,
    proposalExecutions: Array.isArray(executionResult.value) ? executionResult.value : executionResult.value?.executions || [],
    pilotStatus: pilotResult.value || null, pilotLoading: false, pilotError: pilotResult.error?.message || null,
    assuranceRuns: Array.isArray(assuranceResult.value) ? assuranceResult.value : assuranceResult.value?.runs || [], assuranceLoading: false, assuranceError: assuranceResult.error?.message || null,
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

async function refreshPilotStatus() {
  state.pilotLoading = true;
  state.pilotError = null;
  renderPilotStatus();
  try {
    state.pilotStatus = await api("/v1/pilot-status");
  } catch (error) {
    state.pilotStatus = null;
    state.pilotError = error.message;
    throw error;
  } finally {
    state.pilotLoading = false;
    renderPilotStatus();
  }
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

function liveCursorStorageKey() {
  return state.me?.tenant_id ? `commerce-agent:mission-cursor:${state.me.tenant_id}` : null;
}

function loadLiveCursor() {
  const key = liveCursorStorageKey();
  if (!key) return null;
  try {
    const value = sessionStorage.getItem(key);
    return value !== null && /^\d+$/.test(value) ? Number(value) : null;
  } catch (error) {
    console.warn("实时游标读取失败", error);
    return null;
  }
}

function rememberLiveCursor(cursor) {
  if (!Number.isSafeInteger(cursor) || cursor < 0) return;
  state.liveCursor = cursor;
  const key = liveCursorStorageKey();
  if (!key) return;
  try { sessionStorage.setItem(key, String(cursor)); }
  catch (error) { console.warn("实时游标保存失败", error); }
}

function clearLiveCursor() {
  const key = liveCursorStorageKey();
  state.liveCursor = null;
  if (!key) return;
  try { sessionStorage.removeItem(key); }
  catch (error) { console.warn("实时游标清理失败", error); }
}

function scheduleLiveRefresh() {
  if (state.liveRefreshTimer || !state.apiKey) return;
  state.liveRefreshTimer = setTimeout(() => {
    state.liveRefreshTimer = null;
    refreshAll().catch(error => {
      state.liveError = error.message;
      renderLiveMissionControl();
      notice(error.message, "error");
    });
  }, 350);
}

function handleMissionEvent(frame) {
  if (frame.id !== null) rememberLiveCursor(frame.id);
  const payload = {...(frame.data || {}), sequence: frame.data?.sequence ?? frame.id};
  const isUpdate = frame.event === "mission.update" || (!frame.event.startsWith("mission") && frame.event !== "message");
  if (isUpdate) {
    state.missionEvents = [payload, ...state.missionEvents.filter(item => item.sequence !== payload.sequence)].slice(0, 50);
    state.liveStatus = "live";
    state.liveError = null;
    state.liveLastAt = payload.occurred_at || new Date().toISOString();
    scheduleLiveRefresh();
  } else if (["mission.reset", "mission_control.reset"].includes(frame.event)) {
    state.missionEvents = [];
    state.liveStatus = "empty";
    state.liveError = payload.reason || "历史实时游标已过期，已从当前状态重新同步。";
    scheduleLiveRefresh();
  } else if (["mission.reconnect", "mission_control.reconnect"].includes(frame.event)) {
    state.liveStatus = "reconnecting";
    const reasons = {
      lifetime_limit: "实时连接正在按安全周期轮换，并从最后游标继续。",
      backlog_limit: "待发送事件较多，正在分批从最后游标继续。",
    };
    state.liveError = reasons[payload.reason] || "服务端要求从最后游标重新连接。";
    if (Number.isFinite(Number(payload.retry_after_seconds))) {
      state.liveServerRetryMs = Math.max(1000, Number(payload.retry_after_seconds) * 1000);
    }
  }
  renderLiveMissionControl();
}

async function consumeMissionStream(body) {
  if (!body?.getReader) throw new Error("浏览器不支持经过身份验证的实时流读取");
  const reader = body.getReader(), decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const {done, value} = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), {stream: !done});
    buffer = buffer.replaceAll("\r\n", "\n");
    if (done) buffer = buffer.replaceAll("\r", "\n");
    if (buffer.length > 1_000_000) throw new Error("实时事件帧超过浏览器安全上限");
    let boundary;
    while ((boundary = buffer.indexOf("\n\n")) >= 0) {
      const raw = buffer.slice(0, boundary); buffer = buffer.slice(boundary + 2);
      let event = "message", id = null; const data = [];
      for (const line of raw.split("\n")) {
        if (!line || line.startsWith(":")) continue;
        const split = line.indexOf(":");
        const field = split < 0 ? line : line.slice(0, split);
        const content = split < 0 ? "" : line.slice(split + 1).replace(/^ /, "");
        if (field === "event") event = content;
        else if (field === "id" && /^\d+$/.test(content)) id = Number(content);
        else if (field === "data") data.push(content);
      }
      if (data.length) {
        let parsed;
        try { parsed = JSON.parse(data.join("\n")); }
        catch { throw new Error("Runtime 返回了无效的实时事件 JSON"); }
        handleMissionEvent({event, id, data: parsed});
      }
    }
    if (done) break;
  }
}

function scheduleLiveReconnect(delayMs = null) {
  if (state.liveStopped || !state.apiKey || document.hidden || state.liveRetryTimer) return;
  state.liveAttempt += 1;
  const computed = Math.min(15000, 500 * (2 ** Math.min(state.liveAttempt - 1, 5))) + Math.floor(Math.random() * 250);
  const delay = delayMs ?? computed;
  state.liveStatus = state.liveAttempt >= 5 ? "error" : "reconnecting";
  renderLiveMissionControl();
  state.liveRetryTimer = setTimeout(() => {
    state.liveRetryTimer = null;
    void startLiveStream();
  }, delay);
}

async function startLiveStream() {
  if (state.liveStopped || !state.apiKey || !state.me || document.hidden || state.liveAbort) return;
  state.liveStatus = state.liveAttempt ? "reconnecting" : "connecting";
  state.liveError = null;
  renderLiveMissionControl();
  const controller = new AbortController();
  state.liveAbort = controller;
  const headers = {Authorization: `Bearer ${state.apiKey}`, Accept: "text/event-stream"};
  if (Number.isSafeInteger(state.liveCursor)) headers["Last-Event-ID"] = String(state.liveCursor);
  let retryDelay = null;
  state.liveServerRetryMs = null;
  try {
    const response = await fetch("/v1/mission-control/events", {headers, cache: "no-store", signal: controller.signal});
    if ([401, 403].includes(response.status)) {
      stopPolling();
      state.apiKey = "";
      state.me = null;
      state.liveStatus = "auth_failed";
      state.liveError = "实时连接认证失败";
      setConnected(false);
      renderDisconnected();
      renderLiveMissionControl();
      notice("Runtime 认证已失效，请重新连接。", "error");
      return;
    }
    if (response.status === 422) {
      clearLiveCursor();
      throw new Error("实时游标无效，已清理并准备重新同步");
    }
    if (response.status === 429) {
      const retrySeconds = Number(response.headers.get("Retry-After"));
      retryDelay = Number.isFinite(retrySeconds) ? Math.max(1000, retrySeconds * 1000) : 5000;
      throw new Error("实时连接数已达上限");
    }
    if (!response.ok) throw new Error(`实时事件流请求失败 (${response.status})`);
    if (!(response.headers.get("Content-Type") || "").includes("text/event-stream")) throw new Error("Runtime 未返回 text/event-stream");
    state.liveAttempt = 0;
    state.liveStatus = state.missionEvents.length ? "live" : "empty";
    renderLiveMissionControl();
    await consumeMissionStream(response.body);
  } catch (error) {
    if (error.name !== "AbortError") {
      state.liveError = error.message;
      state.liveStatus = "reconnecting";
      renderLiveMissionControl();
    }
  } finally {
    const wasCurrent = state.liveAbort === controller;
    if (wasCurrent) state.liveAbort = null;
    if (wasCurrent && !state.liveStopped && state.apiKey && !document.hidden) {
      const serverDelay = state.liveServerRetryMs;
      state.liveServerRetryMs = null;
      scheduleLiveReconnect(retryDelay ?? serverDelay);
    }
  }
}

function retryLiveStream() {
  if (!state.apiKey) { notice("请先连接 Runtime。", "error"); return; }
  if (state.liveRetryTimer) clearTimeout(state.liveRetryTimer);
  state.liveRetryTimer = null;
  if (state.liveAbort) state.liveAbort.abort();
  state.liveAbort = null;
  state.liveAttempt = 0;
  state.liveError = null;
  state.liveStopped = false;
  void startLiveStream();
}

function startPolling() {
  stopPolling();
  state.liveStopped = false;
  state.liveCursor = loadLiveCursor();
  state.timer = setInterval(() => refreshAll().catch(error => notice(error.message, "error")), 300000);
  void startLiveStream();
}

function stopPolling() {
  state.liveStopped = true;
  if (state.timer) clearInterval(state.timer);
  if (state.liveRetryTimer) clearTimeout(state.liveRetryTimer);
  if (state.liveRefreshTimer) clearTimeout(state.liveRefreshTimer);
  if (state.liveAbort) state.liveAbort.abort();
  state.timer = null;
  state.liveRetryTimer = null;
  state.liveRefreshTimer = null;
  state.liveAbort = null;
}

function pauseLiveStream() {
  if (state.liveRetryTimer) clearTimeout(state.liveRetryTimer);
  state.liveRetryTimer = null;
  const active = state.liveAbort;
  state.liveAbort = null;
  if (active) active.abort();
  if (!state.liveStopped && state.apiKey) {
    state.liveStatus = "reconnecting";
    state.liveError = "页面暂停后将从最后游标继续。";
    renderLiveMissionControl();
  }
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
    case "refresh-pilot": act(button, refreshPilotStatus, "Pilot Runtime 状态已刷新。", false); break;
    case "retry-live": retryLiveStream(); break;
    case "connect": connect(button); break;
    case "disconnect": disconnect(); break;
    case "select-platform": selectPlatform(button); break;
    case "select-metric": state.chartMetric = button.dataset.metric; renderChartControls(); break;
    case "view-priority": showDetail("Agent Brief", {run_id: state.briefing?.brief_run_id, priority: state.briefing?.priorities?.[Number(button.dataset.index)]}); break;
    case "view-json": showDetail("审计事件", JSON.parse(decodeURIComponent(button.dataset.json))); break;
    case "view-assurance": act(button, async () => showDetail("Assurance 检查项", await api(`/v1/assurance-runs/${id}`)), "Assurance 详情已加载。", false); break;
    case "run-assurance": {
      const kind = button.dataset.kind;
      if (!assuranceCanRun()) { notice("运行 Assurance 需要 admin 或 owner。", "error"); break; }
      if (!["eval", "security"].includes(kind)) { notice("不支持的 Assurance 类型。", "error"); break; }
      act(button, async () => {
        state.assuranceLoading = true; renderAssurance();
        try {
          await api("/v1/assurance-runs", {method: "POST", headers: {"Idempotency-Key": idempotency(`ui-assurance-${kind}`)}, json: {kind}});
        } finally {
          state.assuranceLoading = false;
          renderAssurance();
        }
      }, kind === "eval" ? "工作流评测已保存。" : "安全检查已保存。");
      break;
    }
    case "view-import": act(button, async () => showDetail("Evidence Import", await api(`/v1/evidence-imports/${id}`)), "Evidence 详情已加载。", false); break;
    case "view-job": act(button, async () => showDetail("Job", await api(`/v1/jobs/${id}`)), "Job 详情已加载。", false); break;
    case "view-action": showDetail("待审批 Action", (state.mission?.approval_inbox || []).find(item => item.id === id) || (state.briefing?.approvals || []).find(item => item.id === id)); break;
    case "view-run": act(button, async () => { const bundle = await api(`/v1/agent-runs/${id}`); const tasks = bundle.tasks || []; const reviewerTask = tasks.find(task => ["reviewer", "review"].some(term => String(task.agent_name || task.agent || task.name || "").toLowerCase().includes(term))) || null; showDetail("Agent Run", {run: bundle.run, graph_version_id: bundle.run?.graph_version_id, review_status: bundle.run?.review_status || bundle.run?.reviewer_status, reviewer_task: reviewerTask, tasks, evaluations: bundle.evaluations, report: latestReport(bundle)}); }, "Agent Run 详情已加载。", false); break;
    case "execute-run": act(button, () => api(`/v1/agent-runs/${id}/execute`, {method: "POST"}), "Agent Run 已完成。"); break;
    case "view-daily-ops-run": act(button, async () => showDetail("Daily Ops 运行", await api(`/v1/daily-ops-runs/${id}`)), "Daily Ops 详情已加载。", false); break;
    case "view-daily-ops-brief": act(button, async () => showDetail("Daily Ops Brief", await api(`/v1/daily-ops-runs/${id}/brief`)), "Daily Ops Brief 已加载。", false); break;
    case "trigger-daily-ops": act(button, () => api(`/v1/daily-ops-schedules/${id}/trigger`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-daily-ops-trigger")}}), "Daily Ops 已触发。"); break;
    case "execute-daily-ops": act(button, () => api(`/v1/daily-ops-runs/${id}/execute`, {method: "POST"}), "Daily Ops 已执行。"); break;
    case "retry-daily-ops": act(button, () => api(`/v1/daily-ops-runs/${id}/retry`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-daily-ops-retry")}}), "Daily Ops 已重试。"); break;
    case "toggle-daily-ops-schedule": { const item = state.dailyOpsSchedules.find(schedule => schedule.id === id); if (!item) { notice("Daily Ops 计划不存在", "error"); break; } act(button, () => api(`/v1/daily-ops-schedules/${id}`, {method: "PATCH", json: {name: item.name, platform: item.platform, objective: item.objective, timezone_name: item.timezone, local_time: item.local_time, graph_version_id: item.graph_version_id, evidence_selectors: item.evidence_selectors, max_source_age_hours: item.max_source_age_hours, enabled: button.dataset.enabled === "true"}}), button.dataset.enabled === "true" ? "Daily Ops 计划已启用。" : "Daily Ops 计划已停用。"); break; }
    case "queue-run": act(button, () => api("/v1/jobs", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-job")}, json: {run_id: id, max_attempts: 3}}), "Run 已加入后台队列。"); break;
    case "evaluate-run": act(button, () => api(`/v1/agent-runs/${id}/evaluate`, {method: "POST"}), "Evaluation 已保存。"); break;
    case "approve-action": act(button, () => api(`/v1/actions/${id}/approve`, {method: "POST"}), "Action 已批准；仍需 Operator 执行。"); break;
    case "view-proposal": act(button, async () => showDetail("行动提案", await api(`/v1/proposals/${id}`)), "提案详情已加载。", false); break;
    case "submit-proposal": act(button, () => api(`/v1/proposals/${id}/submit`, {method: "POST", json: {expected_version: Number(button.dataset.version)}}), "提案已提交审批。"); break;
    case "approve-proposal": $("proposal-decision-form").reset(); $("proposal-decision-id").value=id; $("proposal-decision-version").value=button.dataset.version; $("proposal-decision").value="approve"; $("proposal-decision-dialog").showModal(); break;
    case "reject-proposal": $("proposal-decision-form").reset(); $("proposal-decision-id").value=id; $("proposal-decision-version").value=button.dataset.version; $("proposal-decision").value="reject"; $("proposal-decision-dialog").showModal(); break;
    case "revise-proposal": {
      const proposal = state.proposals.find(item => item.id === id);
      if (!proposal) { notice("提案不存在，请刷新后重试。", "error"); break; }
      $("proposal-revision-id").value = id;
      $("proposal-revision-version").value = button.dataset.version;
      $("proposal-revision-title").value = proposal.title || "";
      $("proposal-revision-rationale").value = proposal.rationale || "";
      $("proposal-revision-impact").value = proposal.expected_impact || "";
      $("proposal-revision-rollback").value = proposal.rollback_plan || "";
      $("proposal-revision-operation").value = proposal.operation;
      $("proposal-revision-risk").value = proposal.risk;
      $("proposal-revision-expires").value = localDateTimeValue(proposal.expires_at);
      $("proposal-revision-payload").value = JSON.stringify(proposal.payload || {}, null, 2);
      $("proposal-revision-dialog").showModal();
      break;
    }
    case "execute-proposal": act(button, () => api(`/v1/proposals/${id}/execute`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-proposal-execute")}, json: {expected_version: Number(button.dataset.version)}}), "提案已提交执行。"); break;
    case "retry-proposal": act(button, () => api(`/v1/proposals/${id}/retry`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-proposal-retry")}, json: {expected_version: Number(button.dataset.version)}}), "提案执行已重试。"); break;
    case "toggle-schedule": act(button, () => api(`/v1/schedules/${id}`, {method: "PATCH", json: {enabled: button.dataset.enabled === "true"}}), "Schedule 状态已更新。"); break;
    case "open-connector-form": openConnectorForm(); break;
    case "edit-connector": openConnectorForm(state.connectors.find(item => item.id === id)); break;
    case "health-check-connector": act(button, () => api(`/v1/connectors/${id}/health-check`, {method: "POST"}), "健康检查已完成。"); break;
    case "open-ads-capability-form": openAdsCapabilityForm(id); break;
    case "view-ads-capability-gate": act(button, async () => showDetail("Amazon Ads 准入检查", await api(`/v1/ads-capability-gates/${id}`)), "准入详情已加载。", false); break;
    case "open-recipe-form": openRecipeForm(); break;
    case "edit-recipe": openRecipeForm(state.reportRecipes.find(item => item.id === id)); break;
    case "enqueue-report-sync": {
      const recipe = state.reportRecipes.find(item => item.id === id);
      const availability = recipe ? recipeSyncAvailability(recipe) : {enabled: false, reason: "Report Recipe 不可用，无法排队同步。"};
      if (!availability.enabled) { notice(availability.reason, "error"); break; }
      act(button, () => api(`/v1/report-recipes/${id}/sync`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-report-sync")}}), "Sync 已排队；L3 Worker 将在后台执行和轮询。");
      break;
    }
    case "view-report-sync": act(button, async () => showDetail("Report Sync", await api(`/v1/report-syncs/${id}`)), "Sync 详情已加载。", false); break;
    case "materialize-evidence-metrics": {
      if (!metricCanMaterialize()) { notice("需要 operator、admin 或 owner 角色", "error"); break; }
      const imported = state.imports.find(item => item.id === id);
      if (!(state.catalog?.metric_materialization_report_types || []).includes(imported?.report_type)) { notice("该报告类型尚无指标映射。", "error"); break; }
      act(button, () => api(`/v1/evidence-imports/${id}/metric-materialization`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-metric-materialization")}}), "指标物化结果已刷新。", true);
      break;
    }
    case "view-metric-observation": act(button, async () => {
      const observation = await api(`/v1/metric-observations/${id}`);
      const record = observation.metric_observation || observation.observation || observation;
      const evidenceId = record.evidence_import_id;
      const evidence = evidenceId ? await api(`/v1/evidence-imports/${evidenceId}`) : null;
      const reportSync = state.reportSyncs.find(sync => sync.evidence_import_id === evidenceId) || null;
      showDetail("Metric 来源与质量", {metric_observation: record, evidence_import: evidence, report_sync: reportSync});
    }, "指标来源已加载。", false); break;
    case "retry-metric-materialization": {
      const evidenceId = button.dataset.evidenceId;
      if (!metricCanMaterialize()) { notice("需要 operator、admin 或 owner 角色", "error"); break; }
      if (!evidenceId) { notice("缺少 Evidence 标识，无法重试物化。", "error"); break; }
      act(button, () => api(`/v1/evidence-imports/${evidenceId}/metric-materialization`, {method: "POST", headers: {"Idempotency-Key": idempotency("ui-metric-materialization")}}), "指标物化结果已刷新。", true);
      break;
    }
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
$("recipe-connector-account").addEventListener("change", () => renderRecipeMarketplaces());

$("recipe-form").addEventListener("submit", event => {
  event.preventDefault();
  const button = event.submitter;
  if (!recipeCanManage()) { notice("需要 operator、admin 或 owner 角色", "error"); return; }
  const connectorAccountId = $("recipe-connector-account").value;
  const type = reportRecipeTypes().find(item => item.key === $("recipe-type").value);
  const marketplaceIds = [...document.querySelectorAll('input[name="recipe-marketplace"]:checked')].map(node => node.value);
  const allowed = new Set(recipeAccountMarketplaces(state.connectors.find(item => item.id === connectorAccountId)).map(item => item.id));
  const name = $("recipe-name").value.trim();
  const intervalMinutes = Number($("recipe-interval").value);
  const lookbackDays = Number($("recipe-lookback").value);
  const nextRun = $("recipe-next-run").value;
  if (!connectorAccountId || !type || !name || !marketplaceIds.length || marketplaceIds.some(id => !allowed.has(id)) || !Number.isInteger(intervalMinutes) || intervalMinutes < 60 || !Number.isInteger(lookbackDays) || lookbackDays < 1 || lookbackDays > 30 || !nextRun) {
    notice("请完成 Recipe 配置；marketplace 必须属于所选 Amazon account。", "error"); return;
  }
  const payload = {
    name,
    recipe_key: type.key,
    marketplace_ids: marketplaceIds,
    interval_minutes: intervalMinutes,
    lookback_days: lookbackDays,
    enabled: $("recipe-enabled").checked,
    next_run_at: new Date(nextRun).toISOString(),
  };
  const recipeId = $("recipe-id").value;
  act(button, async () => {
    const json = recipeId ? payload : {connector_account_id: connectorAccountId, ...payload};
    await api(recipeId ? `/v1/report-recipes/${recipeId}` : "/v1/report-recipes", {method: recipeId ? "PATCH" : "POST", json});
    $("recipe-dialog").close();
  }, recipeId ? "Report Recipe 已更新。" : "Report Recipe 已创建。");
});

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
  } : provider === "amazon_ads" ? {
    region: $("amazon-ads-region").value.trim(),
    profile_id: $("amazon-ads-profile-id").value.trim(),
    lwa_client_id_ref: $("amazon-ads-lwa-client-id-ref").value.trim(),
    lwa_client_secret_ref: $("amazon-ads-lwa-client-secret-ref").value.trim(),
    lwa_refresh_token_ref: $("amazon-ads-refresh-token-ref").value.trim(),
  } : {
    shop_domain: $("shopify-domain").value.trim(),
    api_version: $("shopify-api-version").value.trim(),
    credential_ref: $("shopify-access-token-ref").value.trim(),
  };
  if (!externalAccountId || (provider === "amazon_spapi" && (!config.region || !config.marketplace_ids.length || !config.lwa_client_id_ref || !config.lwa_client_secret_ref || !config.lwa_refresh_token_ref)) || (provider === "amazon_ads" && (!config.region || !config.profile_id || !config.lwa_client_id_ref || !config.lwa_client_secret_ref || !config.lwa_refresh_token_ref)) || (provider === "shopify" && (!config.shop_domain || !config.api_version || !config.credential_ref))) {
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

$("ads-capability-form").addEventListener("submit", event => {
  event.preventDefault();
  const button = event.submitter;
  if (!adsCapabilityCanRun()) { notice("需要 admin 或 owner 角色", "error"); return; }
  const connectorAccountId = $("ads-capability-account").value;
  if (!connectorAccountId || !amazonAdsAccounts().some(account => account.id === connectorAccountId)) { notice("请选择有效的 Amazon Ads 账户。", "error"); return; }
  const attestationReference = $("ads-capability-attestation-reference").value.trim();
  act(button, async () => {
    await api("/v1/ads-capability-gates", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-ads-capability")}, json: {connector_account_id: connectorAccountId, ...(attestationReference ? {attestation_reference: attestationReference} : {})}});
    $("ads-capability-dialog").close();
  }, "Amazon Ads 准入结果已保存。", true);
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
  if (!runCanCreate()) { notice("需要 operator、admin 或 owner 角色", "error"); return; }
  const evidenceIds = [...document.querySelectorAll('input[name="run-evidence"]:checked')].map(node => node.value);
  const metricObservationIds = [...document.querySelectorAll('input[name="run-metric-observation"]:checked')].map(node => node.value);
  const graphVersionId = document.querySelector('input[name="run-graph-version"]:checked')?.value;
  if (!graphVersionId) { notice("请选择一个已发布协作图", "error"); return; }
  if (!evidenceIds.length && !metricObservationIds.length) { notice("至少选择 Evidence 或 Metric Observation 中的一类输入", "error"); return; }
  const inputs = {...(evidenceIds.length ? {evidence_import_ids: evidenceIds} : {}), ...(metricObservationIds.length ? {metric_observation_ids: metricObservationIds} : {})};
  act(event.submitter, () => api("/v1/agent-runs", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-run")}, json: {workflow: "weekly_ops", objective: $("run-objective").value.trim(), graph_version_id: graphVersionId, ...inputs}}), "Agent Run 已创建。");
});

$("schedule-form").addEventListener("submit", event => {
  event.preventDefault();
  act(event.submitter, () => api("/v1/schedules", {method: "POST", json: {
    name: $("schedule-name").value.trim(), objective: $("schedule-objective").value.trim(),
    evidence_selectors: [{platform: $("schedule-platform").value, report_type: $("schedule-report-type").value}],
    interval_minutes: Number($("schedule-interval").value), next_run_at: new Date($("schedule-next-run").value).toISOString(),
  }}), "Schedule 已创建。");
});

$("proposal-form").addEventListener("submit", event => {
  event.preventDefault();
  if (!proposalCanCreate()) { notice("需要 operator、admin 或 owner 角色", "error"); return; }
  let payload; try { payload = JSON.parse($("proposal-payload").value); } catch { notice("Payload 必须是有效 JSON", "error"); return; }
  const run = state.dailyOpsRuns.find(item => item.id === $("proposal-run").value); const priority = proposalPriorities(run)[Number($("proposal-priority").value)];
  if (!run || !priority) { notice("请选择已完成 Daily Ops 优先事项", "error"); return; }
  const expiry = new Date($("proposal-expires").value);
  if (!Number.isFinite(expiry.getTime()) || expiry.getTime() <= Date.now()) { notice("过期时间必须晚于现在。", "error"); return; }
  act(event.submitter, async () => {
    await api("/v1/proposals", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-proposal")}, json: {daily_ops_run_id: run.id, priority_rank: Number($("proposal-priority").value) + 1, operation: $("proposal-operation").value, risk: $("proposal-risk").value, payload, rollback_plan: $("proposal-rollback").value.trim(), expires_at: expiry.toISOString()}});
    $("proposal-form").reset();
    setDefaultTimes();
  }, "提案已创建。");
});

$("proposal-decision-form").addEventListener("submit", event => {
  event.preventDefault();
  const id = $("proposal-decision-id").value;
  const comment = $("proposal-decision-comment").value.trim();
  if (!comment) { notice("请填写审批备注。", "error"); return; }
  act(event.submitter, async () => {
    await api(`/v1/proposals/${id}/decisions`, {method: "POST", json: {expected_version: Number($("proposal-decision-version").value), decision: $("proposal-decision").value, comment}});
    $("proposal-decision-dialog").close();
    $("proposal-decision-form").reset();
  }, "审批决定已保存。");
});
$("proposal-revision-form").addEventListener("submit", event => {
  event.preventDefault();
  let payload;
  try { payload = JSON.parse($("proposal-revision-payload").value); }
  catch { notice("Payload 必须是有效 JSON", "error"); return; }
  const expiry = new Date($("proposal-revision-expires").value);
  if (!Number.isFinite(expiry.getTime()) || expiry.getTime() <= Date.now()) { notice("修订后的过期时间必须晚于现在。", "error"); return; }
  const id = $("proposal-revision-id").value;
  act(event.submitter, async () => {
    await api(`/v1/proposals/${id}`, {method: "PATCH", json: {
      expected_version: Number($("proposal-revision-version").value),
      title: $("proposal-revision-title").value.trim(),
      rationale: $("proposal-revision-rationale").value.trim(),
      expected_impact: $("proposal-revision-impact").value.trim(),
      rollback_plan: $("proposal-revision-rollback").value.trim(),
      operation: $("proposal-revision-operation").value,
      risk: $("proposal-revision-risk").value,
      expires_at: expiry.toISOString(),
      payload,
    }});
    $("proposal-revision-dialog").close();
  }, "提案修订已保存。");
});
$("proposal-operation").addEventListener("change", setProposalPayloadTemplate);
$("proposal-run").addEventListener("change", populateProposalPriorities);
$("proposal-revision-operation").addEventListener("change", () => {
  $("proposal-revision-payload").value = proposalPayloadTemplate($("proposal-revision-operation").value);
});

document.addEventListener("visibilitychange", () => {
  if (document.hidden) pauseLiveStream();
  else if (!state.liveStopped && state.apiKey) void startLiveStream();
});
window.addEventListener("pagehide", pauseLiveStream);
window.addEventListener("pageshow", () => {
  if (!state.liveStopped && state.apiKey) void startLiveStream();
});

$("daily-ops-form").addEventListener("submit", event => {
  event.preventDefault();
  if (!dailyOpsCanManage()) { notice("需要 operator、admin 或 owner 角色", "error"); return; }
  const graphVersionId = $("daily-ops-graph").value, reportType = $("daily-ops-evidence").value;
  const maxSourceAgeHours = Number($("daily-ops-max-age").value);
  if (!graphVersionId || !reportType || !$("daily-ops-time").value || !$("daily-ops-timezone").value.trim() || !Number.isInteger(maxSourceAgeHours) || maxSourceAgeHours < 1 || maxSourceAgeHours > 8760) { notice("请完成 Daily Ops 配置，并选择已发布 Graph 与 Evidence report type。", "error"); return; }
  act(event.submitter, () => api("/v1/daily-ops-schedules", {method: "POST", headers: {"Idempotency-Key": idempotency("ui-daily-ops-schedule")}, json: {name: $("daily-ops-name").value.trim(), platform: state.selectedPlatform, objective: $("daily-ops-objective").value.trim(), timezone_name: $("daily-ops-timezone").value.trim(), local_time: $("daily-ops-time").value, graph_version_id: graphVersionId, evidence_selectors: [{report_type: reportType}], max_source_age_hours: maxSourceAgeHours, enabled: true}}), "Daily Ops 计划已创建。");
});

function setDefaultTimes() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  $("evidence-observed").value = local;
  const next = new Date(now.getTime() + 5 * 60000);
  $("schedule-next-run").value = new Date(next.getTime() - next.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  if ($("daily-ops-timezone") && !$("daily-ops-timezone").value) $("daily-ops-timezone").value = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  if ($("proposal-expires")) { const expiry = new Date(now.getTime() + 24 * 60 * 60000); $("proposal-expires").value = localDateTimeValue(expiry); }
  if ($("proposal-payload")) setProposalPayloadTemplate();
}

window.addEventListener("resize", () => {
  const metric = (state.briefing?.metrics || []).find(item => (item.series_id || item.key) === state.chartMetric);
  if (metric) requestAnimationFrame(() => drawChart(metric));
});

const now = new Date();
$("today-label").textContent = `今天是 ${now.toLocaleDateString("zh-CN", {year: "numeric", month: "2-digit", day: "2-digit"})}`;
setDefaultTimes();
setConnected(false);
renderDisconnected();
tryDemoSession().catch(error => notice(error.message, "error"));
