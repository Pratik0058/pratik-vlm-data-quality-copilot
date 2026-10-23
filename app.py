"""Streamlit dashboard for Pratik VLM Data Quality Copilot."""
import pandas as pd
import streamlit as st

from quality_checks import (
    DEFAULT_ALLOWED_LABELS,
    DEFAULT_GENERIC_CAPTIONS,
    add_quality_status,
    validate_dataset,
)

st.set_page_config(page_title="Pratik VLM Data Quality Copilot", page_icon="🔎", layout="wide")
st.title("🔎 Pratik VLM Data Quality Copilot")
st.caption("VLM annotation dataset QA screening · Built by Pratik Sagale")

with st.sidebar:
    st.header("Quality rules")
    st.write("Adjust checks for your annotation project. Findings are prompts for human review, not automatic judgments of correctness.")
    min_caption_chars = st.slider("Minimum caption characters", 0, 100, 12)
    label_text = st.text_area("Allowed labels (one per line)", value="\n".join(DEFAULT_ALLOWED_LABELS), height=150)
    allowed_labels = [item.strip() for item in label_text.splitlines() if item.strip()]
    check_allowed_labels = st.checkbox("Check labels against this list", value=True)
    st.divider()
    st.caption("The app reads CSV values only. It does not upload or inspect image files.")

def load_sample() -> pd.DataFrame:
    return pd.read_csv("data/sample_vlm_annotations.csv")

uploaded = st.file_uploader("Upload an annotation CSV", type=["csv"])
left_button, hint = st.columns([1, 3])
with left_button:
    use_sample = st.button("Load sample dataset", use_container_width=True)
with hint:
    st.caption("Try synthetic sample records or upload your own CSV. Required columns are described in the README.")

if uploaded is not None:
    try:
        data = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
        st.stop()
elif use_sample or st.session_state.get("use_sample", False):
    st.session_state["use_sample"] = True
    try:
        data = load_sample()
    except Exception as exc:
        st.error(f"Could not load sample data: {exc}")
        st.stop()
else:
    st.info("Upload a CSV or click **Load sample dataset** to get started.")
    st.markdown(
        """
        **What this tool checks**
        - Missing required values and duplicate record IDs
        - Labels outside a configurable allow-list
        - Confidence values outside the 0–1 range or non-numeric values
        - Short captions and generic placeholder captions
        """
    )
    st.stop()

findings = validate_dataset(
    data,
    allowed_labels=allowed_labels if check_allowed_labels else None,
    min_caption_chars=min_caption_chars,
    generic_captions=DEFAULT_GENERIC_CAPTIONS,
)
status_data = add_quality_status(data, findings)
total_rows = len(data)
flagged_rows = int((status_data["findings_count"] > 0).sum())
total_findings = len(findings)
error_count = int((findings["severity"] == "error").sum()) if not findings.empty else 0
warning_count = int((findings["severity"] == "warning").sum()) if not findings.empty else 0
clean_share = ((total_rows - flagged_rows) / total_rows * 100) if total_rows else 0.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Records scanned", f"{total_rows:,}")
k2.metric("Records flagged", f"{flagged_rows:,}")
k3.metric("Total findings", f"{total_findings:,}")
k4.metric("Errors / warnings", f"{error_count:,} / {warning_count:,}")
k5.metric("Clean records", f"{clean_share:.1f}%")

st.divider()
preview, summary_col = st.columns([1, 1])
with preview:
    st.subheader("Dataset preview")
    st.dataframe(status_data.head(20), use_container_width=True, hide_index=True)
with summary_col:
    st.subheader("Finding summary")
    if findings.empty:
        st.success("No issues were found by the enabled rules.")
    else:
        summary = (
            findings.groupby(["severity", "rule"], dropna=False)
            .size().reset_index(name="count")
            .sort_values(["severity", "count"], ascending=[True, False])
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.bar_chart(summary.groupby("rule")["count"].sum().sort_values(ascending=False))

st.subheader("Review findings")
if findings.empty:
    st.write("No findings for the current rule settings.")
else:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        severity_options = ["All"] + sorted(findings["severity"].dropna().unique().tolist())
        selected_severity = st.selectbox("Severity", severity_options)
    with filter_col2:
        rule_options = ["All"] + sorted(findings["rule"].dropna().unique().tolist())
        selected_rule = st.selectbox("Rule", rule_options)
    view = findings.copy()
    if selected_severity != "All":
        view = view[view["severity"] == selected_severity]
    if selected_rule != "All":
        view = view[view["rule"] == selected_rule]
    st.dataframe(view, use_container_width=True, hide_index=True)

st.subheader("Export reports")
download1, download2 = st.columns(2)
with download1:
    st.download_button(
        "Download findings CSV",
        data=findings.to_csv(index=False).encode("utf-8"),
        file_name="pratik_vlm_quality_findings.csv",
        mime="text/csv",
        use_container_width=True,
    )
with download2:
    st.download_button(
        "Download dataset with quality status",
        data=status_data.to_csv(index=False).encode("utf-8"),
        file_name="pratik_vlm_dataset_quality_status.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption("Built by Pratik Sagale · Rule-based screening only · Validate flagged records against project guidelines.")
