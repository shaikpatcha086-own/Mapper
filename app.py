import streamlit as st
from io import BytesIO
import pandas as pd
from time import perf_counter

from excel_handler import SourceMetadataReader
from workbook_handler import WorkbookHandler
from matcher import Matcher
from audit_logger import AuditLogger
from ai_assistant import NoMapAIAssistant, LLMTargetReranker

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

        source_load_start = perf_counter()

        source_metadata = []
        preview_frames = []

        for source_file in source_files:

            reader = SourceMetadataReader(source_file)
            reader.load()

            source_metadata.extend(reader.get_metadata())

            preview = reader.preview()

            if preview is not None and not preview.empty:
                preview_frames.append(preview)

        source_load_seconds = perf_counter() - source_load_start

        st.success(
            f"Loaded {len(source_metadata)} source fields from {len(source_files)} source file(s)."
        )

        st.subheader("Source Preview")

        st.dataframe(
            pd.concat(preview_frames, ignore_index=True) if preview_frames else pd.DataFrame(),
            use_container_width=True
        )

        generate_ai_assistance = st.checkbox(
            "Generate AI Suggestions for Leftover Source Fields (slower)",
            value=False,
            help="Enable this only when you need target suggestions for leftover source fields (not final mapped targets)."
        )

        use_llm_rerank = False
        llm_configured_ui = None

        if generate_ai_assistance:
            use_llm_rerank = st.checkbox(
                "Use LLM to rerank leftover suggestions (requires API config)",
                value=False,
                help="Uses Azure OpenAI/OpenAI API when configured; falls back silently if unavailable."
            )

            if use_llm_rerank:
                llm_configured_ui = LLMTargetReranker(top_n=3).is_configured()
                if not llm_configured_ui:
                    st.warning(
                        "LLM rerank is enabled, but API configuration is missing. "
                        "Suggestions will fall back to rule-based engine only."
                    )

        if st.button("🚀 Generate Mapping"):

            with st.spinner("Matching metadata..."):

                target_scan_start = perf_counter()

                workbook = WorkbookHandler(target_file)

                target_metadata = workbook.get_target_fields()

                target_scan_seconds = perf_counter() - target_scan_start

                matcher = Matcher()
                nomap_ai = NoMapAIAssistant(top_n=3) if generate_ai_assistance else None
                llm_reranker = LLMTargetReranker(top_n=3) if (generate_ai_assistance and use_llm_rerank) else None

                logger = AuditLogger()
                nomap_assistance = []
                source_status_map = {}
                source_confidence_map = {}
                mapped_targets_high_conf = set()

                mapped = 0
                review = 0
                nomap = 0

                match_loop_start = perf_counter()

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

                    source_confidence_map[
                        result.get("source_id", result["source_field"])
                    ] = result.get("confidence", 0)

                    if result.get("confidence", 0) >= 85:
                        mapped_targets_high_conf.add(target.get("field", ""))

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

                match_loop_seconds = perf_counter() - match_loop_start

                # Save mapped workbook
                workbook_save_start = perf_counter()
                output = BytesIO()
                workbook.save(output)
                workbook_save_seconds = perf_counter() - workbook_save_start

                # -------------------------------------------------
                # AI Assistance For NoMap
                # -------------------------------------------------

                ai_assistance_seconds = 0.0
                llm_rerank_seconds = 0.0

                if generate_ai_assistance:

                    ai_assistance_start = perf_counter()

                    remaining_sources = [
                        x for x in source_metadata
                        if source_confidence_map.get(
                            x.get("source_id", x.get("field", "")),
                            0
                        )
                        < 85
                    ]

                    for source in remaining_sources:

                        llm_start = perf_counter()

                        suggestions = nomap_ai.suggest_targets_for_unmapped_source(
                            source,
                            target_metadata,
                            exclude_targets=mapped_targets_high_conf,
                            llm_reranker=llm_reranker
                        )

                        llm_rerank_seconds += (perf_counter() - llm_start)

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
                            "Suggestion Confidence": top["confidence"] if top else 0,
                            "Method": top["method"] if top else "",
                            "Reason": top["reason"] if top else "No AI suggestion for this leftover source field",
                            "Suggestion Note": (
                                "Suggestion only for leftover source. "
                                "Main mapping did not auto-map this source under strict rules."
                            ),
                            "Possible Targets": " | ".join(possible_targets),
                            "Alternatives": alternatives
                        })

                    ai_assistance_seconds = perf_counter() - ai_assistance_start
                else:
                    nomap_assistance.append({
                        "Suggested Source": "",
                        "Source Description": "",
                        "Source Status": "",
                        "Mapped From": "",
                        "Target Suggestion": "",
                        "Suggestion Confidence": "",
                        "Method": "",
                        "Reason": "AI Assistance skipped to improve runtime. Enable the checkbox before mapping to include suggestions.",
                        "Suggestion Note": "",
                        "Possible Targets": "",
                        "Alternatives": ""
                    })

                # Save audit report
                audit_save_start = perf_counter()
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
                        sheet_name="AI Suggestions - Leftover Sources",
                        index=False
                    )

                audit_save_seconds = perf_counter() - audit_save_start

                mapping_sheet_names = [
                    x.get("sheet_name", "")
                    for x in getattr(workbook, "mapping_sheets", [])
                ]

                diagnostics = {
                    "source_rows": len(source_metadata),
                    "target_rows": len(target_metadata),
                    "mapping_tabs_detected": len(mapping_sheet_names),
                    "mapping_tab_names": ", ".join(mapping_sheet_names),
                    "source_load_seconds": round(source_load_seconds, 3),
                    "target_scan_seconds": round(target_scan_seconds, 3),
                    "matching_seconds": round(match_loop_seconds, 3),
                    "workbook_save_seconds": round(workbook_save_seconds, 3),
                    "ai_assistance_seconds": round(ai_assistance_seconds, 3),
                    "llm_rerank_seconds": round(llm_rerank_seconds, 3),
                    "llm_rerank_enabled": bool(use_llm_rerank),
                    "llm_configured": bool(llm_reranker.is_configured()) if llm_reranker else False,
                    "audit_save_seconds": round(audit_save_seconds, 3),
                    "total_pairs_considered": matcher.stats["sources_considered"],
                    "pairs_scored": matcher.stats["pairs_scored"],
                    "skipped_used_source": matcher.stats["sources_skipped_used"],
                    "skipped_by_business_rule": matcher.stats["sources_skipped_rule"],
                    "skipped_by_prefilter": matcher.stats["sources_skipped_prefilter"],
                    "below_threshold": matcher.stats["candidates_below_threshold"],
                    "heuristic_rejected": matcher.stats["heuristic_rejected"],
                    "matches_returned": matcher.stats["matches_returned"],
                    "nomap_returned": matcher.stats["nomap_returned"],
                }

                st.session_state.mapping_result = {
                    "summary": logger.summary(),
                    "audit_df": logger.dataframe(),
                    "nomap_df": pd.DataFrame(nomap_assistance),
                    "ai_assistance_enabled": generate_ai_assistance,
                    "diagnostics": diagnostics,
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

            st.subheader("🤖 AI Suggestions For Leftover Source Fields")

            if not result.get("ai_assistance_enabled", True):
                st.info(
                    "AI suggestions were skipped for faster mapping. Re-run with checkbox enabled if you need leftover-source suggestions."
                )

            st.dataframe(
                result["nomap_df"],
                use_container_width=True
            )

            with st.expander("Performance Diagnostics"):
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Metric": key,
                            "Value": value,
                        }
                        for key, value in result.get("diagnostics", {}).items()
                    ]),
                    use_container_width=True,
                    hide_index=True
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