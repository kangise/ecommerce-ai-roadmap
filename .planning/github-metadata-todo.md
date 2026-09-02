# GitHub 元数据更新清单

**agent 改不了，需要仓库主人在 Settings 里手动操作。**

最后核对：2026-09-03（数字由 `scripts/verify_all.py --d2` 的口径实测得出）

## About 描述 —— 待改

当前线上描述里的数字是旧的：

| | 描述现写 | 实际 |
|---|---|---|
| entities | 94 | **100** |
| constraints | 318 | **322** |

其余（69 chapters / 878 prompts / 9 skills）正确。

> 讽刺的是，README 里的同样数字有 `D2` 门禁盯着，仓库描述在 GitHub 设置里，门禁够不着。
> 每次 ontology 增删后都要手动来核一遍。

建议改成：

```
Cross-border e-commerce AI knowledge base, designed to be read by people and installed by agents. 69 trilingual guides, 878 structured prompts, a 100-entity / 322-constraint domain ontology, and 9 agent skills served over MCP. Factual claims are dated and CI-verified; prompts declare their data requirements and failure boundaries. CC0.
```

## Topics —— 已完成

19 个 topic 已配置，早先的拼写问题已修，无需再动。

## 主页 —— 已完成

已指向 https://kangise.github.io/ecommerce-ai-skills/

## Social Preview —— 待办

仍未上传。Settings → Social preview，建议用 `assets/` 下的全景图导出 1280×640 PNG。

## 发布 —— 待办

远端只有 `v1.0.0`、`v1.1.0` 两个 tag，且 **Releases 页面是空的**（tag 存在但没建 Release）。
`pyproject.toml` 已到 `1.3.0`，v1.2.0 与 v1.3.0 从未打过 tag。

后果：`release.yml` 里的 PyPI 发布 job 绑在 `push: tags: ["v*"]`，**从未被触发过**。

打 tag 之前要先做的一次性配置：

1. PyPI 上为本仓库注册 trusted publisher
   （workflow = `release.yml`，environment = `pypi`）
2. GitHub 的 `pypi` environment 里加必需审阅人
   —— PyPI 上传不可撤销，一个版本号用掉就没了

两步做完再打 `v1.3.0`，整条发布链路才走得通。
