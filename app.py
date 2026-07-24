import streamlit as st
from io import BytesIO
import pandas as pd

from excel_handler import SourceMetadataReader
from workbook_handler import WorkbookHandler
from matcher import Matcher
from audit_logger import AuditLogger
from ai_assistant import NoMapAIAssistant

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="D365 Finance & Operations Metadata Mapper",
    layout="wide"
)

if "mapping_result" not in st.session_state:
    st.session_state.mapping_result = None

st.title("🚀 D365 Finance & Operations Metadata Mapper V3")

st.write(
    "Upload Source Metadata and Target Metadata to generate mapping."
)

st.divider()

# ---------------------------------------------------------
# Upload Files
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    source_files = st.file_uploader(
        "📂 Source Metadata (Single or Multiple)",
        type=["xlsx", "csv", "txt"],
        accept_multiple_files=True
    )

with col2:

    target_file = st.file_uploader(
        "📂 Target Metadata",
        type=["xlsx"]
    )

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if source_files and target_file:

    try:

        source_metadata = []
        preview_frames = []

        for source_file in source_files:

            reader = SourceMetadataReader(source_file)
            reader.load()

            source_metadata.extend(reader.get_metadata())

            preview = reader.preview()

            if preview is not None and not preview.empty:
                preview_frames.append(preview)

        st.success(
            f"Loaded {len(source_metadata)} source fields from {len(source_files)} source file(s)."
        )

        st.subheader("Source Preview")

        st.dataframe(
            pd.concat(preview_frames, ignore_index=True) if preview_frames else pd.DataFrame(),
            use_container_width=True
        )

        generate_ai_assistance = st.checkbox(
            "Generate AI Assistance For NoMap (slower)",
            value=False,
            help="Enable this only when you need suggestion analysis for unmapped/review rows."
        )

        if st.button("🚀 Generate Mapping"):

            with st.spinner("Matching metadata..."):

                workbook = WorkbookHandler(target_file)

                target_metadata = workbook.get_target_fields()

                matcher = Matcher()
                nomap_ai = NoMapAIAssistant(top_n=3) if generate_ai_assistance else None

                logger = AuditLogger()
                nomap_assistance = []
                source_status_map = {}

                mapped = 0
                review = 0
                nomap = 0

                # -------------------------------------------------
                # Match Target Fields
                # -------------------------------------------------

                for target in target_metadata:

                    result = matcher.match_target(
                        target,
                        source_metadata
                    )

                    if result is None:

                        workbook.update_source_field(
                            target["row"],
                            "NoMap",
                            target.get("sheet_name")
                        )

                        workbook.update_mapping_origin(
                            target["row"],
                            "NoMap",
                            target.get("sheet_name")
                        )

                        logger.add({
                            "source_field": "NoMap",
                            "source_description": "",
                            "source_entity": "",
                            "source_sheet": "",
                            "source_file": "",
                            "target_field": target["field"],
                            "target_sheet": target.get("sheet_name", ""),
                            "target_description": target.get(
                                "description", ""
                            ),
                            "confidence": 0,
                            "method": "No Match",
                            "status": "NoMap",
                            "reason": "No candidate above threshold",
                            "mapping_source": "NoMap",
                            "ai_suggested_source": "",
                            "ai_confidence": "",
                            "ai_method": "",
                            "ai_reason": "",
                            "ai_alternatives": ""
                        })

                        nomap += 1
                        continue

                    workbook.update_source_field(
                        target["row"],
                        result["source_field"],
                        target.get("sheet_name")
                    )

                    mapped_from = (
                        result.get("source_entity", "")
                        or result.get("source_sheet", "")
                        or result.get("source_file", "")
                    )

                    workbook.update_mapping_origin(
                        target["row"],
                        mapped_from,
                        target.get("sheet_name")
                    )

                    source_status_map[
                        result.get("source_id", result["source_field"])
                    ] = result["status"]

                    logger.add({
                        **result,
                        "target_sheet": target.get("sheet_name", ""),
                        "mapping_source": mapped_from,
                        "ai_suggested_source": "",
                        "ai_confidence": "",
                        "ai_method": "",
                        "ai_reason": "",
                        "ai_alternatives": ""
                    })

                    if result["status"] == "Auto Accept":

                        mapped += 1

                    elif result["status"] == "Review":

                        review += 1

                    else:

                        nomap += 1

                # Save mapped workbook
                output = BytesIO()
                workbook.save(output)

                # -------------------------------------------------
                # AI Assistance For NoMap
                # -------------------------------------------------

                if generate_ai_assistance:

                    remaining_sources = [
                        x for x in source_metadata
                        if source_status_map.get(
                            x.get("source_id", x.get("field", "")),
                            "NoMap"
                        )
                        != "Auto Accept"
                    ]

                    for source in remaining_sources:

                        suggestions = nomap_ai.suggest_targets_for_unmapped_source(
                            source,
                            target_metadata
                        )

                        top = suggestions[0] if suggestions else None

                        alternatives = ""
                        possible_targets = []

                        if suggestions:
                            possible_targets = [
                                f"{x['target_field']} ({x['confidence']})"
                                for x in suggestions
                            ]

                            alternatives = " | ".join([
                                f"{x['target_field']} ({x['confidence']})"
                                for x in suggestions
                            ])

                        nomap_assistance.append({
                            "Suggested Source": source.get("field", ""),
                            "Source Description": source.get("description", ""),
                            "Source Status": source_status_map.get(
                                source.get("source_id", source.get("field", "")),
                                "NoMap"
                            ),
                            "Mapped From": (
                                source.get("source_entity", "")
                                or source.get("source_sheet", "")
                                or source.get("source_file", "")
                            ),
                            "Target Suggestion": top["target_field"] if top else "",
                            "Confidence": top["confidence"] if top else 0,
                            "Method": top["method"] if top else "",
                            "Reason": top["reason"] if top else "No suggestion from AI",
                            "Possible Targets": " | ".join(possible_targets),
                            "Alternatives": alternatives
                        })
                else:
                    nomap_assistance.append({
                        "Suggested Source": "",
                        "Source Description": "",
                        "Source Status": "",
                        "Mapped From": "",
                        "Target Suggestion": "",
                        "Confidence": "",
                        "Method": "",
                        "Reason": "AI Assistance skipped to improve runtime. Enable the checkbox before mapping to include suggestions.",
                        "Possible Targets": "",
                        "Alternatives": ""
                    })

                # Save audit report
                audit_output = BytesIO()

                with pd.ExcelWriter(
                    audit_output,
                    engine="openpyxl"
                ) as writer:

                    logger.dataframe().to_excel(
                        writer,
                        sheet_name="Target Mapping Audit",
                        index=False
                    )

                    pd.DataFrame(nomap_assistance).to_excel(
                        writer,
                        sheet_name="AI Assistance For NoMap",
                        index=False
                    )

                st.session_state.mapping_result = {
                    "summary": logger.summary(),
                    "audit_df": logger.dataframe(),
                    "nomap_df": pd.DataFrame(nomap_assistance),
                    "ai_assistance_enabled": generate_ai_assistance,
                    "mapped_workbook": output.getvalue(),
                    "audit_workbook": audit_output.getvalue(),
                }

        if st.session_state.mapping_result is not None:

            result = st.session_state.mapping_result

            st.success("✅ Mapping Completed")

            # -------------------------------------------------
            # Statistics
            # -------------------------------------------------

            summary = result["summary"]

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total", summary["Total"])
            c2.metric("Mapped", summary["Auto Accept"])
            c3.metric("Review", summary["Review"])
            c4.metric("NoMap", summary["NoMap"])

            # -------------------------------------------------
            # Audit Report Preview
            # -------------------------------------------------

            st.subheader("📋 Mapping Audit Report")

            st.dataframe(
                result["audit_df"],
                use_container_width=True
            )

            st.subheader("🤖 AI Assistance For NoMap")

            if not result.get("ai_assistance_enabled", True):
                st.info(
                    "AI Assistance was skipped for faster mapping. Re-run with checkbox enabled if you need suggestions."
                )

            st.dataframe(
                result["nomap_df"],
                use_container_width=True
            )

            # -------------------------------------------------
            # Download Buttons
            # -------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.download_button(

                    label="📥 Download Mapped Workbook",

                    data=result["mapped_workbook"],

                    file_name="Mapped_Target_Metadata.xlsx",

                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                )

            with col2:

                st.download_button(

                    label="📊 Download Audit Report",

                    data=result["audit_workbook"],

                    file_name="Mapping_Audit_Report.xlsx",

                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                )

    except Exception as ex:

        st.error(str(ex))
        st.exception(ex)

else:

    st.info("Please upload at least one source file and one target file.")