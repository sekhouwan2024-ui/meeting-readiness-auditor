# 运行环境与兼容性

脚本使用Python 3，并按实际输入类型加载依赖：

- PPTX：`python-pptx`
- XLSX/XLSM：`openpyxl`
- DOCX：`python-docx`
- PDF：`pypdf`

PPT预览可选使用LibreOffice与`pdftoppm`。预览工具不可用时，结构化提取仍可继续，但图片化图表和截图表格必须人工查看原页面。

## 固定命令

```bash
python scripts/prepare_materials.py /path/to/materials --out /path/to/work
python scripts/validate_workspace.py /path/to/work
python scripts/query_evidence.py /path/to/work --query <关键词> --limit 30
python scripts/validate_audit.py /path/to/work/audit_result.json --write-normalized /path/to/work/audit_validated.json
python scripts/render_report.py /path/to/work/audit_validated.json --out /path/to/output
```

不要运行临时Python片段来猜测数据结构。不要在用户可见回复中逐项汇报Python版本、依赖检查、工作目录或数据库内部实现。
