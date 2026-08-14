from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "meeting-readiness-auditor" / "scripts"


class EndToEndTests(unittest.TestCase):
    def run_script(self, script: Path, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(arg) for arg in args)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_prepare_query_validate_and_render(self) -> None:
        with tempfile.TemporaryDirectory(prefix="meeting-readiness-test-") as temp:
            temp_path = Path(temp)
            inputs = temp_path / "inputs"
            workspace = temp_path / "workspace"
            report = temp_path / "report"
            self.run_script(ROOT / "examples" / "create_demo_materials.py", "--out", inputs)
            prepared = self.run_script(
                SCRIPTS / "prepare_materials.py",
                inputs,
                "--out",
                workspace,
                "--no-render",
            )
            self.assertTrue(json.loads(prepared.stdout)["ok"])
            validated_workspace = self.run_script(SCRIPTS / "validate_workspace.py", workspace)
            self.assertTrue(json.loads(validated_workspace.stdout)["valid"])
            query = self.run_script(SCRIPTS / "query_evidence.py", workspace, "--query", "Revenue")
            self.assertGreater(json.loads(query.stdout)["returned_count"], 0)
            audit = ROOT / "examples" / "audit_result.example.json"
            validated_audit = self.run_script(SCRIPTS / "validate_audit.py", audit)
            self.assertTrue(json.loads(validated_audit.stdout)["valid"])
            self.run_script(SCRIPTS / "render_report.py", audit, "--out", report)
            self.assertTrue((report / "过会排雷报告.html").exists())
            self.assertTrue((report / "模拟过会.html").exists())
            self.assertTrue((report / "会前处理与答辩准备.xlsx").exists())
            self.assertTrue((report / "一页答辩小抄.md").exists())


if __name__ == "__main__":
    unittest.main()
