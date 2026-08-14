# 证据工作区 Schema 2.0

`prepare_materials.py`建立一个稳定工作区。不要把全部源内容重新读入对话。

## 固定产物

- `workspace_manifest.json`：产物路径与记录计数。
- `inventory.json`：文件清单、角色提示、提取状态和警告。
- `analysis_packet.json`：供模型首次审阅的紧凑摘要。
- `evidence.sqlite`：完整证据库，仅通过`query_evidence.py`查询。
- `previews/`：可用时生成的PPT页面预览。

所有JSON和数据库均使用`schema_version: "2.0"`。

## 统一字段

### 文件

- `file_id`：稳定的本次工作区文件标识。
- `file_name`：原始文件名。
- `file_type`：`pptx`、`xlsx`、`csv`、`docx`或`pdf`。
- `role_hint`：`report_candidate`、`data_candidate`、`definition_candidate`或`supporting_material`。

### PPT证据

- `page`：1开始的页码。
- `block_type`：`text`、`notes`、`table`或`chart`。
- `object_name`：PPT对象名。
- `text_content`：可搜索文本。
- `json_payload`：表格或图表的结构化数据。

### 表格证据

字段名称固定为：

- `sheet_name`，不得使用`sheet`或`name`代替。
- `address`，例如`B12`。
- `row_index`、`column_index`。
- `value_text`、`numeric_value`、`formula`、`number_format`。

`spreadsheet_cells`始终是一行一个单元格的数据库表，不存在“有时是列表、有时是字典”的变体。

## 查询规则

只通过以下命令获取聚焦证据：

```bash
python scripts/query_evidence.py <工作目录> --query GMV --limit 30
python scripts/query_evidence.py <工作目录> --query 投放费用 --type xlsx_cell --limit 30
python scripts/query_evidence.py <工作目录> --file-id <ID> --page 5 --limit 50
```

多个`--query`按AND语义组合。表格查询默认附带相邻一行上下文。

## 禁止事项

- 不生成或读取`source_bundle.json`。
- 不直接把SQLite数据库内容全部导出到上下文。
- 不在运行中猜测字段名、修改脚本或改变Schema。
- 脚本失败时停止并报告错误，不临场编写修补代码。
