# audit_result.json 输出结构

在渲染前生成UTF-8 JSON。字段名称保持英文，字段值使用用户语言。

```json
{
  "report_title": "某项目月度经营复盘｜过会准备报告",
  "meeting_context": {
    "meeting_type": "月度经营复盘",
    "audience_roles": ["老板", "财务负责人"],
    "meeting_goal": "确认结果、问题和下月资源决策"
  },
  "summary": {
    "meeting_status": "needs_data",
    "executive_summary": "一句话说明当前准备状态和最大风险"
  },
  "page_risk_map": [
    {"page": 1, "title": "经营概况", "risk": "high", "issue_count": 2}
  ],
  "findings": [
    {
      "id": "F01",
      "title": "总体留存掩盖付费新增质量下降",
      "type": "logic_gap",
      "severity": "high",
      "confidence": "confirmed",
      "location": "PPT第7页｜用户质量",
      "statement": "整体用户质量基本稳定",
      "assessment": "总体D1仅小幅下降，但付费新增D1明显恶化，自然新增改善托住了平均值",
      "evidence": [
        {
          "file": "原始数据.xlsx",
          "page_or_sheet": "经营总览",
          "cell_or_object": "B4:C4",
          "value_or_quote": "上期200，本期246"
        }
      ],
      "recommended_fix": "增加自然与付费分群，避免仅用总体平均值判断用户质量"
    }
  ],
  "questions": [
    {
      "id": "Q01",
      "priority": "high",
      "question": "增长主要由什么驱动，是否可持续？",
      "why_it_may_be_asked": "规模增长同时伴随成本和质量压力",
      "direct_answer": "先给出基于修正后事实的直接回答",
      "evidence": [],
      "unknowns": ["尚缺少渠道级拆分"],
      "next_question": "如果核心驱动消失，下月结果会怎样？",
      "based_on_unfixed_error": false
    }
  ],
  "simulation": {
    "title": "模拟过会｜老板 + 财务 + 业务负责人",
    "opening": "请先用自己的话回答，再对照建议答案和证据。",
    "rounds": [
      {
        "id": "S01",
        "role": "老板",
        "question": "投放费用增长45%，新增用户只增长20%，为什么5月还值得继续投入？",
        "intent": "判断继续投入的边际回报和资源取舍",
        "answer_status": "partial",
        "suggested_answer": "不建议按4月方式继续整体扩量。现有数据支持先控制低质量扩量，再根据渠道级留存和付费质量决定预算。",
        "evidence": [
          {
            "file": "原始数据.xlsx",
            "page_or_sheet": "用户与投放",
            "cell_or_object": "B5:C7",
            "value_or_quote": "费用+45%；新增+20%；CAC上升"
          }
        ],
        "unknowns": ["渠道级留存", "自然新增占比"],
        "prep_action": "会前补齐渠道级新增、CAC、D1/D7留存和付费转化。",
        "follow_up_question": "如果必须今天削减20%预算，你会先削哪个渠道？",
        "avoid_answer": "整体增长不错，后续继续优化。"
      }
    ],
    "summary": {
      "total_rounds": 5,
      "ready": 1,
      "partial": 3,
      "not_ready": 1,
      "decision_needed": 0
    }
  },
  "data_requests": [
    {
      "item": "渠道级新增和留存",
      "reason": "判断获客成本上升来自哪个渠道",
      "priority": "会前必须",
      "owner": "待指定",
      "deadline": "会前2小时"
    }
  ]
}
```

## 枚举约束

- `summary.meeting_status`：`needs_fix`、`needs_data`、`ready_for_rehearsal`、`ready_with_caveats`
- `findings[].type`：`confirmed_error`、`definition_risk`、`logic_gap`、`visual_risk`、`important_omission`、`needs_investigation`
- `severity`与`priority`：`critical`、`high`、`medium`、`low`
- `confidence`：`confirmed`、`likely`、`uncertain`
- `simulation.rounds[].answer_status`：`ready`、`partial`、`not_ready`、`decision_needed`

## 模拟过会要求

- 必须生成4—8轮。
- 只基于修正后的事实，不重复追问已修正的计算错误。
- 问题顺序从结果逐步深入到原因、取舍、行动和风险。
- `not_ready`至少有一项`unknowns`和明确`prep_action`。
- `decision_needed`的`prep_action`说明需要哪类决策。
- `suggested_answer`可在20—45秒内口头表达，不写成长篇报告。
- `avoid_answer`是材料中常见但无效的空泛、回避或无证据答法。

不要生成模糊的0—100“准备度评分”。总览只使用可核验的修正项、待补数据和模拟问题数量。

## HTML稳定定位约定

渲染器为录屏和复核生成稳定锚点：

- 发现卡：`finding-F01`
- 问题卡：`question-Q01`
- 答辩小抄：`cheat-Q01`
- 补数行：`gap-D01`
- 模拟会议：`simulation-stage`、`simulation-question`、`simulation-answer`、`simulation-action`、`simulation-evidence`、`simulation-unknowns`、`simulation-followup`

报告支持`?tab=fixes&focus=finding-F01`等定位参数；模拟页面支持`?recording=1&round=S01&reveal=1`。这些锚点不得随视觉样式调整而改名。
