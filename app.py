import streamlit as st
from io import BytesIO

from excel_handler import SourceMetadataReader
from workbook_handler import WorkbookHandler
from matcher import Matcher
from audit_logger import AuditLogger

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="D365 Finance & Operations Metadata Mapper",
    layout="wide"
)

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

    source_file = st.file_uploader(
        "📂 Source Metadata",
        type=["xlsx", "csv", "txt"]
    )

with col2:

    target_file = st.file_uploader(
        "📂 Target Metadata",
        type=["xlsx"]
    )

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if source_file and target_file:

    try:

        reader = SourceMetadataReader(source_file)
        reader.load()

        source_metadata = reader.get_metadata()

        st.success(
            f"Loaded {len(source_metadata)} source fields."
        )

        st.subheader("Source Preview")

        st.dataframe(
            reader.preview(),
            use_container_width=True
        )

        if st.button("🚀 Generate Mapping"):

            with st.spinner("Matching metadata..."):

                workbook = WorkbookHandler(target_file)

                target_metadata = workbook.get_target_fields()

                matcher = Matcher()

                logger = AuditLogger()

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
                            "NoMap"
                        )

                        logger.add({
                            "source_field": "NoMap",
                            "source_description": "",
                            "target_field": target["field"],
                            "target_description": target.get(
                                "description", ""
                            ),
                            "confidence": 0,
                            "method": "No Match",
                            "status": "NoMap",
                            "reason": "No candidate above threshold"
                        })

                        nomap += 1
                        continue

                    workbook.update_source_field(
                        target["row"],
                        result["source_field"]
                    )

                    logger.add(result)

                    if result["status"] == "Auto Accept":

                        mapped += 1

                    elif result["status"] == "Review":

                        review += 1

                    else:

                        nomap += 1

                # Save mapped workbook
                output = BytesIO()
                workbook.save(output)

                # Save audit report
                audit_output = BytesIO()

                logger.dataframe().to_excel(
                    audit_output,
                    index=False,
                    engine="openpyxl"
                )

            st.success("✅ Mapping Completed")

            # -------------------------------------------------
            # Statistics
            # -------------------------------------------------

            summary = logger.summary()

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
                logger.dataframe(),
                use_container_width=True
            )

            # -------------------------------------------------
            # Download Buttons
            # -------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.download_button(

                    label="📥 Download Mapped Workbook",

                    data=output.getvalue(),

                    file_name="Mapped_Target_Metadata.xlsx",

                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                )

            with col2:

                st.download_button(

                    label="📊 Download Audit Report",

                    data=audit_output.getvalue(),

                    file_name="Mapping_Audit_Report.xlsx",

                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                )

    except Exception as ex:

        st.error(str(ex))
        st.exception(ex)

else:

    st.info("Please upload both files.")