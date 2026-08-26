/* Commerce Agent OS locale catalog.  This file is intentionally standalone so
 * the existing runtime can adopt it without changing its data or auth flow. */
(function (global) {
  "use strict";

  const SUPPORTED = ["zh-CN", "en"];
  const STORAGE_KEY = "commerce-agent-os.locale";
  const textSources = new WeakMap();
  const attributeSources = new WeakMap();
  const titleSources = new WeakMap();
  let memoryLocale = null;

  // Product names, API names, identifiers, and user/agent generated content are
  // deliberately not in this catalog. They must remain stable across locales.
  const CATALOG = {
    "zh-CN": {
      "Commerce Agent OS · 今日简报": "Commerce Agent OS · 今日简报", "今日简报": "今日简报", "主导航": "主导航",
      Agents: "智能体", Evidence: "证据", Approvals: "审批", Accounts: "账户", Automations: "自动化", Audit: "审计",
      "Local Runtime": "本地运行时", "未连接": "未连接", "已连接": "已连接", "连接 Runtime": "连接运行时",
      "断开": "断开", "安全连接": "安全连接", "界面主题": "界面主题", Light: "浅色", Dark: "深色", "使用 Light 主题": "使用浅色主题", "使用 Dark 主题": "使用深色主题",
      "DEMO DATA": "演示数据", "当前为 Demo 租户": "当前为 Demo 租户", "连接 Runtime 后显示真实经营数据。": "连接 Runtime 后显示真实经营数据。",
      "查看今日简报": "查看今日简报", "开始周度复盘": "开始周度复盘", "真实 Evidence 趋势": "真实 Evidence 趋势",
      "尚未连接": "尚未连接", "等待数据": "等待数据", "等待 Evidence": "等待证据", "还没有可绘制的经营指标": "还没有可绘制的经营指标",
      "导入 Evidence": "导入证据", "查看全部 Runs": "查看全部运行记录", "需要你决定": "需要你决定", "待审批": "待审批",
      "运行状态": "运行状态", "Agent 协作中": "Agent 协作中", "选择趋势指标": "选择趋势指标", "经营指标趋势图": "经营指标趋势图",
      "导入真实数据": "导入真实数据", "平台": "平台", "报表类型": "报表类型", "观察时间": "观察时间", "工作表（可选）": "工作表（可选）",
      "选择真实 CSV、TSV 或 XLSX": "选择真实 CSV、TSV 或 XLSX", "上传并验证": "上传并验证", "已验证 Evidence": "已验证 Evidence",
      "指标观测": "指标观测", "物化任务": "物化任务", "Agent Operations": "Agent Operations", "Weekly Ops": "Weekly Ops",
      "创建 Agent Run": "创建智能体运行", "Agent Runs": "智能体运行记录", "审批中心": "审批中心", "行动提案": "行动提案", "创建提案": "创建提案",
      "审批队列": "审批队列", "连接店铺账户": "连接店铺账户", "添加账户": "添加账户", "运行准入检查": "运行准入检查", "保存账户": "保存账户",
      "计划与后台任务": "计划与后台任务", "刷新运行状态": "刷新运行状态", "实时运行状态": "实时运行状态", "立即重试": "立即重试",
      "创建 Schedule": "创建计划", "后台任务": "后台任务", "Daily Ops 计划": "Daily Ops 计划", "Daily Ops 运行": "Daily Ops 运行",
      "审计时间线": "审计时间线", "运行 Eval": "运行 Eval", "运行 Security": "运行 Security", "不可变审计事件": "不可变审计事件",
      "关闭": "关闭", "详情": "详情", "查看": "查看", "查看详情": "查看详情", "编辑": "编辑", "健康检查": "健康检查",
      "批准": "批准", "拒绝": "拒绝", "要求修改": "要求修改", "提交决定": "提交决定", "保存新版本": "保存新版本",
      "连接后读取真实经营数据。": "连接后读取真实经营数据。", "请先连接 Runtime": "请先连接 Runtime", "请先连接 Runtime。": "请先连接 Runtime。",
      "viewer": "查看者", "operator": "操作员", "admin": "管理员", "owner": "所有者", "checking": "检查中", "pending": "待处理",
      "requested": "已请求", "scheduled": "已计划", "queued": "已排队", "running": "运行中", "processing": "处理中", "completed": "已完成",
      "succeeded": "成功", "failed": "失败", "blocked": "已阻断", "approved": "已批准", "rejected": "已拒绝", "revision_required": "需要修订",
      "expired": "已过期", "enabled": "已启用", "disabled": "已停用", "healthy": "健康", "unhealthy": "不健康", "degraded": "降级",
      "stopped": "已停止", "connected": "已连接", "disconnected": "未连接", "low": "低", "medium": "中", "high": "高", "critical": "严重",
      "需要 admin 或 owner 角色": "需要管理员或所有者角色", "需要 operator、admin 或 owner 角色": "需要操作员、管理员或所有者角色",
      "当前角色只能查看": "当前角色只能查看", "尚无已发布协作图": "尚无已发布协作图", "尚无 Evidence": "尚无 Evidence",
      "暂无后台任务": "暂无后台任务", "暂无实时活动": "暂无实时活动", "未知阻塞": "未知阻塞", "检查未通过": "检查未通过",
      "人工复核": "人工复核", "同步 Shopify 商品": "同步 Shopify 商品", "导入 Amazon 报表": "导入 Amazon 报表", "更新 Amazon Ads Campaign": "更新 Amazon Ads Campaign",
      "请输入 API Key": "请输入 API Key", "请选择文件": "请选择文件", "请求失败": "请求失败", "保存": "保存", "重试": "重试"
      ,"Connections": "连接", "Connection Center": "连接中心", "Marketplace APIs": "平台 API", "AI Provider": "AI 提供商",
      "Reports & Sync": "报表与同步", "Runtime session": "Runtime 会话", "Secret boundary": "密钥边界", "Last checked": "最近检查",
      "Credential refs": "凭据引用", "Report type": "报表类型", "Marketplaces": "销售市场", "Cadence": "执行频率", "lookback": "回溯窗口", "Lookback": "回溯窗口", "Next run": "下次运行",
      "Adapter Lock": "适配器锁", "Agent Brief": "Agent 简报", "Pilot Runtime": "Pilot 运行时", "Live Mission Control": "实时任务控制", "Assurance Center": "Assurance 中心",
      "present": "存在", "checks": "检查项", "checks passed": "检查项通过", "sources": "来源", "rows": "行", "sources/rows": "来源/行", "Runtime": "运行时", "Marketplace": "平台", "AI": "人工智能", "Reports": "报表", "状态": "状态", "加载失败": "加载失败", "保存失败": "保存失败", "连接失败": "连接失败", "验证失败": "验证失败", "修复": "修复", "立即修复": "立即修复",
      "Connection": "连接", "Connections Hub": "连接中心"
    },
    en: {
      "Commerce Agent OS · 今日简报": "Commerce Agent OS · Daily Briefing", "今日简报": "Daily Briefing", "主导航": "Main navigation",
      Agents: "Agents", Evidence: "Evidence", Approvals: "Approvals", Accounts: "Accounts", Automations: "Automations", Audit: "Audit",
      "Local Runtime": "Local Runtime", "未连接": "Disconnected", "已连接": "Connected", "连接 Runtime": "Connect Runtime",
      "断开": "Disconnect", "安全连接": "Connect securely", "界面主题": "Theme", Light: "Light", Dark: "Dark", "使用 Light 主题": "Use Light theme", "使用 Dark 主题": "Use Dark theme",
      "DEMO DATA": "DEMO DATA", "当前为 Demo 租户": "Demo tenant", "连接 Runtime 后显示真实经营数据。": "Connect Runtime to show live business data.",
      "查看今日简报": "View today's briefing", "开始周度复盘": "Start weekly review", "真实 Evidence 趋势": "Verified Evidence trends",
      "尚未连接": "Not connected", "等待数据": "Waiting for data", "等待 Evidence": "Waiting for Evidence", "还没有可绘制的经营指标": "No metrics to chart yet",
      "导入 Evidence": "Import Evidence", "查看全部 Runs": "View all Runs", "需要你决定": "Your decision needed", "待审批": "Pending approvals",
      "运行状态": "Runtime status", "Agent 协作中": "Agents collaborating", "选择趋势指标": "Select trend metric", "经营指标趋势图": "Business metric trend chart",
      "导入真实数据": "Import live data", "平台": "Platform", "报表类型": "Report type", "观察时间": "Observed at", "工作表（可选）": "Worksheet (optional)",
      "选择真实 CSV、TSV 或 XLSX": "Choose a CSV, TSV, or XLSX file", "上传并验证": "Upload and validate", "已验证 Evidence": "Verified Evidence",
      "指标观测": "Metric observations", "物化任务": "Materialization jobs", "Agent Operations": "Agent Operations", "Weekly Ops": "Weekly Ops",
      "创建 Agent Run": "Create Agent Run", "Agent Runs": "Agent Runs", "审批中心": "Approvals", "行动提案": "Action proposals", "创建提案": "Create proposal",
      "审批队列": "Approval queue", "连接店铺账户": "Connect store accounts", "添加账户": "Add account", "运行准入检查": "Run capability check", "保存账户": "Save account",
      "计划与后台任务": "Schedules and background jobs", "刷新运行状态": "Refresh runtime status", "实时运行状态": "Live runtime status", "立即重试": "Retry now",
      "创建 Schedule": "Create Schedule", "后台任务": "Background jobs", "Daily Ops 计划": "Daily Ops schedules", "Daily Ops 运行": "Daily Ops runs",
      "审计时间线": "Audit timeline", "运行 Eval": "Run Eval", "运行 Security": "Run Security", "不可变审计事件": "Immutable audit events",
      "关闭": "Close", "详情": "Details", "查看": "View", "查看详情": "View details", "编辑": "Edit", "健康检查": "Health check",
      "批准": "Approve", "拒绝": "Reject", "要求修改": "Request changes", "提交决定": "Submit decision", "保存新版本": "Save new version",
      "连接后读取真实经营数据。": "Connect to read live business data.", "请先连接 Runtime": "Connect Runtime first", "请先连接 Runtime。": "Connect Runtime first.",
      "viewer": "Viewer", "operator": "Operator", "admin": "Administrator", "owner": "Owner", "checking": "Checking", "pending": "Pending",
      "requested": "Requested", "scheduled": "Scheduled", "queued": "Queued", "running": "Running", "processing": "Processing", "completed": "Completed",
      "succeeded": "Succeeded", "failed": "Failed", "blocked": "Blocked", "approved": "Approved", "rejected": "Rejected", "revision_required": "Changes required",
      "expired": "Expired", "enabled": "Enabled", "disabled": "Disabled", "healthy": "Healthy", "unhealthy": "Unhealthy", "degraded": "Degraded",
      "stopped": "Stopped", "connected": "Connected", "disconnected": "Disconnected", "low": "Low", "medium": "Medium", "high": "High", "critical": "Critical",
      "需要 admin 或 owner 角色": "Administrator or owner role required", "需要 operator、admin 或 owner 角色": "Operator, administrator, or owner role required",
      "当前角色只能查看": "Your role is read-only", "尚无已发布协作图": "No published Agent Graphs", "尚无 Evidence": "No Evidence yet",
      "暂无后台任务": "No background jobs", "暂无实时活动": "No live activity", "未知阻塞": "Unknown blocker", "检查未通过": "Check failed",
      "人工复核": "Human review", "同步 Shopify 商品": "Sync Shopify products", "导入 Amazon 报表": "Import Amazon report", "更新 Amazon Ads Campaign": "Update Amazon Ads Campaign",
      "请输入 API Key": "Enter an API Key", "请选择文件": "Choose a file", "请求失败": "Request failed", "保存": "Save", "重试": "Retry"
      ,"Connections": "Connections", "Connection Center": "Connection Center", "Marketplace APIs": "Marketplace APIs", "AI Provider": "AI Provider",
      "Reports & Sync": "Reports & Sync", "Runtime session": "Runtime session", "Secret boundary": "Secret boundary", "Last checked": "Last checked",
      "Credential refs": "Credential refs", "Report type": "Report type", "Marketplaces": "Marketplaces", "Cadence": "Cadence", "lookback": "Lookback", "Lookback": "Lookback", "Next run": "Next run",
      "Adapter Lock": "Adapter Lock", "Agent Brief": "Agent Brief", "Pilot Runtime": "Pilot Runtime", "Live Mission Control": "Live Mission Control", "Assurance Center": "Assurance Center",
      "present": "Present", "checks": "Checks", "checks passed": "Checks passed", "sources": "Sources", "rows": "Rows", "sources/rows": "Sources/rows", "Runtime": "Runtime", "Marketplace": "Marketplace", "AI": "AI", "Reports": "Reports", "状态": "Status", "加载失败": "Load failed", "保存失败": "Save failed", "连接失败": "Connection failed", "验证失败": "Validation failed", "修复": "Fix", "立即修复": "Fix now",
      "Connection": "Connection", "Connections Hub": "Connections Hub"
    }
  };

  function locale(value) { return SUPPORTED.includes(value) ? value : "zh-CN"; }
  // Static mission-control surface coverage. Values are UI copy only; runtime/user data is never cataloged.
  const STATIC_CATALOG = {
    "API 密钥": "API Key",
    "API 密钥仅保存在当前页面内存，刷新或断开后立即清除。": "The API Key stays in page memory only and is cleared on refresh or disconnect.",
    "API Key 仅保存在当前页面内存，刷新或断开后立即清除。": "The API Key stays in page memory only and is cleared on refresh or disconnect.",
    "API Key 只保存在当前页面内存，不写入浏览器存储或 Runtime 数据库。": "The API Key stays in page memory only; it is never written to browser storage or the Runtime database.",
    "Access token 环境变量": "Access token environment variable",
    "Agent Graph 版本": "Agent Graph version",
    "Agent 协作中": "Agents collaborating",
    "Amazon Ads Campaign 更新（被阻断）": "Amazon Ads campaign update (blocked)",
    "Amazon Ads 准入": "Amazon Ads access check",
    "Amazon Ads 更新 Campaign（当前被 Adapter Lock 阻断）": "Update an Amazon Ads campaign (currently blocked by Adapter Lock)",
    "Amazon Ads 账户": "Amazon Ads account",
    "Cadence（分钟）": "Cadence (minutes)",
    "Daily Ops 计划": "Daily Ops schedules",
    "Daily Ops 运行": "Daily Ops runs",
    "Eval 验证真实 Reviewer/评测覆盖；Security 验证数据库、租户约束和审计哈希链。": "Eval verifies real Reviewer and evaluation coverage; Security verifies the database, tenant constraints, and audit hash chain.",
    "Evidence 类型": "Evidence type",
    "LWA client ID 环境变量": "LWA client ID environment variable",
    "LWA client secret 环境变量": "LWA client secret environment variable",
    "Lookback（天）": "Lookback (days)",
    "Marketplace 与模型密钥由部署环境或 Secret Manager 提供。": "Marketplace and model credentials are supplied by the deployment environment or Secret Manager.",
    "Presence 只表示配置项存在，不代表模型访问已通过真实调用验证。当前版本没有浏览器端“测试 OpenAI”按钮。": "Presence means the setting exists; it does not prove model access through a live call. This version has no browser-side “Test OpenAI” button.",
    "Recipe 只会从该账户已配置的 marketplaces 中选择。L2 仅保存配置，不会调用 Amazon。": "The recipe can select only marketplaces configured for this account. L2 saves configuration only and does not call Amazon.",
    "Refresh token 环境变量": "Refresh token environment variable",
    "Restore 只允许本地 CLI": "Restore is available only through the local CLI",
    "Runtime API Key 只存在于当前页面内存；刷新或断开后清除。": "The Runtime API Key exists only in page memory and is cleared on refresh or disconnect.",
    "Schedule 只选择最新真实 Evidence，Worker 使用持久化队列、租约和重试。": "Schedules select only the latest verified Evidence. Workers use a durable queue, leases, and retries.",
    "Seller ID 或店铺账户 ID": "Seller ID or store account ID",
    "Worker 心跳": "Worker heartbeats",
    "一条命令统一运行 API 与六个后台 Worker；此处只读取真实持久心跳，不从浏览器启动或停止进程。": "One command runs the API and six background workers. This page reads durable heartbeats; it does not start or stop processes from the browser.",
    "上传并验证": "Upload and validate",
    "不可变审计事件": "Immutable audit events",
    "不要填写密钥或凭证值。": "Do not enter secrets or credential values.",
    "中文": "Chinese",
    "为什么现在要做": "Why act now",
    "主导航": "Main navigation",
    "仅从已完成的 Daily Ops 优先事项创建；所有外部写入都先经过审批。": "Create proposals only from completed Daily Ops priorities. Every external write requires approval first.",
    "今日简报": "Daily briefing",
    "从已验证 Evidence 物化；每个数值都保留原始来源、周期和质量信号。": "Materialized from verified Evidence; every value retains its source, period, and quality signals.",
    "优先事项": "Priorities",
    "使用 Dark 主题": "Use Dark theme",
    "使用 Light 主题": "Use Light theme",
    "使用中文": "Use Chinese",
    "保存 Recipe": "Save Recipe",
    "保存会创建不可变的新版本，并使旧版本审批失效。": "Saving creates a new immutable version and invalidates approvals for the old version.",
    "保存可复现的 Amazon 报告配置；远程采集由 L3 Sync 执行。": "Save reproducible Amazon report configuration; L3 Sync performs remote collection.",
    "保存新版本": "Save new version",
    "保存账户": "Save account",
    "修订提案": "Revise proposal",
    "写入适配器单独评估；当前版本只允许读取和展示状态。": "The write adapter is evaluated separately. This version can only read and display status.",
    "决定": "Decision",
    "决定会绑定当前提案版本与内容哈希，提交后不可修改。": "The decision is bound to the current proposal version and content hash and cannot be changed after submission.",
    "切换操作时会载入该平台的有效参数模板；只填写账户标识，不要填写密钥。": "Changing the operation loads a valid parameter template for that platform. Enter account identifiers only, never secrets.",
    "创建 Daily Ops": "Create Daily Ops",
    "创建提案": "Create proposal",
    "刷新运行状态": "Refresh runtime status",
    "同步 Shopify 商品": "Sync Shopify products",
    "名称": "Name",
    "后台任务": "Background jobs",
    "启用此 Recipe": "Enable this Recipe",
    "回滚方案": "Rollback plan",
    "图由管理员通过 API 发布；当前页面只允许选择已发布版本运行。": "Administrators publish graphs through the API. This page can run only published versions.",
    "在一个位置管理当前 Runtime 会话、Marketplace API、模型 API 准备度和报告同步配置。": "Manage the current Runtime session, Marketplace APIs, model API readiness, and report sync configuration in one place.",
    "在运行 Pilot 的 Secret Manager 或进程环境中设置以下变量，然后重启 Pilot 并重新检查：": "Set these variables in the Secret Manager or process environment that runs Pilot, then restart Pilot and check again:",
    "基于证据的关键发现，按影响优先": "Evidence-backed findings, prioritized by impact",
    "填写平台账户标识和环境变量名称。不要输入任何密钥值。": "Enter platform account identifiers and environment-variable names. Never enter secret values.",
    "外部账户 ID": "External account ID",
    "安全连接": "Connect securely",
    "实时运行状态": "Live runtime status",
    "审批": "Approvals",
    "审批中心": "Approval center",
    "审批备注": "Approval note",
    "审批／工单 reference（可选）": "Approval or ticket reference (optional)",
    "审查最新导入的数据并生成本周行动计划。": "Review the latest imported data and create this week’s action plan.",
    "审计": "Audit",
    "密钥安全边界": "Credential security boundary",
    "导入 Amazon Business、Ads 或 FBA Inventory 报表后，这里只显示真实观测值。": "Import Amazon Business, Ads, or FBA Inventory reports; this chart displays verified observations only.",
    "导入 Amazon 报表": "Import Amazon report",
    "将使用已保存的环境变量引用验证 Ads 访问能力。可选填写审批或工单号，便于审计追踪。": "Validate Ads access using saved environment-variable references. Optionally add an approval or ticket number for audit traceability.",
    "工作表（可选）": "Worksheet (optional)",
    "已验证 Evidence": "Verified Evidence",
    "平台": "Platform",
    "开始周度复盘": "Start weekly review",
    "当前为 Demo 租户": "Demo tenant",
    "当前会话": "Current session",
    "当前租户准备度": "Current tenant readiness",
    "当前趋势数据": "Current trend data",
    "待审批": "Pending approvals",
    "恢复原值": "Restore the previous value",
    "所有外部动作都必须经过授权；Agent 不会绕过审批直接执行。": "Every external action requires authorization; agents never bypass approval to execute directly.",
    "所有指标、Evidence、Agent 结论和审批均为演示数据，不可用于真实经营决策。": "All metrics, Evidence, agent conclusions, and approvals are demo data and must not be used for real business decisions.",
    "找出本周最重要、可由证据支持的经营行动。": "Identify this week’s most important business actions supported by Evidence.",
    "报表类型": "Report type",
    "拒绝": "Reject",
    "按本地日期与时区运行；只使用已持久化 Evidence，缺失时保留明确空态。": "Run by local date and time zone using persisted Evidence only, with an explicit empty state when data is missing.",
    "提交决定": "Submit decision",
    "提案审批": "Proposal approval",
    "操作": "Operation",
    "操作参数（JSON）": "Operation parameters (JSON)",
    "数值": "Value",
    "文件不会离开当前 Runtime。": "The file never leaves this Runtime.",
    "文件经过字段验证、PII/密钥拦截和租户隔离后才会进入 Agent 工作流。": "Files enter the agent workflow only after field validation, PII and secret checks, and tenant isolation.",
    "早上好，今天先看": "Good morning. Start with",
    "时区": "Timezone",
    "智能体": "Agents",
    "最大来源年龄（小时）": "Maximum source age (hours)",
    "未连接": "Disconnected",
    "本地时间": "Local time",
    "本次目标": "Objective",
    "查看 Pilot Runtime 详情": "View Pilot Runtime details",
    "查看全部 Runs": "View all Runs",
    "查看全部审批": "View all approvals",
    "标题": "Title",
    "检查授权、Profile、Sponsored Products 读取权限与外部审批；不会创建、修改或暂停 Campaign。": "Check authorization, profile, Sponsored Products read access, and external approval. This does not create, modify, or pause campaigns.",
    "检查最新经营信号并生成今日行动建议。": "Review the latest business signals and create today’s recommended actions.",
    "模型 API 准备度": "Model API readiness",
    "此页面仅保存环境变量引用和非敏感连接配置。": "This page saves only environment-variable references and non-sensitive connection configuration.",
    "每条事件绑定前一条哈希；完整性由 Security Assurance 复核。": "Each event is bound to the previous hash; Security Assurance verifies integrity.",
    "每次导入、Agent 执行、审批和外部动作都保留租户内可追溯记录。": "Every import, agent run, approval, and external action retains a tenant-scoped audit record.",
    "浏览器不会覆盖数据库。使用经过校验的 `opc-ecommerce backup` / `restore` 后，恢复演练会作为真实 Assurance 记录出现。": "The browser never overwrites the database. After a validated `opc-ecommerce backup` / `restore`, the recovery drill appears as a real Assurance record.",
    "添加 Recipe": "Add Recipe",
    "添加账户": "Add account",
    "添加连接": "Add connection",
    "物化任务": "Materialization jobs",
    "由 L3 Worker 异步执行并轮询；排队不表示报表已完成。": "An L3 Worker runs and polls asynchronously; queued does not mean the report is complete.",
    "界面主题": "Theme",
    "界面语言": "Language",
    "的经营信号": "business signals",
    "目标": "Objective",
    "真实 Evidence 趋势": "Verified Evidence trends",
    "立即重试": "Retry now",
    "等待数据": "Waiting for data",
    "简报": "Briefing",
    "经营指标趋势图": "Business metric trend chart",
    "自动化": "Automations",
    "行动提案": "Action proposals",
    "要求修改": "Request changes",
    "观察时间": "Observed at",
    "证据": "Evidence",
    "详情": "Details",
    "说明判断依据或需要修改的内容": "Explain the rationale or requested changes",
    "过期时间": "Expiration",
    "运行 Eval": "Run Eval",
    "运行 Security": "Run Security",
    "运行准入检查": "Run capability check",
    "运行真实准入检查": "Run live capability check",
    "还没有可绘制的经营指标": "No metrics to chart yet",
    "这是管理员提供的外部批准引用，不是 Amazon API 自动签发的证明。": "This is an external approval reference supplied by an administrator, not an attestation issued automatically by the Amazon API.",
    "这里只读取部署环境中的配置存在性，不会接收、保存或回显模型密钥。": "This page checks whether deployment configuration exists; it never receives, stores, or reveals model credentials.",
    "连接": "Connection",
    "连接 Amazon SP-API、Amazon Ads 与 Shopify；保存环境变量引用，不保存密钥值。": "Connect Amazon SP-API, Amazon Ads, and Shopify. Save environment-variable references, never secret values.",
    "连接 Runtime": "Connect Runtime",
    "连接 Runtime 后开始接收租户内的实时状态。": "Connect Runtime to receive live tenant-scoped status.",
    "连接 Runtime 后显示真实经营数据。": "Connect Runtime to show live business data.",
    "连接与 API": "Connections & APIs",
    "连接后，Agent 会把真实 Evidence 汇总为需要你决定的经营事项。": "After connecting, agents summarize verified Evidence into business decisions that need your review.",
    "连接或更换 Key": "Connect or replace key",
    "连接设置": "Connection settings",
    "连接设置分类": "Connection settings",
    "选择 Evidence": "Select Evidence",
    "选择 Metric Observations（可选）": "Select Metric Observations (optional)",
    "选择已发布协作图": "Select published Agent Graph",
    "选择已发布的协作图与真实输入，交给平台专家、跨平台 Controller、Manager 和 Reviewer 协作。": "Select a published collaboration graph and verified inputs for platform specialists, the cross-platform Controller, Manager, and Reviewer to work together.",
    "选择趋势指标": "Select trend metric",
    "部署环境配置": "Deployment environment configuration",
    "重新检查": "Check again",
    "间隔（分钟）": "Interval (minutes)",
    "需要你决定": "Your decision needed",
    "项行动": "actions",
    "预期影响": "Expected impact",
    "风险": "Risk",
    "首次运行": "First run",
    "高风险外部动作必须由另一位具备权限的用户审批，随后才允许 Operator 执行。": "High-risk external actions require approval by another authorized user before an Operator may execute them.",
  };
  Object.keys(STATIC_CATALOG).forEach(key => {
    if (CATALOG["zh-CN"][key] === undefined) CATALOG["zh-CN"][key] = key;
    if (CATALOG.en[key] === undefined) CATALOG.en[key] = STATIC_CATALOG[key];
  });
  const GENERIC_CATALOG = {
    "API credential": ["API 凭据", "API credential"], "API version": ["API 版本", "API version"],
    "Advertising profile ID": ["广告 Profile ID", "Advertising profile ID"], "Amazon account": ["Amazon 账户", "Amazon account"],
    "Amazon Ads region": ["Amazon Ads 区域", "Amazon Ads region"], "Amazon region": ["Amazon 区域", "Amazon region"],
    "Audit Trail": ["审计轨迹", "Audit Trail"], Automation: ["自动化", "Automation"], "Daily Ops": ["每日运营", "Daily Ops"],
    "Eval · Security · Restore": ["评测 · 安全 · 恢复", "Eval · Security · Restore"], "Evidence Center": ["证据中心", "Evidence Center"],
    "Evidence report type": ["证据报表类型", "Evidence report type"], "Evidence-backed detail": ["证据支撑的详情", "Evidence-backed detail"],
    "Hash chained": ["哈希链", "Hash chained"], "Human Control": ["人工控制", "Human Control"], "Human control": ["人工控制", "Human control"],
    Imported: ["已导入", "Imported"], "Legacy Actions": ["旧版操作", "Legacy Actions"], "Marketplace connection": ["平台连接", "Marketplace connection"],
    Materialization: ["指标物化", "Materialization"], "Metric Observations": ["指标观测", "Metric Observations"], Model: ["模型", "Model"],
    Normalized: ["已标准化", "Normalized"], "One-command Pilot": ["一键 Pilot", "One-command Pilot"], Proposals: ["提案", "Proposals"],
    Provider: ["提供商", "Provider"], "Published Agent Graphs": ["已发布智能体协作图", "Published Agent Graphs"], "Recipe type": ["报表方案类型", "Recipe type"],
    "Report Recipes": ["报表方案", "Report Recipes"], "Run History": ["运行历史", "Run History"], Runs: ["运行记录", "Runs"],
    "Runtime API": ["运行时 API", "Runtime API"], Schedules: ["计划", "Schedules"], "Secure local session": ["安全本地会话", "Secure local session"],
    "Shopify domain": ["Shopify 域名", "Shopify domain"], "Sync Activity": ["同步活动", "Sync Activity"], "Use English": ["使用英文", "Use English"],
    "Versioned proposal": ["版本化提案", "Versioned proposal"], Workers: ["后台执行器", "Workers"], "XLSX sheet name": ["XLSX 工作表名称", "XLSX sheet name"],
    "Amazon daily pulse": ["Amazon 每日脉搏", "Amazon daily pulse"], "Amazon weekly review": ["Amazon 周度复盘", "Amazon weekly review"],
    "US business report": ["美国站经营报告", "US business report"], Tenant: ["租户", "Tenant"], Role: ["角色", "Role"],
    "Session secret": ["会话密钥", "Session secret"], "Memory only": ["仅内存", "Memory only"], Storage: ["存储", "Storage"],
    "Not persisted": ["不持久化", "Not persisted"], "Live verification": ["实时验证", "Live verification"], "Secret storage": ["密钥存储", "Secret storage"],
    "Deployment environment": ["部署环境", "Deployment environment"], "Deployment managed · presence only": ["部署托管 · 仅检查存在性", "Deployment managed · presence only"],
    missing: ["缺少配置", "Missing"], unknown: ["未知", "Unknown"], ready: ["就绪", "Ready"], attention: ["需要关注", "Needs attention"],
    starting: ["启动中", "Starting"], stopping: ["停止中", "Stopping"], stale: ["已过期", "Stale"], superseded: ["已取代", "Superseded"],
    unchecked: ["未检查", "Unchecked"], misconfigured: ["配置错误", "Misconfigured"], polling: ["轮询中", "Polling"], passed: ["已通过", "Passed"],
    executed: ["已执行", "Executed"], fatal: ["严重错误", "Fatal"], error: ["错误", "Error"], empty: ["暂无数据", "No data"], skipped: ["已跳过", "Skipped"],
    auth_failed: ["认证失败", "Authentication failed"], reconnecting: ["重新连接中", "Reconnecting"], connecting: ["连接中", "Connecting"],
    Blocked: ["已阻断", "Blocked"], "Eligible · 未安装": ["符合条件 · 未安装", "Eligible · Not installed"], snapshot: ["快照", "Snapshot"],
  };
  Object.entries(GENERIC_CATALOG).forEach(([key, values]) => {
    CATALOG["zh-CN"][key] = values[0];
    CATALOG.en[key] = values[1];
  });
  // Controlled app.js feedback, empty states, and permission copy.
  const APP_CATALOG = {
    "主题已切换，但浏览器无法保存偏好。": "Theme changed, but the browser could not save the preference.",
    "暂无同步活动": "No sync activity yet", "暂无后台任务": "No background jobs yet", "暂无实时活动": "No live activity yet",
    "暂无审计事件": "No audit events yet", "暂无行动提案": "No action proposals yet", "暂无物化任务": "No materialization jobs yet",
    "无法加载提案": "Unable to load proposals", "界面语言已更新。": "Interface language updated.",
    "已连接。API Key 仅保存在当前页面内存。": "Connected. The API Key stays in page memory only.",
    "提案已提交审批。": "Proposal submitted for approval.", "提案详情已加载。": "Proposal details loaded.",
    "提案执行已重试。": "Proposal execution retried.", "提案已提交执行。": "Proposal submitted for execution.",
    "账户已添加。": "Account added.", "账户配置已更新。": "Account configuration updated.",
    "Demo 数据已自动加载。": "Demo data loaded automatically.",
    "健康检查已完成。": "Health check completed.", "准入详情已加载。": "Capability details loaded.",
    "安全检查已保存。": "Security check saved.", "工作流评测已保存。": "Workflow evaluation saved.",
    "指标物化结果已刷新。": "Metric materialization refreshed.", "同步 Shopify 商品": "Sync Shopify products",
    "人工复核记录": "Human review record", "导入 Amazon SP-API 报表": "Import Amazon SP-API report", "更新 Amazon Ads Campaign": "Update Amazon Ads campaign",
    "更新 Shopify 商品": "Update Shopify product", "更新 Shopify 库存": "Update Shopify inventory",
    "需要 admin 或 owner 角色": "Administrator or owner role required",
    "需要 operator、admin 或 owner 角色": "Operator, administrator, or owner role required",
    "Runtime 未连接": "Runtime disconnected", "Runtime 已连接": "Runtime connected",
    "连接 Runtime API Key 后显示当前租户与角色。": "Connect with a Runtime API Key to view the current tenant and role.",
    "连接后读取模型 API 的部署准备度。": "Connect to read model API deployment readiness.",
    "正在检查模型 API": "Checking model API", "正在读取部署环境中的配置存在性。": "Checking for deployment configuration.",
    "无法读取模型 API 准备度": "Unable to read model API readiness", "未配置": "Not configured", "已检测到配置": "Configuration detected", "未执行": "Not run",
    "完成部署配置后重启 Pilot，再使用“重新检查”读取真实准备度。": "After completing deployment configuration, restart Pilot and use Check again to read actual readiness.",
    "配置存在性已通过；真实模型访问仍需部署 smoke 验证。": "Configuration presence passed; live model access still requires a deployment smoke test.",
    "配置模型 API": "Configure model API", "配置 Marketplace API": "Configure Marketplace API",
    "验证并更换": "Validate and replace", "原会话已保留。": "The previous session was preserved.",
    "use an eai_ API key": "Use a valid eai_ API key.",
    "主题已更新。": "Theme updated.", "语言已切换，但浏览器无法保存偏好。": "Language changed, but the browser could not save the preference.",
    "首次观测": "First observation", "币种未知": "Unknown currency", "观测于": "Observed on", "最新观测": "Latest observation",
    "销售额": "Sales", "转化率": "Conversion rate", "广告花费": "Ad spend", "缺货 SKU": "Out-of-stock SKUs", "订购件数": "Units ordered",
    "影响": "Impact", "Owner": "Owner", "条": "items", "confidence": "confidence", "查看证据": "View Evidence",
    "正在连接": "Connecting", "正在建立经过身份验证的实时事件流。": "Establishing an authenticated live event stream.",
    "实时已连接": "Live connected", "当前还没有新的任务状态事件。": "There are no new task-status events yet.", "最近更新": "Last updated",
    "正在接收真实任务状态。": "Receiving live task status.", "正在重连": "Reconnecting", "连接已中断，将从最后游标继续。": "Connection interrupted; resuming from the last cursor.",
    "实时连接异常": "Live connection error", "无法建立实时事件流。": "Unable to establish the live event stream.", "认证已失效": "Authentication expired",
    "API Key 已从页面内存清除，请重新连接 Runtime。": "The API Key was cleared from page memory. Reconnect Runtime.",
    "LWA 授权": "LWA authorization", "Profile 匹配": "Profile match", "Sponsored Products 只读": "Sponsored Products read access", "外部批准证明": "External approval evidence",
    "阻塞原因": "Blockers", "外部证明": "External evidence", "required Amazon Ads credential is not configured": "Required Amazon Ads credentials are not configured.",
    "Adapter registered": "Adapter registered", "是": "Yes", "否": "No", "写操作": "Write operations", "无": "None", "原因": "Reasons", "未提供原因": "No reason provided",
    "检查于": "Checked at", "当前租户的真实准入评估": "Live access evaluation for the current tenant", "Amazon Ads 写入适配器": "Amazon Ads write adapter",
    "当前构建未注册 Amazon Ads 写操作。此区域仅展示准入锁状态，不提供执行、解锁或写入按钮。": "This build has no registered Amazon Ads write operations. This area displays the access lock only and provides no execute, unlock, or write controls.",
    "尚无 Amazon Ads 账户": "No Amazon Ads account", "尚无 L5 准入记录": "No L5 access record", "L5 Gate 未通过": "L5 gate did not pass", "必需能力不完整": "Required capabilities are incomplete",
    "账户 region 或 Profile 已变化": "Account region or profile changed", "Gate 尚未完成": "Gate is not complete", "账户在 Gate 后已更新": "Account changed after the gate",
    "Gate 已超过 24 小时": "Gate is older than 24 hours", "Gate 时间异常": "Gate timestamp is invalid", "Adapter 未安装": "Adapter is not installed", "写入面已关闭": "Write surface is disabled",
  };
  Object.keys(APP_CATALOG).forEach(key => {
    if (CATALOG["zh-CN"][key] === undefined) CATALOG["zh-CN"][key] = key;
    CATALOG.en[key] = APP_CATALOG[key];
  });
  Object.assign(CATALOG["zh-CN"], {
    "Agent Brief": "智能体简报", "Agent Operations": "智能体运营", "Agent 协作中": "智能体协作中", "Assurance Center": "保障中心",
    "Runtime 未连接": "运行时未连接", "Runtime 已连接": "运行时已连接", "连接 Runtime": "连接运行时", "真实 Evidence 趋势": "真实证据趋势",
    "在一个位置管理当前 Runtime 会话、Marketplace API、模型 API 准备度和报告同步配置。": "在一个位置管理当前运行时会话、平台 API、模型 API 准备度和报告同步配置。",
    "API Key 只保存在当前页面内存，不写入浏览器存储或 Runtime 数据库。": "API 密钥只保存在当前页面内存，不写入浏览器存储或运行时数据库。",
    "连接或更换 Key": "连接或更换密钥",
    "请输入 API Key": "请输入 API 密钥", "已连接。API Key 仅保存在当前页面内存。": "已连接。API 密钥仅保存在当前页面内存。",
    "use an eai_ API key": "请使用有效的 eai_ API 密钥。",
    "Runtime API Key 只存在于当前页面内存；刷新或断开后清除。": "运行时 API 密钥只存在于当前页面内存；刷新或断开后清除。",
    "Marketplace 与模型密钥由部署环境或 Secret Manager 提供。": "平台与模型密钥由部署环境或密钥管理器提供。",
    "Presence 只表示配置项存在，不代表模型访问已通过真实调用验证。当前版本没有浏览器端“测试 OpenAI”按钮。": "配置存在只表示配置项已提供，不代表模型访问已通过真实调用验证。当前版本没有浏览器端“测试 OpenAI”按钮。",
    "连接 Runtime API Key 后显示当前租户与角色。": "连接运行时 API 密钥后显示当前租户与角色。",
    "连接后读取模型 API 的部署准备度。": "连接后读取模型 API 的部署准备度。", "配置 Marketplace API": "配置平台 API",
    "查看全部 Runs": "查看全部运行记录", "等待 Evidence": "等待证据", "Evidence 类型": "证据类型", "Evidence report type": "证据报表类型",
    "所有指标、Evidence、Agent 结论和审批均为演示数据，不可用于真实经营决策。": "所有指标、证据、智能体结论和审批均为演示数据，不可用于真实经营决策。",
    "Adapter registered": "适配器已注册", "required Amazon Ads credential is not configured": "尚未配置必需的 Amazon Ads 凭据。",
    "L5 Gate 未通过": "L5 准入未通过", "账户 region 或 Profile 已变化": "账户区域或 Profile 已变化", "Gate 尚未完成": "准入检查尚未完成",
    "账户在 Gate 后已更新": "账户在准入检查后已更新", "Gate 已超过 24 小时": "准入检查已超过 24 小时", "Gate 时间异常": "准入检查时间异常",
    "Adapter 未安装": "适配器未安装", "写入面已关闭": "写入能力已关闭",
  });
  function markStorageUnavailable() {
    if (global.document && global.document.documentElement) global.document.documentElement.setAttribute("data-locale-storage", "unavailable");
  }
  function getLocale() {
    try { return locale(global.localStorage.getItem(STORAGE_KEY)); }
    catch (_) { markStorageUnavailable(); return memoryLocale || "zh-CN"; }
  }
  function setLocale(value) {
    const next = locale(value);
    // Keep the selection effective for this page even when storage is blocked.
    memoryLocale = next;
    try {
      global.localStorage.setItem(STORAGE_KEY, next);
      if (global.document && global.document.documentElement) global.document.documentElement.removeAttribute("data-locale-storage");
    } catch (_) { markStorageUnavailable(); }
    apply(global.document);
    return next;
  }
  function translate(text, targetLocale) {
    const value = String(text ?? "");
    const active = CATALOG[locale(targetLocale)];
    if (active[value] !== undefined) return active[value];
    // Translate only machine-shaped counters; arbitrary/user text is untouched.
    const match = value.match(/^(\d+)\s+(present|checks passed|sources|rows|sources\/rows)$/i);
    if (match) return `${match[1]} ${active[match[2].toLowerCase()]}`;
    return value;
  }
  function apply(root) {
    const doc = root || global.document;
    if (!doc) return;
    const active = getLocale();
    if (doc.documentElement) {
      doc.documentElement.lang = active;
      const currentTitle = String(doc.title || "");
      let titleState = titleSources.get(doc);
      if (!titleState) titleState = {source: currentTitle, lastTranslated: currentTitle};
      else if (currentTitle !== titleState.lastTranslated) titleState.source = currentTitle;
      doc.title = translate(titleState.source, active);
      titleState.lastTranslated = doc.title;
      titleSources.set(doc, titleState);
    }
    const walker = doc.createTreeWalker(doc.body || doc, 4);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      if (node.parentElement && /^(SCRIPT|STYLE|CODE|PRE)$/i.test(node.parentElement.tagName)) return;
      const value = node.nodeValue;
      if (!value || !value.trim()) return;
      const trimmed = value.trim();
      let state = textSources.get(node);
      if (!state) state = {source: trimmed, lastTranslated: trimmed};
      else if (trimmed !== state.lastTranslated) state.source = trimmed;
      const translated = translate(state.source, active);
      node.nodeValue = value.replace(trimmed, translated);
      state.lastTranslated = translated;
      textSources.set(node, state);
    });
    (doc.querySelectorAll ? doc.querySelectorAll("[aria-label], [title], [placeholder]") : []).forEach(node => {
      ["aria-label", "title", "placeholder"].forEach(attr => {
        if (!node.hasAttribute(attr)) return;
        const value = node.getAttribute(attr), key = `${attr}`;
        let states = attributeSources.get(node);
        if (!states) { states = {}; attributeSources.set(node, states); }
        let state = states[key];
        if (!state) state = states[key] = {source: value, lastTranslated: value};
        else if (value !== state.lastTranslated) state.source = value;
        const translated = translate(state.source, active);
        node.setAttribute(attr, translated);
        state.lastTranslated = translated;
      });
    });
  }
  global.CommerceI18n = Object.freeze({ SUPPORTED, CATALOG, STORAGE_KEY, getLocale, setLocale, translate, apply });
})(window);
