"""Unit tests for annotation dataset validation."""
import unittest
import pandas as pd
from quality_checks import add_quality_status, validate_dataset


class ValidateDatasetTests(unittest.TestCase):
    def base_frame(self):
        return pd.DataFrame([
            {"record_id": "A1", "image_path": "a.jpg", "caption": "A person stands beside a car.", "label": "person", "confidence": 0.9},
            {"record_id": "A2", "image_path": "b.jpg", "caption": "A dog runs through grass.", "label": "animal", "confidence": 0.7},
        ])

    def test_clean_dataset_has_no_findings(self):
        self.assertTrue(validate_dataset(self.base_frame(), min_caption_chars=8).empty)

    def test_duplicate_ids_flag_each_duplicate(self):
        frame = self.base_frame()
        frame.loc[1, "record_id"] = "A1"
        found = validate_dataset(frame)
        self.assertEqual(len(found[found["rule"] == "duplicate_record_id"]), 2)

    def test_missing_required_value_is_flagged(self):
        frame = self.base_frame()
        frame.loc[0, "caption"] = " "
        self.assertIn("missing_value", validate_dataset(frame)["rule"].tolist())

    def test_unknown_label_is_flagged(self):
        frame = self.base_frame()
        frame.loc[0, "label"] = "spaceship"
        self.assertIn("unknown_label", validate_dataset(frame)["rule"].tolist())

    def test_confidence_values_are_validated(self):
        frame = self.base_frame()
        frame.loc[0, "confidence"] = 1.2
        frame.loc[1, "confidence"] = "high"
        found = validate_dataset(frame)
        self.assertEqual(len(found[found["rule"] == "invalid_confidence"]), 2)

    def test_generic_and_short_caption_checks(self):
        frame = self.base_frame()
        frame.loc[0, "caption"] = "image"
        rules = set(validate_dataset(frame, min_caption_chars=12)["rule"].tolist())
        self.assertIn("generic_caption", rules)
        self.assertIn("short_caption", rules)

    def test_missing_column_is_dataset_level_finding(self):
        frame = self.base_frame().drop(columns=["image_path"])
        found = validate_dataset(frame)
        missing = found[found["rule"] == "missing_column"]
        self.assertEqual(len(missing), 1)
        self.assertEqual(int(missing.iloc[0]["row_number"]), 0)

    def test_quality_status_marks_flagged_records(self):
        frame = self.base_frame()
        frame.loc[0, "caption"] = "image"
        found = validate_dataset(frame)
        result = add_quality_status(frame, found)
        self.assertEqual(result.loc[0, "quality_status"], "Needs review")
        self.assertGreater(result.loc[0, "findings_count"], 0)
        self.assertEqual(result.loc[1, "quality_status"], "Pass")


if __name__ == "__main__":
    unittest.main()
