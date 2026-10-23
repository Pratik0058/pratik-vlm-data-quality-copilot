# Pratik VLM Data Quality Copilot — Interview Guide

**Author:** Pratik Sagale  
**Project:** Independent portfolio project  
**Tech stack:** Python, Pandas, Streamlit, unittest

## 1. Problem and goal

Vision-language model (VLM) workflows depend on well-structured image-and-text annotations. Before a dataset is used, it can contain avoidable issues such as duplicate IDs, blank captions, labels outside the project taxonomy, invalid confidence values, or placeholder text like “image”. Finding these problems manually in spreadsheets can be repetitive.

I built the **Pratik VLM Data Quality Copilot** to make these first-pass checks repeatable. It scans a CSV, generates explained findings, summarizes dataset quality, and exports results so an annotator or QA reviewer can focus on records that need attention.

## 2. What the tool does

The user opens the Streamlit dashboard and either uploads a CSV or loads the included synthetic sample. The sidebar lets the user choose a minimum caption length and an allowed-label list. The dashboard shows records scanned, records flagged, total findings, error/warning counts, and the share of records with no findings.

Reviewers can filter findings by severity or rule. Each finding includes the source row number, record ID, rule, field, observed value, severity, and a plain-language explanation. The app also exports two reports: a findings CSV and a copy of the original dataset with a finding count and “Pass” or “Needs review” status for each row.

The current checks are:
- Required values and required columns.
- Duplicate nonblank record IDs, marking every row in a duplicate group.
- Labels outside a configurable case-insensitive allow-list.
- Confidence values that are not numeric or lie outside the inclusive 0–1 range.
- Captions shorter than the configured threshold.
- Exact matches to common generic captions such as “image” or “no description”.

## 3. How I designed it

**Streamlit UI (app.py):** Handles data upload, configurable controls, summary metrics, tables, filtering, a finding summary chart, and report downloads.

**Validation module (quality_checks.py):** Contains the reusable validation rules. The validate_dataset function takes a Pandas DataFrame and the selected rule settings, and returns a normalized findings table. I kept this logic separate from the interface so it can be tested and reused in a batch workflow later.

**Status and reporting:** The add_quality_status function associates row-level findings with the input dataset and adds a finding count and status, which makes the output easier to hand to a reviewer.

**Tests (tests/test_quality_checks.py):** Uses Python’s built-in unittest framework to test clean data, duplicate IDs, missing fields, unknown labels, invalid confidence values, generic/short captions, missing columns, and row-level status.

**Sample data:** The CSV contains synthetic records with both valid examples and intentional quality issues. It lets someone demonstrate the dashboard without real employer, customer, or private data.

## 4. Important limitation

This version is a **rule-based QA screening tool**, not a VLM or LLM. It does not open image files, inspect pixels, or prove that a caption semantically matches an image. It checks the CSV’s structure and a handful of obvious text/value patterns.

A short caption may be valid for a particular task, and a label outside the default list may be valid under another project’s taxonomy. Findings therefore need human review against the project’s annotation guidelines. I do not claim measured improvements in model accuracy, review time, or business outcomes because I have not run a controlled evaluation.

## 5. Interview answer you can practice (about 60 seconds)

“I built a Python and Streamlit project called Pratik VLM Data Quality Copilot to support first-pass QA for VLM annotation datasets. I wanted to make common checks—like duplicate record IDs, missing captions, labels outside the taxonomy, and invalid confidence values—repeatable instead of relying entirely on manual spreadsheet review.

I used Pandas for the CSV processing and built a separate validation module with configurable, deterministic rules. Each rule generates a finding with severity, row number, field, value, and an explanation. The Streamlit dashboard summarizes the issues, lets a reviewer filter findings, and exports a detailed report and a row-level dataset status. I also included synthetic data and unit tests.

This first version does not inspect images or verify semantic caption accuracy; it is a transparent screening layer for human reviewers. As a next step, I would add project-specific schemas and evaluate an optional model-assisted caption-grounding check against human-reviewed examples.”

## 6. Common follow-up questions

**Why Streamlit?** It let me build and demonstrate the workflow quickly in Python without needing a separate front-end stack.

**Why separate the rules from the UI?** It makes the checks easier to test, debug, reuse, and eventually call from a batch process.

**How would you reduce false positives?** Use project-owned schemas and taxonomies, tune thresholds, explain each flag, and keep subjective issues as review warnings. Evaluate rules against a human-reviewed dataset.

**How could you scale it?** Add per-project config files, process larger CSVs in batches, save versioned QA reports, integrate the checks into a data pipeline, and profile performance on realistic datasets. A future semantic check would need a defined model, evaluation criteria, and human confirmation.

**How would you measure value?** Measure each rule’s precision and recall against expert-reviewed records, the share of flagged records confirmed by reviewers, issues found before delivery, and review time. Do not quote impact until it has been measured.

## 7. Run and demo it

1. Install: python -m pip install -r requirements.txt
2. Start: streamlit run app.py
3. Click **Load sample dataset** and point out the duplicate ID, generic caption, unknown label, and invalid confidence.
4. Change the threshold or allowed-label list and show how the findings change.
5. Download the reports.
6. Run tests: python -m unittest discover -s tests -v

Describe this honestly as an independent portfolio project built by you to demonstrate Python-based annotation QA. Understand the logic before interviews and be clear about what the tool currently does—and does not—do.
