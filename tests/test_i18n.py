import json
import re
import subprocess
from pathlib import Path
from html.parser import HTMLParser


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "ecommerce_ai_skills/runtime/web/i18n.js"


def _catalogs():
    script = """
      global.window = {localStorage: {getItem: () => null, setItem: () => {}}};
      global.document = undefined;
      require(process.argv[1]);
      process.stdout.write(JSON.stringify(window.CommerceI18n.CATALOG));
    """
    result = subprocess.run(["node", "-e", script, str(I18N)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_bilingual_catalog_is_symmetric_and_nonempty():
    catalogs = _catalogs()
    assert set(catalogs) == {"zh-CN", "en"}
    assert set(catalogs["zh-CN"]) == set(catalogs["en"])
    assert all(isinstance(v, str) and v.strip() for locale in catalogs.values() for v in locale.values())
    assert all("Localized interface copy" not in v for locale in catalogs.values() for v in locale.values())
    assert all(not re.search(r"[\u4e00-\u9fff]", value) for value in catalogs["en"].values())
    assert len(catalogs["zh-CN"]) == len(set(catalogs["zh-CN"]))


def test_required_status_terms_and_product_surface_are_present():
    catalogs = _catalogs()
    required = {"connected", "disconnected", "pending", "running", "completed", "failed", "blocked", "approved", "rejected", "expired", "viewer", "operator", "admin", "owner", "需要 admin 或 owner 角色", "创建提案", "导入 Evidence"}
    assert required <= set(catalogs["zh-CN"])
    assert required <= set(catalogs["en"])
    # Brand/API names are not translated; generic Evidence remains a deliberate
    # product term in the UI, so it is allowed as a phrase key.
    # Runtime is a deliberate product term; brands and credential labels remain
    # stable and are only translated when embedded in a larger UI phrase.
    assert {"Amazon", "Shopify", "API Key"}.isdisjoint(set(catalogs["zh-CN"]))


class _VisibleSurface(HTMLParser):
    """Collect fixed user-facing HTML copy, excluding code/data containers."""
    def __init__(self):
        super().__init__(); self.skip = 0; self.values = set()
    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "code", "pre"}: self.skip += 1
        if not self.skip:
            for name, value in attrs:
                if name in {"aria-label", "title", "placeholder"} and value and re.search(r"[\u4e00-\u9fff]", value):
                    self.values.add(value.strip())
    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "code", "pre"} and self.skip: self.skip -= 1
    def handle_data(self, data):
        value = data.strip()
        if not self.skip and value and re.search(r"[\u4e00-\u9fff]", value): self.values.add(value)


def test_mission_control_fixed_cjk_surface_has_english_catalog_coverage():
    parser = _VisibleSurface()
    parser.feed((ROOT / "ecommerce_ai_skills/runtime/web/mission-control.html").read_text(encoding="utf-8"))
    catalogs = _catalogs()
    # Templates and JSON payloads are data, not fixed UI copy.
    fixed = {value for value in parser.values if not value.startswith("{") and "${" not in value}
    missing = sorted(value for value in fixed if value not in catalogs["en"])
    assert not missing, f"missing en catalog entries: {missing}"
    assert all(not re.search(r"[\u4e00-\u9fff]", catalogs["en"][value]) for value in fixed)


def test_key_app_feedback_and_permission_copy_has_english_coverage():
    catalogs = _catalogs()
    required = {"暂无同步活动", "暂无后台任务", "暂无行动提案", "无法加载提案", "界面语言已更新。", "提案已提交审批。", "健康检查已完成。", "需要 admin 或 owner 角色"}
    assert required <= set(catalogs["zh-CN"]) == set(catalogs["en"])
    assert all(not re.search(r"[\u4e00-\u9fff]", catalogs["en"][key]) for key in required)


def test_common_navigation_theme_and_recovery_terms_are_bilingual():
    catalogs = _catalogs()
    required = {"Agents", "Evidence", "Connections", "Connection Center", "Runtime", "Marketplace", "AI", "Reports", "Light", "Dark", "加载失败", "保存失败", "连接失败", "修复", "立即修复"}
    assert required <= set(catalogs["zh-CN"]) | set(catalogs["en"])
    assert catalogs["zh-CN"]["Agents"] == "智能体"
    assert catalogs["zh-CN"]["Evidence"] == "证据"
    assert catalogs["zh-CN"]["Light"] == "浅色"
    assert catalogs["en"]["Light"] == "Light"
    assert catalogs["zh-CN"]["Marketplace connection"] == "平台连接"
    assert catalogs["zh-CN"]["Runtime API"] == "运行时 API"
    assert catalogs["en"]["连接 Amazon SP-API、Amazon Ads 与 Shopify；保存环境变量引用，不保存密钥值。"].startswith("Connect Amazon SP-API")


def test_javascript_syntax_and_locale_storage_is_non_sensitive():
    result = subprocess.run(["node", "--check", str(I18N)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    source = I18N.read_text(encoding="utf-8")
    assert "localStorage.setItem(STORAGE_KEY, next)" in source
    assert "apiKey" not in source
    assert "API_KEY" not in source
    assert "sessionStorage" not in source


def test_dom_apply_round_trips_and_tracks_dynamic_text():
    script = r'''
      const fs = require("fs");
      let stored = "zh-CN";
      const html = {lang: "", attrs: {}, setAttribute(k, v) { this.attrs[k] = v; }, removeAttribute(k) { delete this.attrs[k]; }};
      const text = {nodeValue: "今日简报", parentElement: {tagName: "DIV"}};
      const button = {attrs: {"aria-label": "主导航"}, hasAttribute(k) { return k in this.attrs; }, getAttribute(k) { return this.attrs[k]; }, setAttribute(k, v) { this.attrs[k] = v; }};
      const doc = {title: "Commerce Agent OS · 今日简报", documentElement: html, body: {},
        createTreeWalker() { let done = false; return {nextNode() { if (done) return false; done = true; this.currentNode = text; return true; }}; },
        querySelectorAll() { return [button]; }};
      global.window = {document: doc, localStorage: {getItem() { return stored; }, setItem(k, v) { stored = v; }}};
      require(process.argv[1]);
      window.CommerceI18n.setLocale("en");
      if (text.nodeValue !== "Daily Briefing" || doc.title !== "Commerce Agent OS · Daily Briefing" || button.attrs["aria-label"] !== "Main navigation") process.exit(2);
      window.CommerceI18n.setLocale("zh-CN");
      if (text.nodeValue !== "今日简报" || doc.title !== "Commerce Agent OS · 今日简报" || button.attrs["aria-label"] !== "主导航") process.exit(3);
      text.nodeValue = "查看今日简报";
      window.CommerceI18n.apply(doc);
      if (text.nodeValue !== "查看今日简报") process.exit(4);
    '''
    result = subprocess.run(["node", "-e", script, str(I18N)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_dynamic_counters_translate_without_touching_user_data():
    script = r'''
      global.window = {localStorage: {getItem: () => null, setItem: () => {}}};
      require(process.argv[1]);
      const i = window.CommerceI18n;
      if (i.translate("12 present", "zh-CN") !== "12 存在") process.exit(2);
      if (i.translate("3 checks passed", "zh-CN") !== "3 检查项通过") process.exit(3);
      if (i.translate("4 sources", "en") !== "4 Sources") process.exit(4);
      if (i.translate("customer sources", "zh-CN") !== "customer sources") process.exit(5);
    '''
    result = subprocess.run(["node", "-e", script, str(I18N)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_storage_failure_is_visible_in_document_state():
    script = r'''
      const html = {attrs: {}, setAttribute(k, v) { this.attrs[k] = v; }};
      global.window = {document: {documentElement: html}, localStorage: {getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); }}};
      require(process.argv[1]);
      window.CommerceI18n.getLocale();
      if (html.attrs["data-locale-storage"] !== "unavailable") process.exit(2);
    '''
    result = subprocess.run(["node", "-e", script, str(I18N)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_storage_failure_keeps_locale_in_memory_for_current_page():
    script = r'''
      const html = {attrs: {}, lang: "", setAttribute(k, v) { this.attrs[k] = v; }, removeAttribute() {}};
      const text = {nodeValue: "今日简报", parentElement: {tagName: "DIV"}};
      const doc = {title: "Commerce Agent OS · 今日简报", documentElement: html, body: {},
        createTreeWalker() { let done = false; return {nextNode() { if (done) return false; done = true; this.currentNode = text; return true; }}; },
        querySelectorAll() { return []; }};
      global.window = {document: doc, localStorage: {getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); }}};
      require(process.argv[1]);
      window.CommerceI18n.setLocale("en");
      if (window.CommerceI18n.getLocale() !== "en" || text.nodeValue !== "Daily Briefing" || html.attrs["data-locale-storage"] !== "unavailable") process.exit(2);
    '''
    result = subprocess.run(["node", "-e", script, str(I18N)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
