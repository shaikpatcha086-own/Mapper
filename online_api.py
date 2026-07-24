from io import BytesIO
import json
import zipfile
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from excel_handler import SourceMetadataReader
from matcher import Matcher
from workbook_handler import WorkbookHandler
from ai_assistant import NoMapAIAssistant


class MetadataItem(BaseModel):
    field: str = Field(min_length=1)
    description: str = ""


class MapFieldsRequest(BaseModel):
    source_metadata: list[MetadataItem]
    target_metadata: list[MetadataItem]


class UploadedFileAdapter:
    """Expose UploadFile as an object compatible with SourceMetadataReader."""

    def __init__(self, upload_file: UploadFile):
        self.name = upload_file.filename or "uploaded_file"
        self._file = upload_file.file

    def read(self, *args: Any, **kwargs: Any):
        return self._file.read(*args, **kwargs)

    def seek(self, *args: Any, **kwargs: Any):
        return self._file.seek(*args, **kwargs)

    def tell(self):
        return self._file.tell()


app = FastAPI(
    title="D365 Metadata Mapper Online API",
    version="1.0.0",
    description="Online API for source-to-target metadata mapping.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "D365 Metadata Mapper Online API",
        "status": "running",
        "endpoints": ["/health", "/map/fields", "/map/files"],
    }


@app.get("/health")
def health():
    return {"ok": True}


def run_mapping(source_metadata: list[dict], target_metadata: list[dict]) -> dict:
    matcher = Matcher()
    nomap_ai = NoMapAIAssistant(top_n=3)
    decisions: list[dict] = []

    for target in target_metadata:
        result = matcher.match_target(target, source_metadata)

        if result is None:
            decisions.append(
                {
                    "target_sheet": target.get("sheet_name", ""),
                    "target_field": target["field"],
                    "target_description": target.get("description", ""),
                    "source_field": "NoMap",
                    "source_description": "",
                    "source_entity": "",
                    "source_sheet": "",
                    "source_file": "",
                    "confidence": 0,
                    "method": "No Match",
                    "status": "NoMap",
                    "reason": "No candidate above threshold",
                    "mapping_source": "NoMap",
                    "ai_suggested_source": "",
                    "ai_confidence": "",
                    "ai_method": "",
                    "ai_reason": "",
                    "ai_alternatives": "",
                }
            )
            continue

        decisions.append(
            {
                "target_sheet": target.get("sheet_name", ""),
                "target_field": result["target_field"],
                "target_description": result.get("target_description", ""),
                "source_field": result["source_field"],
                "source_description": result.get("source_description", ""),
                "source_entity": result.get("source_entity", ""),
                "source_sheet": result.get("source_sheet", ""),
                "source_file": result.get("source_file", ""),
                "confidence": result["confidence"],
                "method": result["method"],
                "status": result["status"],
                "reason": result["reason"],
                "mapping_source": (
                    result.get("source_entity", "")
                    or result.get("source_sheet", "")
                    or result.get("source_file", "")
                ),
                "ai_suggested_source": "",
                "ai_confidence": "",
                "ai_method": "",
                "ai_reason": "",
                "ai_alternatives": "",
            }
        )

    used_sources = set(matcher.used_source_fields)

    remaining_sources = [
        x for x in source_metadata
        if x.get("source_id", x.get("field", "")) not in used_sources
    ]

    unmapped_source_review: list[dict] = []

    for source in remaining_sources:

        suggestions = nomap_ai.suggest_targets_for_unmapped_source(
            source,
            target_metadata
        )

        top = suggestions[0] if suggestions else None

        alternatives = ""

        if suggestions:
            alternatives = " | ".join([
                f"{x['target_field']} ({x['confidence']})"
                for x in suggestions
            ])

        unmapped_source_review.append({
            "source_field": source.get("field", ""),
            "source_description": source.get("description", ""),
            "suggested_target": top["target_field"] if top else "",
            "confidence": top["confidence"] if top else "",
            "method": top["method"] if top else "",
            "reason": top["reason"] if top else "",
            "alternatives": alternatives,
        })

    summary = {
        "Total": len(decisions),
        "Auto Accept": sum(1 for d in decisions if d["status"] == "Auto Accept"),
        "Review": sum(1 for d in decisions if d["status"] == "Review"),
        "NoMap": sum(1 for d in decisions if d["status"] == "NoMap"),
    }

    return {
        "summary": summary,
        "decisions": decisions,
        "unmapped_source_review": unmapped_source_review,
    }


@app.post("/map/fields")
def map_fields(payload: MapFieldsRequest):
    if not payload.source_metadata:
        raise HTTPException(status_code=400, detail="source_metadata cannot be empty")

    if not payload.target_metadata:
        raise HTTPException(status_code=400, detail="target_metadata cannot be empty")

    source_metadata = [item.model_dump() for item in payload.source_metadata]

    target_metadata = [
        {
            "row": index + 1,
            "field": item.field,
            "description": item.description,
        }
        for index, item in enumerate(payload.target_metadata)
    ]

    return run_mapping(source_metadata, target_metadata)


@app.post("/map/files")
def map_files(
    source_file: UploadFile | None = File(default=None),
    source_files: list[UploadFile] | None = File(default=None),
    target_file: UploadFile = File(...),
):
    uploaded_sources: list[UploadFile] = []

    if source_file is not None:
        uploaded_sources.append(source_file)

    if source_files:
        uploaded_sources.extend(source_files)

    if not uploaded_sources:
        raise HTTPException(status_code=400, detail="At least one source file is required")

    source_names = [((f.filename or "").lower()) for f in uploaded_sources]
    target_name = (target_file.filename or "").lower()

    if not all(name.endswith((".xlsx", ".csv", ".txt")) for name in source_names):
        raise HTTPException(status_code=400, detail="Each source file must be xlsx, csv, or txt")

    if not target_name.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Target file must be xlsx")

    try:
        source_metadata = []

        for uploaded_source in uploaded_sources:
            source_adapter = UploadedFileAdapter(uploaded_source)
            source_reader = SourceMetadataReader(source_adapter)
            source_reader.load()
            source_metadata.extend(source_reader.get_metadata())

        target_file.file.seek(0)
        workbook = WorkbookHandler(target_file.file)
        target_metadata = workbook.get_target_fields()

        result = run_mapping(source_metadata, target_metadata)

        for target_row, decision in zip(target_metadata, result["decisions"]):
            workbook.update_source_field(
                target_row["row"],
                decision["source_field"],
                target_row.get("sheet_name")
            )
            workbook.update_mapping_origin(
                target_row["row"],
                decision.get("mapping_source", ""),
                target_row.get("sheet_name")
            )

        mapped_output = BytesIO()
        workbook.save(mapped_output)

        audit_output = BytesIO()
        with pd.ExcelWriter(audit_output, engine="openpyxl") as writer:
            pd.DataFrame(result["decisions"]).to_excel(
                writer,
                index=False,
                sheet_name="Target Mapping Audit"
            )
            pd.DataFrame(result.get("unmapped_source_review", [])).to_excel(
                writer,
                index=False,
                sheet_name="Unmapped Source AI Review"
            )

        package_output = BytesIO()
        with zipfile.ZipFile(package_output, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("Mapped_Target_Metadata.xlsx", mapped_output.getvalue())
            archive.writestr("Mapping_Audit_Report.xlsx", audit_output.getvalue())
            archive.writestr("Summary.json", json.dumps(result["summary"], indent=2))

        package_output.seek(0)

        return StreamingResponse(
            package_output,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=Mapping_Output.zip",
            },
        )

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex
