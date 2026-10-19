from __future__ import annotations

from claude_kit import doctor
from claude_kit.paths import Paths


def test_a_jq_with_a_known_bug_fails_with_the_reason() -> None:
    finding = doctor.jq_finding("jq-1.8.2")
    assert finding.level == "fail"
    assert "jqlang/jq/issues/3636" in finding.message


def test_a_missing_jq_fails_and_a_working_one_passes() -> None:
    assert doctor.jq_finding(None).level == "fail"
    assert doctor.jq_finding("jq-1.7.1-apple").level == "ok"


def test_tools_checks_the_jq_the_status_line_runs(paths: Paths) -> None:
    jq = [finding for finding in doctor.tools(paths) if finding.message.startswith("jq")]
    assert [finding.level for finding in jq] == ["ok"]
