# Pratik VLM Data Quality Copilot

**Built by Pratik Sagale** · Python · Pandas · Streamlit · Data Quality · VLM Annotation QA

A lightweight dashboard for checking structured vision-language model (VLM) annotation datasets. Upload a CSV, review quality findings, filter issues, and export reports.

## Why this project?

VLM datasets can contain duplicate IDs, missing fields, inconsistent labels, invalid confidence values, or generic captions. These problems are repetitive to find manually. This tool applies transparent, repeatable checks so reviewers can focus on records that need attention.

## Features

- CSV upload and synthetic demo dataset.
- Overview metrics: records scanned, flagged records, findings, errors, and clean-record share.
- Checks for missing required values, duplicate IDs, labels outside a configurable allow-list, confidence values outside 0–1, short captions, and generic placeholder captions.
- Filter findings by severity and rule.
- Download row-level findings and a dataset with quality status.
- Automated unit tests for the core validation rules.

## Quick start

Requires Python 3.10+.

```powershell
git clone https://github.com/Pratik0058/pratik-vlm-data-quality-copilot.git
cd pratik-vlm-data-quality-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

## Expected columns

| Column | Meaning |
|---|---|
| `record_id` | Unique identifier for the annotation |
| `image_path` | Asset name/path or reference |
| `caption` | Text description |
| `label` | Annotation category |
| `confidence` | Optional numeric score from 0 to 1 |

Extra columns are permitted. Missing required columns are reported.

## How it works

```text
CSV upload → validate available fields → apply independent quality rules
          → produce explained row-level findings → filter and export reports
```

The rule logic is in `quality_checks.py`, separate from the Streamlit UI. Run tests with:

```bash
python -m unittest discover -s tests -v
```

## Important limitation

This version is a **rule-based QA tool**, not a vision-language model. It does not open images or prove whether a caption semantically matches an image. Findings are review prompts, and all decisions should be checked against the project's annotation guidelines. The demo records are synthetic; no business impact or accuracy gain is claimed.

## Repository files

- `app.py` — dashboard UI
- `quality_checks.py` — reusable validation logic
- `data/sample_vlm_annotations.csv` — sample records, including intentional issues
- `tests/test_quality_checks.py` — unit tests
- `INTERVIEW_GUIDE.md` — walkthrough and interview practice
- `requirements.txt` — Python dependencies

## Author

**Pratik Sagale** · [GitHub @Pratik0058](https://github.com/Pratik0058)
