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

            suggestions = nomap_ai.suggest_for_nomap(
                target,
                source_metadata
            )

            top = suggestions[0] if suggestions else None

            alternatives = ""

            if suggestions:
                alternatives = " | ".join([
                    f"{x['source_field']} ({x['confidence']})"
                    for x in suggestions
                ])

            decisions.append(
                {
                    "target_field": target["field"],
                    "target_description": target.get("description", ""),
                    "source_field": "NoMap",
                    "source_description": "",
                    "confidence": 0,
                    "method": "No Match",
                    "status": "NoMap",
                    "reason": "No candidate above threshold",
                    "ai_suggested_source": top["source_field"] if top else "",
                    "ai_confidence": top["confidence"] if top else "",
                    "ai_method": top["method"] if top else "",
                    "ai_reason": top["reason"] if top else "",
                    "ai_alternatives": alternatives,
                }
            )
            continue

        decisions.append(
            {
                "target_field": result["target_field"],
                "target_description": result.get("target_description", ""),
                "source_field": result["source_field"],
                "source_description": result.get("source_description", ""),
                "confidence": result["confidence"],
                "method": result["method"],
                "status": result["status"],
                "reason": result["reason"],
                "ai_suggested_source": "",
                "ai_confidence": "",
                "ai_method": "",
                "ai_reason": "",
                "ai_alternatives": "",
            }
        )

    summary = {
        "Total": len(decisions),
        "Auto Accept": sum(1 for d in decisions if d["status"] == "Auto Accept"),
        "Review": sum(1 for d in decisions if d["status"] == "Review"),
        "NoMap": sum(1 for d in decisions if d["status"] == "NoMap"),
    }

    return {"summary": summary, "decisions": decisions}


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
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...),
):
    source_name = (source_file.filename or "").lower()
    target_name = (target_file.filename or "").lower()

    if not source_name.endswith((".xlsx", ".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Source file must be xlsx, csv, or txt")

    if not target_name.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Target file must be xlsx")

    try:
        source_adapter = UploadedFileAdapter(source_file)
        source_reader = SourceMetadataReader(source_adapter)
        source_reader.load()
        source_metadata = source_reader.get_metadata()

        target_file.file.seek(0)
        workbook = WorkbookHandler(target_file.file)
        target_metadata = workbook.get_target_fields()

        result = run_mapping(source_metadata, target_metadata)

        for target_row, decision in zip(target_metadata, result["decisions"]):
            workbook.update_source_field(target_row["row"], decision["source_field"])

        mapped_output = BytesIO()
        workbook.save(mapped_output)

        audit_output = BytesIO()
        pd.DataFrame(result["decisions"]).to_excel(audit_output, index=False, engine="openpyxl")

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
