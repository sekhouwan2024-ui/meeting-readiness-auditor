# 过会排雷

[English README](README.md)

一个开源 Codex Skill：把 PPT 中的结论与底层 Excel、CSV、Word、PDF 证据逐项核对，先修正会前可以确认的问题，再准备真正会被追问的原因、判断、取舍、行动和风险。

适用于经营复盘、销售汇报、项目汇报、客户方案和管理层评审。当前工作流针对中文业务材料和中文输出做了优化。

## 能做什么

- 将 PPTX、XLSX/XLSM、CSV、DOCX、PDF 提取为本地可查询的证据工作区；
- 核对数字、公式、口径、时间窗口、单位、图表结论和跨文件一致性；
- 区分确定错误、口径风险、逻辑缺口、视觉风险、重要遗漏和待调查异常；
- 生成交互式排雷报告、手机端模拟过会、协作 XLSX 和一页答辩小抄；
- 用确定性脚本负责抽取与校验，用 Agent 负责有证据边界的业务判断。

## 隐私说明

仓库内脚本只在本地处理文件，不主动上传源材料。但你使用的 Agent 运行环境可能有自己的数据处理规则，处理机密文件前请先确认。生成的工作区可能包含业务数据和本机绝对路径，默认不要提交到 Git，并按组织的数据保留要求及时清理。

## 安装到 Codex

```bash
git clone https://github.com/sekhouwan2024-ui/meeting-readiness-auditor.git
cd meeting-readiness-auditor
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skill/meeting-readiness-auditor" ~/.codex/skills/meeting-readiness-auditor
```

重启 Codex 后可以这样调用：

```text
使用 $meeting-readiness-auditor 核对这份汇报和底层资料，并帮我准备过会答辩。
```

完整的本地冒烟测试命令、目录结构、贡献方式和限制说明见 [English README](README.md)。

## 重要边界

本 Skill 是会前辅助审查工具，不替代正式财务审计、法律意见或管理层决策。扫描件、图片化图表、复杂嵌入对象、宏和专业会计规则仍可能需要人工或专业人员复核。所有生成结论都应由汇报负责人确认。

## 许可证

[MIT](LICENSE)
