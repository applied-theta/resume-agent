#!/usr/bin/env python3
"""Compute weighted overall scores from individual analysis JSON files.

Usage:
    uv run scripts/compute-scores.py <session-directory>

Reads analysis JSON files from the session directory and computes a weighted
overall score with letter grade. The scoring mode is determined by the presence
of keyword-analysis.json (with-JD vs without-JD weights).

Weights and grade boundaries are loaded from the scoring rubric
(skills/analyze-resume/scoring-rubric.json) as the single source of truth.
"""

import json
import sys
from pathlib import Path

import jsonschema

RUBRIC_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "analyze-resume"
    / "scoring-rubric.json"
)

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "schemas" / "scores-summary.schema.json"
)

# Structure quality score mapping from parsed-resume metadata
STRUCTURE_QUALITY_SCORES: dict[str, float] = {
    "well-structured": 80,
    "well_structured": 80,
    "moderate": 60,
    "unstructured": 35,
}


def load_rubric(
    rubric_path: Path = RUBRIC_PATH,
) -> tuple[dict[str, float], dict[str, float], list[tuple[int, str]]]:
    """Load weights and grade boundaries from the scoring rubric.

    Returns (weights_with_jd, weights_without_jd, grade_boundaries).
    """
    data = json.loads(rubric_path.read_text(encoding="utf-8"))

    weights_with_jd = {
        name: dim["weight"]
        for name, dim in data["weights"]["with_jd"]["dimensions"].items()
    }
    weights_without_jd = {
        name: dim["weight"]
        for name, dim in data["weights"]["without_jd"]["dimensions"].items()
    }
    grade_boundaries = [
        (entry["min_score"], entry["grade"]) for entry in data["grade_mapping"]
    ]

    return weights_with_jd, weights_without_jd, grade_boundaries


def score_to_grade(score: float, grade_boundaries: list[tuple[int, str]]) -> str:
    """Map a numeric score (0-100) to a letter grade."""
    for minimum, grade in grade_boundaries:
        if score >= minimum:
            return grade
    return "F"


def load_analysis_file(path: Path) -> dict | None:
    """Load and parse a JSON analysis file.

    Returns the parsed dict or None if the file is missing or malformed.
    Prints a warning to stderr for malformed files.
    """
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"WARNING: Skipping malformed file {path.name}: {exc}", file=sys.stderr)
        return None


def estimate_structure_score(session_dir: Path) -> float | None:
    """Derive a basic structure/format score from parsed-resume.json metadata.

    Used as a fallback when ATS analysis is unavailable. Returns a score
    (0-100) or None if parsed-resume.json is not available.
    """
    parsed = load_analysis_file(session_dir / "parsed-resume.json")
    if parsed is None:
        return None

    metadata = parsed.get("metadata", {})
    structure_quality = metadata.get("structure_quality", "")
    base_score = STRUCTURE_QUALITY_SCORES.get(structure_quality, 50.0)

    adjustments = 0.0

    # Bonus for having key sections present
    if parsed.get("summary"):
        adjustments += 5.0
    if parsed.get("skills") and any(parsed["skills"].get(k) for k in parsed["skills"]):
        adjustments += 5.0
    if parsed.get("education"):
        adjustments += 3.0

    # Penalty for excessive page count (non-executive)
    page_count = metadata.get("page_count", 1)
    if page_count > 3:
        adjustments -= 10.0
    elif page_count > 2:
        adjustments -= 5.0

    return max(0.0, min(100.0, base_score + adjustments))


def extract_dimension_scores(
    session_dir: Path,
) -> tuple[dict[str, float | None], dict[str, bool]]:
    """Extract individual dimension scores from analysis files.

    Returns a tuple of:
    - dict mapping dimension name to score (or None if unavailable)
    - dict mapping dimension name to True if fallback was used
    """
    scores: dict[str, float | None] = {}
    fallbacks: dict[str, bool] = {}

    # ATS compatibility: overall_score from ats-analysis.json
    ats_data = load_analysis_file(session_dir / "ats-analysis.json")
    if ats_data is not None:
        scores["ats_compatibility"] = ats_data.get("overall_score")
        # Structure format: derived from ATS structure_quality dimension
        dimensions = ats_data.get("dimensions", {})
        structure_quality = dimensions.get("structure_quality", {})
        scores["structure_format"] = structure_quality.get("score")
    else:
        scores["ats_compatibility"] = None
        # Fallback: estimate structure score from parsed-resume.json
        fallback_score = estimate_structure_score(session_dir)
        scores["structure_format"] = fallback_score
        if fallback_score is not None:
            fallbacks["structure_format"] = True

    # Keyword alignment: match_rate from keyword-analysis.json
    keyword_data = load_analysis_file(session_dir / "keyword-analysis.json")
    if keyword_data is not None:
        scores["keyword_alignment"] = keyword_data.get("match_rate")
    else:
        scores["keyword_alignment"] = None

    # Content quality: overall_score from content-analysis.json
    content_data = load_analysis_file(session_dir / "content-analysis.json")
    if content_data is not None:
        scores["content_quality"] = content_data.get("overall_score")
    else:
        scores["content_quality"] = None

    # Strategic positioning: overall_score from strategy-analysis.json
    strategy_data = load_analysis_file(session_dir / "strategy-analysis.json")
    if strategy_data is not None:
        scores["strategic_positioning"] = strategy_data.get("overall_score")
    else:
        scores["strategic_positioning"] = None

    # Market intelligence: overall_score from skills-research.json
    skills_data = load_analysis_file(session_dir / "skills-research.json")
    if skills_data is not None:
        scores["market_intelligence"] = skills_data.get("overall_score")
    else:
        scores["market_intelligence"] = None

    return scores, fallbacks


def validate_result(result: dict) -> None:
    """Validate the result dict against the scores-summary JSON Schema.

    Prints a warning to stderr if validation fails but does not abort.
    """
    if not SCHEMA_PATH.exists():
        return
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=result, schema=schema)
    except (json.JSONDecodeError, jsonschema.ValidationError) as exc:
        print(
            f"WARNING: scores-summary self-validation failed: {exc}",
            file=sys.stderr,
        )


def compute_scores(session_dir: Path) -> dict:
    """Compute the weighted overall score and build the summary dict.

    Raises SystemExit on fatal errors (no session dir, no usable scores).
    """
    if not session_dir.is_dir():
        print(f"ERROR: Session directory not found: {session_dir}", file=sys.stderr)
        sys.exit(1)

    weights_with_jd, weights_without_jd, grade_boundaries = load_rubric()

    dimension_scores, fallbacks = extract_dimension_scores(session_dir)

    # Determine scoring mode based on keyword-analysis.json presence
    has_keyword = (session_dir / "keyword-analysis.json").exists()
    base_weights = weights_with_jd if has_keyword else weights_without_jd
    weights_used = "with_jd" if has_keyword else "without_jd"

    # Filter to dimensions that have valid scores
    available: dict[str, tuple[float, float]] = {}
    for dim_name, weight in base_weights.items():
        score = dimension_scores.get(dim_name)
        if score is not None:
            available[dim_name] = (score, weight)

    if not available:
        print(
            "ERROR: No analysis files found with valid scores in "
            f"{session_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    # If some dimensions are missing, redistribute their weight proportionally
    total_available_weight = sum(w for _, w in available.values())
    scale_factor = 1.0 / total_available_weight if total_available_weight > 0 else 1.0

    dimension_details: dict[str, dict] = {}
    overall_score = 0.0

    for dim_name, (score, original_weight) in available.items():
        adjusted_weight = round(original_weight * scale_factor, 4)
        weighted = round(score * adjusted_weight, 1)
        overall_score += weighted
        detail: dict = {
            "score": score,
            "weight": round(adjusted_weight, 2),
            "weighted": weighted,
        }
        if fallbacks.get(dim_name):
            detail["fallback"] = True
        dimension_details[dim_name] = detail

    overall_score = round(overall_score)
    grade = score_to_grade(overall_score, grade_boundaries)

    return {
        "overall_score": overall_score,
        "grade": grade,
        "weights_used": weights_used,
        "dimension_scores": dimension_details,
    }


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: uv run scripts/compute-scores.py <session-directory>",
            file=sys.stderr,
        )
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    result = compute_scores(session_dir)

    validate_result(result)

    output_path = session_dir / "scores-summary.json"
    output_path.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
