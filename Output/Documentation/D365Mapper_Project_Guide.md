# D365 Metadata Mapper V3

## 1. What This Project Does

This project maps legacy ERP metadata fields to Microsoft Dynamics 365 Finance and Operations target metadata.

It supports two usage modes:

- Streamlit UI for business users (upload files, generate mapping, download output)
- FastAPI for system-to-system integration (JSON or file API)

Primary outcomes:

- Faster metadata mapping during data migration
- Consistent mapping decisions using rules and business dictionaries
- Audit output for review, governance, and sign-off

## 2. Why So Many Python Engines Exist

Metadata matching is not one simple string comparison. Legacy names are often abbreviated, compressed, or domain-specific. This solution uses specialized engines so each problem is solved correctly.

### Engine design purpose

- Normalization engine: cleans and standardizes text before matching
- Abbreviation expansion engine: expands compressed legacy tokens into business words
- Concept engine: converts raw fields into business concepts for semantic matching
- Dictionary engines: map known business synonyms and D365 concepts
- Alias engine: handles enterprise-approved direct alias mappings
- Rule engine: blocks invalid semantic conflicts (for example customer vs vendor)
- Scoring engine: evaluates all matching rules and returns confidence + reason
- Ranking engine: picks the best candidate when multiple high-confidence options exist
- Matcher engine: orchestrates scoring, filtering, and ambiguity handling for each target field
- Audit/report components: produce transparent outputs and review artifacts

This modular design is easier to tune, test, and govern than one monolithic script.

## 3. Core File Map

- [app.py](app.py): Streamlit web app
- [online_api.py](online_api.py): FastAPI service
- [matcher.py](matcher.py): target-to-source orchestration
- [scorer.py](scorer.py): multi-rule confidence scoring
- [ranking.py](ranking.py): tie-break and enterprise ranking
- [rules.py](rules.py): negative business rules
- [semantic_matcher.py](semantic_matcher.py): concept-level semantic score
- [concept_engine.py](concept_engine.py): concept extraction pipeline with cache
- [abbreviation_expander.py](abbreviation_expander.py): field expansion logic
- [normalizer.py](normalizer.py): normalization and token helpers
- [enterprise_alias_dictionary.py](enterprise_alias_dictionary.py): enterprise alias table
- [d365_dictionary.py](d365_dictionary.py): D365 business concept mapping
- [business_dictionary.py](business_dictionary.py): business synonym expansion
- [excel_handler.py](excel_handler.py): source metadata parser
- [workbook_handler.py](workbook_handler.py): target workbook read/write
- [audit_logger.py](audit_logger.py): audit table + summary generation
- [config.py](config.py): thresholds, headers, and constants
- [requirements.txt](requirements.txt): Python dependencies
- [ONLINE_INTEGRATION.md](ONLINE_INTEGRATION.md): API/UI integration notes

## 4. End-to-End Functional Flow

### A) Streamlit UI flow

1. User uploads source metadata file (xlsx/csv/txt).
2. User uploads target D365 template workbook (xlsx).
3. App reads source and target structures.
4. For each target field, matcher evaluates all valid source candidates.
5. Scoring and ranking choose best source field or NoMap.
6. App writes source mapping into target workbook.
7. App generates audit report and summary metrics.
8. User downloads mapped workbook and audit output.

### B) API flow

1. Client calls [online_api.py](online_api.py) endpoint:
   - POST /map/fields (JSON in, JSON out), or
   - POST /map/files (files in, zip out)
2. API executes same matcher/scorer pipeline.
3. API returns decisions and summary (and output package for file mode).

## 5. Matching Logic Flow (Inside Engine)

1. Normalize source and target field data.
2. Apply enterprise alias match first (high-confidence shortcut).
3. Evaluate all rule families in scorer:
   - exact
   - normalized
   - D365 dictionary
   - business fingerprint
   - token/synonym/acronym/contains
   - description-based
   - fuzzy
   - semantic concept
4. Keep highest scoring rule result.
5. Filter low-confidence candidates.
6. Rank remaining candidates.
7. Mark ambiguous close scores as Review.
8. Return Auto Accept, Review, or NoMap with reason.

## 6. Requirements and Prerequisites

### Business prerequisites

- Source metadata file with field names (description optional)
- Target D365 template with field column and source_field column
- Known enterprise aliases and dictionary terms maintained over time

### Technical prerequisites

- Python 3.11+ (recommended)
- Git
- Internet access for dependency install/deployment

### Install dependencies

```bash
pip install -r requirements.txt
```

## 7. Local Run Instructions

### Streamlit UI

```bash
streamlit run app.py
```

### FastAPI

```bash
python -m uvicorn online_api:app --host 127.0.0.1 --port 8000
```

Then open:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## 8. Deployment Options

### Option 1 (current demo): Render

Recommended for quick external demo.

- Deploy as Docker web service
- Use [Dockerfile](Dockerfile)
- Public URL can be shared with users

Important:

- Free plans may sleep when idle
- Treat public URL as internet-facing unless access controls are added

### Option 2 (enterprise): Azure

Recommended for production organization rollout.

Typical stack:

- Azure App Service or Azure Container Apps
- Azure API Management
- Microsoft Entra ID authentication
- Key Vault for secrets
- Application Insights for monitoring

## 9. Security and Governance Guidance

For production usage:

1. Add authentication and access control.
2. Restrict CORS (do not keep wildcard in production API).
3. Enforce file size/type limits and validation.
4. Store audit logs in controlled storage.
5. Use non-production metadata for public demos.

## 10. How This Should Work in Future

### Near term

- Continue dictionary and alias tuning by migration domain
- Expand regression test dataset for quality stability
- Keep confidence thresholds under governance review

### Mid term

- Add role-based access and approval workflow for Review mappings
- Introduce versioned dictionaries and change history
- Add monitoring dashboards for mapping quality KPIs

### Long term

- Integrate with enterprise migration pipelines
- Provide API-first orchestration for batch mapping at scale
- Add controlled AI-assisted suggestions for low-confidence cases

## 11. Suggested Operating Model

1. Business team owns dictionary and alias updates.
2. Data migration team owns template quality and test scenarios.
3. Engineering team owns runtime, deployment, security, and CI/CD.
4. Weekly governance reviews assess:
   - Auto Accept percentage
   - Review percentage
   - NoMap percentage
   - false positives and false negatives

## 12. Troubleshooting Quick Notes

- If API localhost URLs do not open, verify dependencies from [requirements.txt](requirements.txt) are installed.
- If Render Docker build cannot find requirements.txt, check [.dockerignore](.dockerignore) rules.
- If mapping quality is weak for specific domains, update business/alias dictionaries before changing core logic.

## 13. Current Status Summary

- GitHub repository is set up and push process is working.
- Render deployment is live for Streamlit demo.
- Automated compile/test checks are added for baseline stability.

---

For API endpoint usage details and sample payloads, see [ONLINE_INTEGRATION.md](ONLINE_INTEGRATION.md).
