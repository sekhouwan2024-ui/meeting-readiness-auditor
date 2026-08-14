---
name: meeting-readiness-auditor
description: Audit business presentations before high-stakes review meetings by checking PPTX claims against XLSX, CSV, DOCX, and PDF evidence. Use for management reviews, operating reviews, sales reports, project updates, and client proposals that need cross-file verification of numbers, formulas, definitions, charts, conclusions, disclosure, attribution, segment quality, execution readiness, and key assumptions. Produce evidence-grounded fixes, likely follow-up questions, data requests, an interactive report, and a rehearsal-ready meeting simulation. Optimized for Chinese-language business materials and outputs.
---

# 过会排雷

把汇报材料处理成一套“过会备战包”：先处理可确认的问题，再推演真正会被追问的原因、判断、取舍、行动和风险。不要用话术解释本可提前修掉的数据错误。

## 工作原则

1. 以底层证据为准，不以PPT中的说法为准。
2. 把事实、解释、假设和建议明确分开。
3. 确定错误必须可定位、可复算、可修正；未发现确定错误是完全有效的结果，不得为了排雷强行挑错。
4. 数据错误先进入“会前处理”，修正后不得作为正式追问重复出现。
5. 材料不足时说“目前无法判断”，并列出需要补充的资料。
6. 不编造数字、原因、负责人或已完成动作，不替用户掩盖负面事实。
7. 输出以交互式HTML报告和逐题模拟会议为主，不在聊天中堆叠长篇分析。
8. 模拟会议不虚构“AI评分”；用户先自行作答，再对照证据型建议回答。
9. 不在运行中临时修改脚本、猜测JSON字段或用一次性代码修补流程。

## 用户可见进度

最多显示以下四个简短阶段，不输出内部计划、依赖检查或数据库结构：

1. 正在读取汇报和底层资料。
2. 正在核验数字、口径和图表。
3. 正在生成高风险追问与补数清单。
4. 正在整理过会报告和模拟会议。

脚本失败时停止，简洁说明失败文件与步骤。不要现场修改Skill脚本后重试。

## 固定工作流

### 1. 明确会议上下文

从用户材料或请求中确定：

- 会议类型与目标。
- 主要参会角色。
- 汇报文件与底层证据文件。
- 是否需要特定角色视角；若未指定，默认使用老板 + 财务 + 业务负责人组合。

仅在缺少会显著影响审查结果的信息时提问，其他情况直接开始。

### 2. 建立证据工作区

只运行打包脚本：

```bash
python scripts/prepare_materials.py <文件或目录...> --out <工作目录>
python scripts/validate_workspace.py <工作目录>
```

工作区契约见`references/source-schema.md`。

首次分析只读取：

- `inventory.json`
- `analysis_packet.json`
- 必要的PPT预览图

禁止读取或生成单体`source_bundle.json`。禁止把全部Excel单元格或数据库内容加载进上下文。

需要核验证据时，按关键词或位置聚焦查询：

```bash
python scripts/query_evidence.py <工作目录> --query <关键词> --limit 30
```

可按`--type`、`--file-id`、`--page`或`--sheet`缩小范围。每次查询只服务于当前结论或问题。

### 3. 建立证据地图

把PPT中的关键数字、标题结论、图表、目标和行动计划映射到底层数据、口径说明和其他证据。优先定位到文件、页码/工作表、单元格或图表对象。

审计时读取：

- 通用规则：`references/audit-rules.md`
- 证据与严重程度：`references/evidence-standard.md`
- 涉及特定业务时：`references/domain-lenses.md`
- 数字基本正确但仍需深入审查时：`references/subtle-risk-patterns.md`

### 4. 阶段A：会前处理

检查并分类：

- 计算与公式。
- 时间、单位、对象、状态、过滤和去重口径。
- PPT与底层数据一致性。
- 标题、正文、图表和数据方向的一致性。
- 图表尺度、双轴、单位、图例和时间范围。
- 结论支撑、选择性披露、因果推断和行动完整性。
- 观察窗口成熟度、总体与分群差异、归因口径漂移、增长质量和目标关键假设。

为每个发现给出原表述、核验结论、证据、必要时的复算公式和建议处理。若未发现明显算术错误，应明确说明主要风险来自可比性、解释边界、分群、归因或决策准备。不能确认的问题使用`definition_risk`或`needs_investigation`，不要升级成确定错误。

### 5. 建立修正后事实版本

在内部采用建议修正后的数字、口径和结论作为后续推演基础。若某项修正需要用户确认，在报告中明确标记，不要静默修改原文件。

### 6. 阶段B：过会推演

只基于修正后的事实生成问题。读取`references/question-design.md`和`references/simulation-design.md`，从以下角度筛选高价值问题：

- 结果为什么发生。
- 结果是否达到目标、是否可持续。
- 为什么选择当前方案和资源取舍。
- 下一步由谁、何时、以什么指标执行。
- 关键假设、最坏情况和失败预案。

每个问题必须包含：直接回答、证据、当前未知、需要补充的资料和下一层追问。不要把已经修正的计算错误当作正式问题。

把最高价值的问题组织成4—8轮连续模拟会议。每轮指定提问角色、问题意图、回答准备状态、建议回答、会前动作、错误答法和下一层追问。问题逐步深入，不要换句话重复。

### 7. 生成与验证结构化结果

严格按`references/output-schema.md`生成`audit_result.json`。字段名称保持英文，内容使用用户语言。

```bash
python scripts/validate_audit.py <audit_result.json> --write-normalized <audit_validated.json>
```

验证失败时只修复分析JSON，不修改脚本或Schema。对警告人工复核，尤其是过度指控、证据不足和指标命名问题。验证通过后，再做一次跨输出一致性检查：同一指标在执行摘要、发现卡、问题卡、模拟回答和答辩小抄中必须使用同一复算值；PPT页码和原表述必须真实存在。

### 8. 渲染过会备战包

```bash
python scripts/render_report.py <audit_validated.json> --out <输出目录>
```

交付：

- `过会排雷报告.html`：总览、逐页雷区、修正项、模拟过会、追问、答辩小抄和补数清单。
- `模拟过会.html`：适合单独打开和录屏的一题一屏演练页面。页面自动适配竖屏；录制9:16视频时添加`?recording=1`。可使用`&round=S01&reveal=1`直接定位并展开指定轮次。
- 报告支持录屏定位参数：`过会排雷报告.html?tab=fixes&focus=finding-F02`、`?tab=questions&focus=question-Q01`、`?tab=data&focus=gap-D02`。渲染器必须为发现、问题、小抄和补数项生成稳定锚点。
- `会前修正与答辩准备.xlsx`：便于协作和落实的修正、问答与补数工作簿。
- `一页答辩小抄.md`：会前快速复习版本。

聊天回复只摘要最高优先级风险和最需要准备的3个问题，并提供文件链接；不要复制整份报告。

## 质量门槛

交付前确认：

- 工作区通过`validate_workspace.py`。
- 每个确定错误至少有一条直接证据。
- 所有复算通过`validate_audit.py`；总体指标使用加权总体或已验证总览公式，不用单个渠道值或简单平均代替。
- 问题不基于尚未修正的数据错误。
- 模拟过会包含4—8轮递进问题，并且每轮有角色、回答状态、建议回答、会前动作和下一层追问。
- `not_ready`问题明确缺失资料；`decision_needed`问题明确需要谁做什么决策。
- 建议回答没有材料之外的事实断言。
- 需要补充的数据具体到用途、负责人和截止时间。
- HTML在桌面和手机宽度下均可阅读；`模拟过会.html?recording=1`在9:16竖屏视口下不横向溢出，一屏只聚焦当前问题或回答反馈。
- 输出注明AI结果需由汇报负责人复核。

## 边界

本Skill是会前辅助审查，不替代正式财务审计、法律意见或管理层决策。扫描件、复杂嵌入对象和图片化图表可能需要额外视觉检查。未经用户确认，不直接覆盖原PPT或底层数据。
