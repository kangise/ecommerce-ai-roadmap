# Constraints: ecom-customer-service

Generated from `ontology/constraints.yaml`.

- **amazon.violation.response_deadline**: 收到 Amazon 政策违规通知须及时响应（通常 48-72 小时），超时可能导致更严重处罚 (verified 2026-08)
- **amazon.safety_complaint.response_deadline**: 所有产品安全相关投诉必须在 24 小时内响应，否则可能导致 Listing 下架 (verified 2026-08)
- **amazon.listing.forbidden_unverified_claim**: Listing 中禁止使用未经验证的声明（如宣称 "FDA approved" 但实际没有 FDA 批准）；健康声明需认证依据 (verified 2026-08)
- **content.ai_generated.commercial_license**: 商业使用 AI 生成内容时优先选择明确授予商业许可的付费工具（免费工具权利归属不确定），保留 Prompt 与生成记录作为创作证据 (verified 2026-08)

## How to Apply in Customer Service

1. **响应时限**: 申诉（Plan of Action）与违规通知响应按 `amazon.violation.response_deadline` 卡死 48-72 小时；产品安全相关投诉按 `amazon.safety_complaint.response_deadline` 必须在 24 小时内响应。生成申诉信和差评回复时，把时限写进自检清单。
2. **对外承诺边界**: 所有面向客户的回复、邮件、模板（差评回复、Review 请求、FAQ、多语言模板）不得写入退款金额、赔偿、时效、平台政策例外等未授权承诺，也不得虚构产品不具备的功能/认证——对应 `amazon.listing.forbidden_unverified_claim`。客户能看到的文字就是 Listing 的一部分。
3. **AI 生成内容商用**: 用 AI 生成客服模板并用于商业回复时，优先使用明确授予商业许可的工具，并保留 Prompt 与生成记录——对应 `content.ai_generated.commercial_license`。
