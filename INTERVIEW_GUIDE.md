# Pratik VLM Data Quality Copilot — Interview Guide

**Author:** Pratik Sagale  
**Project type:** Independent portfolio project  
**Stack:** Python, Pandas, Streamlit, unittest

## 1. The problem I chose

Vision-language models (VLMs) learn from combinations of visual inputs and language. Annotation data used to build or evaluate those systems needs consistent identifiers, complete fields, controlled labels, and useful captions. A dataset can contain issues that are easy to miss in a manual spreadsheet review: duplicate record IDs, blank captions, labels outside the project's taxonomy, invalid confidence scores, and placeholder captions such as “image”.

I built the **Pratik VLM Data Quality Copilot** to make basic first-pass QA checks repeatable. It surfaces suspicious records so that a reviewer can spend more time deciding whether annotations satisfy project guidelines.

## 2. What the application does

The user starts the Streamlit app, loads the included sample CSV or uploads a dataset, and adjusts screening rules in the sidebar. The dashboard displays records scanned, records with findings, total findings, error and warning counts, and the share of records that passed the enabled checks. The user can filter findings and download a detailed findings CSV or a copy of the dataset with a quality status for each record.

Each finding includes the CSV row number, record ID, severity, rule name, field, observed value, and a plain-language explanation. A record can have multiple findings—for example, a duplicate ID and an invalid confidence value.

## 3. Technical design

### A. Streamlit presentation layer — app.py

I used Streamlit to build a dashboard without a separate front-end framework. It handles CSV upload, sidebar controls, summary metrics, tables, a chart, filters, and download buttons. The workflow stays focused: load data, review metrics, investigate findings, export a report.

### B. Validation layer — quality_checks.py

I separated validation logic from the UI so the checks can be tested independently and reused. The validate_dataset function accepts a pandas DataFrame and configurable options, then returns a normalized findings table. The checks include:

- **Required values and columns:** identifies empty record IDs, image paths, captions, and labels, plus missing schema columns.
- **Duplicate record IDs:** marks every row in a group with a repeated nonblank ID.
- **Allowed labels:** flags labels outside a configurable case-insensitive list.
- **Confidence values:** flags non-numeric values or values outside the inclusive 0–1 range when that column exists.
- **Caption length:** flags captions below the configurable character threshold.
- **Generic captions:** flags exact matches to common placeholders such as “image” or “no description”.

The add_quality_status function adds a findings count and “Pass” or “Needs review” status to each row. It also records whether any finding is an error.

### C. Test layer — tests/test_quality_checks.py

I used Python's built-in unittest framework to test a clean dataset, duplicate IDs, missing required values, unknown labels, invalid confidence, generic and short captions, missing columns, and row-level quality status. Since the core rules are deterministic, the tests are quick to reproduce.

### D. Demo dataset

The sample CSV is synthetic. It intentionally contains a mix of valid rows and examples of common data issues, so someone can test the workflow without real customer, employer, or private data.

## 4. The most important design decision

This first version is a **rule-based QA tool**, not a vision-language model that understands images. It does not load image files, infer visual content, or decide whether a caption accurately describes an image. It checks data structure and obvious text/value patterns.

That distinction matters. A short caption can be correct for some tasks, and a label missing from the default allow-list might be valid for a project with a different taxonomy. Therefore, some findings are warnings and the app explains why the record was flagged. A human reviewer must make the final decision using the annotation guidelines.

## 5. Suggested interview explanation (60–90 seconds)

“I built a Python and Streamlit tool called Pratik VLM Data Quality Copilot to improve first-pass QA for vision-language annotation datasets. The motivation was that duplicate IDs, missing captions, inconsistent labels, and invalid confidence values are repetitive to check manually, but can create downstream data-quality problems.

I used Pandas to process the CSV and created a separate validation module with independent, configurable rules. Each rule generates a structured finding with severity, row number, field, observed value, and explanation. Streamlit displays dataset-level metrics, lets reviewers filter findings, and exports both a findings report and a dataset with record-level status. I also added synthetic sample data and unit tests for key validation cases.

One deliberate limitation is that this version does not inspect image pixels or claim to verify semantic caption accuracy. It is a transparent QA-screening layer that helps a human reviewer prioritize records. My next step would be to add project-specific schemas and optionally a model-assisted image-caption grounding check, evaluated against human-reviewed examples and with human confirmation.”

## 6. Questions an interviewer may ask

**Why Streamlit?**  
It helped me prototype the end-to-end workflow quickly in Python, keeping the focus on validation logic instead of UI boilerplate.

**Why separate the validation module from the app?**  
The rules can be tested independently and reused from another interface or batch pipeline. Separating them also makes debugging and maintenance easier.

**How do you control false positives?**  
I made thresholds and allowed labels configurable, explain each finding, and treat subjective checks as warnings rather than ground truth. A production version should use a schema and thresholds agreed with the data owner.

**Does it use an LLM or VLM?**  
Not in this first version. It is a data-quality tool for VLM annotation workflows using deterministic checks. Semantic image-caption verification would be a separate feature requiring a model, an evaluation set, and human review.

**How would you scale it?**  
I would add project-specific schema/config files, batch processing for large datasets, logging and versioned reports, stronger taxonomy management, and an optional CI pipeline step. I would profile against realistic dataset sizes before optimizing.

**How would you measure whether it helps?**  
I would build a representative, human-reviewed test set and measure each rule's precision and recall, issues found before delivery, review time, and the proportion of flagged records that reviewers confirm. I would not claim gains without running that evaluation.

**What was the main trade-off?**  
The first version favors interpretability, ease of setup, and testability over semantic understanding. Its rules are straightforward to explain, but they cannot detect every annotation error.

## 7. How to demonstrate it

1. Install dependencies with pip install -r requirements.txt.
2. Start it with streamlit run app.py.
3. Click “Load sample dataset” to show intentionally flawed records.
4. Point out a duplicate ID, generic caption, unknown label, and invalid confidence.
5. Change the caption threshold or allowed labels and show how findings update.
6. Download the findings CSV and record-status CSV.
7. Run python -m unittest discover -s tests -v.

## 8. How to describe ownership and impact accurately

Present this as an independent portfolio project built to demonstrate Python-based data validation and annotation QA. The dataset is synthetic. No business impact, accuracy improvement, or time savings have been claimed because those outcomes have not been measured. Run the project yourself, inspect the code, and be ready to explain the rules before discussing it in an interview.
