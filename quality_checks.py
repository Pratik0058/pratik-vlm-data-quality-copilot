"""Rule-based checks for structured VLM annotation CSV datasets."""
from __future__ import annotations
from typing import Iterable, Optional
import pandas as pd

DEFAULT_REQUIRED_COLUMNS = ("record_id", "image_path", "caption", "label")
DEFAULT_ALLOWED_LABELS = ("person", "vehicle", "animal", "object", "scene", "text")
DEFAULT_GENERIC_CAPTIONS = ("image", "an image", "picture", "a picture", "no description", "unknown", "n/a", "na", "none")


def _is_blank(value: object) -> bool:
    if pd.isna(value):
        return True
    return isinstance(value, str) and not value.strip()


def validate_dataset(frame: pd.DataFrame, *, required_columns: Iterable[str] = DEFAULT_REQUIRED_COLUMNS,
                     allowed_labels: Optional[Iterable[str]] = DEFAULT_ALLOWED_LABELS,
                     min_caption_chars: int = 12,
                     generic_captions: Iterable[str] = DEFAULT_GENERIC_CAPTIONS,
                     confidence_column: str = "confidence") -> pd.DataFrame:
    """Return normalized findings, one row per issue. Row 0 means dataset-level."""
    if min_caption_chars < 0:
        raise ValueError("min_caption_chars must be zero or greater")
    result_columns = ["row_number", "record_id", "severity", "rule", "field", "value", "message"]
    findings: list[dict[str, object]] = []

    def add(row_number: int, record_id: object, severity: str, rule: str,
            field: str, value: object, message: str) -> None:
        findings.append({"row_number": row_number, "record_id": record_id, "severity": severity,
                         "rule": rule, "field": field,
                         "value": "" if pd.isna(value) else str(value), "message": message})

    df = frame.copy()
    required = tuple(required_columns)
    available = set(df.columns)
    for column in required:
        if column not in available:
            add(0, "", "error", "missing_column", column, "",
                f"Required column '{column}' is missing. Checks for this field cannot run.")
    ids = df["record_id"] if "record_id" in available else pd.Series("", index=df.index)

    for column in required:
        if column not in available:
            continue
        for pos, value in enumerate(df[column].tolist(), start=1):
            if _is_blank(value):
                rid = ids.iloc[pos - 1] if "record_id" in available else ""
                add(pos, rid, "error", "missing_value", column, value, f"'{column}' is empty.")

    if "record_id" in available:
        normalized = df["record_id"].astype("string").str.strip()
        valid = normalized.notna() & normalized.ne("")
        duplicate_mask = valid & normalized.duplicated(keep=False)
        for pos, duplicate in enumerate(duplicate_mask.tolist(), start=1):
            if duplicate:
                rid = df.iloc[pos - 1]["record_id"]
                add(pos, rid, "error", "duplicate_record_id", "record_id", rid,
                    "Record ID appears more than once in the dataset.")

    if allowed_labels is not None and "label" in available:
        allowed = {str(label).strip().casefold() for label in allowed_labels}
        for pos, label in enumerate(df["label"].tolist(), start=1):
            if _is_blank(label):
                continue
            if str(label).strip().casefold() not in allowed:
                rid = ids.iloc[pos - 1] if "record_id" in available else ""
                add(pos, rid, "warning", "unknown_label", "label", label,
                    "Label is not in the configured allow-list; confirm the project taxonomy.")

    generic = {str(item).strip().casefold() for item in generic_captions}
    if "caption" in available:
        for pos, caption in enumerate(df["caption"].tolist(), start=1):
            if _is_blank(caption):
                continue
            rid = ids.iloc[pos - 1] if "record_id" in available else ""
            normalized_caption = str(caption).strip().casefold()
            if len(str(caption).strip()) < min_caption_chars:
                add(pos, rid, "warning", "short_caption", "caption", caption,
                    f"Caption has fewer than {min_caption_chars} characters; review whether it is informative enough.")
            if normalized_caption in generic:
                add(pos, rid, "warning", "generic_caption", "caption", caption,
                    "Caption matches a generic placeholder phrase.")

    if confidence_column in available:
        for pos, value in enumerate(df[confidence_column].tolist(), start=1):
            if _is_blank(value):
                continue
            rid = ids.iloc[pos - 1] if "record_id" in available else ""
            try:
                number = float(value)
            except (TypeError, ValueError):
                add(pos, rid, "warning", "invalid_confidence", confidence_column, value,
                    "Confidence is not numeric.")
                continue
            if not 0.0 <= number <= 1.0:
                add(pos, rid, "warning", "invalid_confidence", confidence_column, value,
                    "Confidence must be between 0 and 1 inclusive.")

    return pd.DataFrame(findings, columns=result_columns)


def add_quality_status(frame: pd.DataFrame, findings: pd.DataFrame) -> pd.DataFrame:
    """Return records with findings_count and quality_status columns."""
    result = frame.copy().reset_index(drop=True)
    counts = [0] * len(result)
    errors = [False] * len(result)
    if not findings.empty:
        relevant = findings[findings["row_number"].between(1, len(result))]
        for _, item in relevant.iterrows():
            index = int(item["row_number"]) - 1
            counts[index] += 1
            if item["severity"] == "error":
                errors[index] = True
    result["findings_count"] = counts
    result["quality_status"] = ["Needs review" if count else "Pass" for count in counts]
    result["has_error"] = errors
    return result
