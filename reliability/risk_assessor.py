from typing import Dict, List


def assess_risk(
    original_code: str,
    fixed_code: str,
    issues: List[Dict[str, str]],
) -> Dict[str, object]:
    """
    Simple, explicit risk assessment used as a guardrail layer.

    Returns a dict with:
    - score: int from 0 to 100 (equals fix_safety_score)
    - level: "low" | "medium" | "high"
    - reasons: list of strings explaining deductions
    - should_autofix: bool
    - issue_severity_score: int from 0 to 100
    """

    reasons: List[str] = []

    if not fixed_code.strip():
        return {
            "score": 0,
            "level": "high",
            "reasons": ["No fix was produced."],
            "should_autofix": False,
            "issue_severity_score": 100,
        }

    original_lines = original_code.strip().splitlines()
    fixed_lines = fixed_code.strip().splitlines()

    # ----------------------------
    # Fix safety score (structural)
    # ----------------------------
    fix_safety_score = 100

    if len(fixed_lines) < len(original_lines) * 0.5:
        fix_safety_score -= 20
        reasons.append("Fixed code is much shorter than original.")

    if "return" in original_code and "return" not in fixed_code:
        fix_safety_score -= 30
        reasons.append("Return statements may have been removed.")

    if "except:" in original_code and "except:" not in fixed_code:
        fix_safety_score -= 5
        reasons.append("Bare except was modified, verify correctness.")

    fix_safety_score = max(0, min(100, fix_safety_score))

    # ----------------------------
    # Issue severity score
    # ----------------------------
    issue_severity_score = 100

    for issue in issues:
        severity = str(issue.get("severity", "")).lower()

        if severity == "high":
            issue_severity_score -= 40
            reasons.append("High severity issue detected.")
        elif severity == "medium":
            issue_severity_score -= 20
            reasons.append("Medium severity issue detected.")
        elif severity == "low":
            issue_severity_score -= 5
            reasons.append("Low severity issue detected.")

    issue_severity_score = max(0, issue_severity_score)

    # ----------------------------
    # Risk level (from fix safety only)
    # ----------------------------
    if fix_safety_score >= 75:
        level = "low"
    elif fix_safety_score >= 40:
        level = "medium"
    else:
        level = "high"

    # ----------------------------
    # Auto-fix policy
    # ----------------------------
    should_autofix = fix_safety_score >= 75 and issue_severity_score >= 60

    if not reasons:
        reasons.append("No significant risks detected.")

    return {
        "score": fix_safety_score,
        "level": level,
        "reasons": reasons,
        "should_autofix": should_autofix,
        "issue_severity_score": issue_severity_score,
    }
