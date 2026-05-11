# Import Plan: Study Data Ingestion into chan_cras

## 1. Purpose
This document defines the implementation plan to ingest longitudinal psychiatry study datasets into the `chan_cras` PostgreSQL application schema.

Target entities:
- `Study`
- `Subject`
- `Procedure`
- `Event`
- Link tables: `StudySubjectLink`, `StudyUserLink` (existing app use)

The plan is optimized for:
- PostgreSQL (relational)
- Highly normalized core schema
- Unified subject record across studies
- Rapid execution timeline (1-2 weeks)
- Data quality, migration safety, and analytics readiness (R/Python)

## 2. Current App Data Model Fit
The app already supports the required import targets:
- `Study`: project/cohort definitions
- `Subject`: participant registry
- `StudySubjectLink`: many-to-many enrollment + `legacy_code`
- `Procedure`: protocol definitions with `form_data_schema` JSONB
- `Event`: subject-procedure-time records with `procedure_data` JSONB
- `AuditLog`: immutable change history

This is a strong fit for importing mixed-format historical studies while keeping normalized core relationships.

## 3. Import Design Principles
1. Preserve normalized relational core.
2. Use one unified subject identity across all cohorts.
3. Keep source provenance for every imported record.
4. Make loads idempotent (safe re-run).
5. Quarantine ambiguous and failed records rather than forcing bad joins.
6. Validate at each stage (staging, conformed, production).
7. Keep dry-run tooling isolated from the existing `chan_cras` application codebase.

## 4. Scope Overview
Primary wave focuses on `1400 sample` streams:
- Baseline: `HCS3data.csv`
- Follow-up streams: `hcs10`, `hcs20`, `TRS_12FU`, `crf_trs`
- CDARS derivatives: `cleaned_Rx_Antipsychotic202411.csv`, `monthly_DDD_updated.csv`, `mortality20year.csv`, `Ref.Keys_1400.csv`
- Crosswalk support: `masterlist_linkage` files

Out of scope for Wave 1 (unless explicitly expanded):
- Parallel project roots (`treatment_resistant_schizophrenia`, `fep`) as primary load sources

## 4.1 Wave 1B Scope Extension (FEP + TRS Parallel Projects)
Wave 1B is executed after Wave 1 passes all hard gates.

Wave 1B source roots:
- `fep`
- `treatment_resistant_schizophrenia`

Confirmed Wave 1B policy decisions:
- Sequence: Wave 1B runs after Wave 1.
- Study granularity: one `Study` per folder stream.
- Procedure design: medication workbooks map to dedicated medication procedure families.
- Masterlist workbooks: identity/linkage source only by default (not direct `Event` facts unless explicitly approved).
- HKID matching: allowed only under restricted linkage governance controls.

Wave 1B study mapping (folder-level):
- `FEP`
- `TRS_GRF`
- `TRS_VS`
- `TRS_CLOZ_DOSAGE`

Recommended Wave 1B ingest order:
1. Identity and enrollment foundations
   - `fep/Masterlist eye gaze_2.xlsx`
   - `treatment_resistant_schizophrenia/GRF TRS/Masterlist_GRF.xlsx`
   - `treatment_resistant_schizophrenia/VS/Masterlist copy.xlsx`
   - `treatment_resistant_schizophrenia/clozapine dosage/Cloz_dosage_masterlist.xlsx`
2. TRS_GRF core clinical datasets
   - `treatment_resistant_schizophrenia/GRF TRS/TRS_Database.xlsx`
   - `treatment_resistant_schizophrenia/GRF TRS/Treatment_Responsive_Database.xlsx`
   - `treatment_resistant_schizophrenia/GRF TRS/HC_Database.xlsx`
   - `treatment_resistant_schizophrenia/GRF TRS/GABA_TRS_GRF.xlsx`
   - `treatment_resistant_schizophrenia/GRF TRS/UTRS_dataset.xlsx`
3. TRS_VS core clinical datasets
   - `treatment_resistant_schizophrenia/VS/Study1_TRS_Database copy.xlsx`
   - `treatment_resistant_schizophrenia/VS/Study2_FEP_Database copy.xlsx`
   - `treatment_resistant_schizophrenia/VS/Study2_Chronic_Database copy.xlsx`
   - `treatment_resistant_schizophrenia/VS/Study2_HC_Database copy.xlsx`
4. Medication-focused datasets (dedicated procedures)
   - `treatment_resistant_schizophrenia/VS/Study1_TRS_medication.xlsx`
   - `treatment_resistant_schizophrenia/VS/Study2_FEP_medication.xlsx`
   - `treatment_resistant_schizophrenia/VS/Study2_Chronic_medication.xlsx`
   - `treatment_resistant_schizophrenia/clozapine dosage/Cloz_dosage_database.xlsx`
   - `treatment_resistant_schizophrenia/clozapine dosage/meds_25.xlsx`
5. Casenote and review datasets
   - `treatment_resistant_schizophrenia/VS/Study1_TRS_casenote_review.xlsx`

Wave 1B mapping rules:
- `Subject` creation always flows through canonical identity matching against existing subject identity map.
- If masterlist and clinical workbook identities disagree, route to ambiguity queue; do not force-match.
- `StudySubjectLink.legacy_code` preserves source participant identifiers per folder stream.
- Event payload fields remain in `procedure_data` JSONB with source provenance metadata.

## 4.2 Wave 1 Initial Files to Ingest
The recommended first-pass ingestion order should follow the dependency chain needed to build identity, enrollment, and core event history safely.

Reference index:
- See [README.md](README.md) for the full workspace Data Dictionary Index and direct links to the primary study files.

Recommended initial files:
1. Identity and linkage foundation
   - [masterlist_linkage/overall_masterlist_crosswalk.csv](masterlist_linkage/overall_masterlist_crosswalk.csv)
   - [masterlist_linkage/overall_masterlist_crosswalk_summary.csv](masterlist_linkage/overall_masterlist_crosswalk_summary.csv)
   - [1400 sample/1400cdars/Ref.Keys_1400.csv](1400%20sample/1400cdars/Ref.Keys_1400.csv)
2. Anchor cohort
   - [1400 sample/HCS3data.csv](1400%20sample/HCS3data.csv)
3. Early follow-up streams
   - [1400 sample/hcs10/Interview(209)_changeFrec.csv](1400%20sample/hcs10/Interview(209)_changeFrec.csv)
   - [1400 sample/hcs10/Data Entry_Med_combined_120724_update0726.csv](1400%20sample/hcs10/Data%20Entry_Med_combined_120724_update0726.csv)
   - [1400 sample/hcs20/qualitative_description_dataset.csv](1400%20sample/hcs20/qualitative_description_dataset.csv)
4. TRS follow-up stream
   - [1400 sample/TRS_12FU/Full_1400_clozform_20220607.csv](1400%20sample/TRS_12FU/Full_1400_clozform_20220607.csv)
5. CDARS derived outcomes
   - [1400 sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv](1400%20sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv)
   - [1400 sample/1400cdars/monthly_DDD_updated.csv](1400%20sample/1400cdars/monthly_DDD_updated.csv)
   - [1400 sample/1400cdars/mortality20year.csv](1400%20sample/1400cdars/mortality20year.csv)

Rationale for this order:
- Crosswalk and reference-key files establish the canonical subject identity map.
- HCS3 provides the anchor subject set and baseline cohort structure.
- HCS10, HCS20, and TRS_12FU add longitudinal procedures and events.
- CDARS derived files are loaded after subject identity is stable so medication and mortality records can be linked deterministically.

## 4.3 Wave 1 Source-to-Target Mapping

| Source file | Primary role in import | Main target tables | Notes |
|---|---|---|---|
| [masterlist_linkage/overall_masterlist_crosswalk.csv](masterlist_linkage/overall_masterlist_crosswalk.csv) | Canonical subject identity resolution | staging identity tables, `Subject`, subject alias/link tables | Foundation for deduplicating subjects across streams |
| [masterlist_linkage/overall_masterlist_crosswalk_summary.csv](masterlist_linkage/overall_masterlist_crosswalk_summary.csv) | QC and reconciliation support | import QC reports, validation outputs | Not a primary fact table source |
| [1400 sample/1400cdars/Ref.Keys_1400.csv](1400%20sample/1400cdars/Ref.Keys_1400.csv) | CDARS reference-key linkage | staging identity tables, subject alias/link tables | Restricted linkage asset; governs matching to CDARS-derived data |
| [1400 sample/HCS3data.csv](1400%20sample/HCS3data.csv) | Anchor cohort baseline and 3-year follow-up facts | `Study`, `Subject`, `StudySubjectLink`, `Procedure`, `Event` | Core anchor dataset for cohort membership and baseline event history |
| [1400 sample/hcs10/Interview(209)_changeFrec.csv](1400%20sample/hcs10/Interview(209)_changeFrec.csv) | HCS10 interview event data | `Study`, `StudySubjectLink`, `Procedure`, `Event` | Subject creation only if missing from anchor identity map |
| [1400 sample/hcs10/Data Entry_Med_combined_120724_update0726.csv](1400%20sample/hcs10/Data%20Entry_Med_combined_120724_update0726.csv) | HCS10 medication review data | `Procedure`, `Event` | Loaded as study-specific medication procedure events |
| [1400 sample/hcs20/qualitative_description_dataset.csv](1400%20sample/hcs20/qualitative_description_dataset.csv) | HCS20 qualitative subsample and descriptors | `Study`, `StudySubjectLink`, `Procedure`, `Event` | Represents a subset stream inside HCS20 |
| [1400 sample/TRS_12FU/Full_1400_clozform_20220607.csv](1400%20sample/TRS_12FU/Full_1400_clozform_20220607.csv) | TRS 12-year interview plus linked HCS3 context | `Study`, `StudySubjectLink`, `Procedure`, `Event` | Requires careful separation of anchor fields vs 12-year event payload |
| [1400 sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv](1400%20sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv) | Longitudinal antipsychotic exposure | `Procedure`, `Event` | One or more medication events per subject-time interval |
| [1400 sample/1400cdars/monthly_DDD_updated.csv](1400%20sample/1400cdars/monthly_DDD_updated.csv) | Monthly standardized medication intensity | `Procedure`, `Event` | Best modeled as repeated monthly medication-summary events |
| [1400 sample/1400cdars/mortality20year.csv](1400%20sample/1400cdars/mortality20year.csv) | Mortality outcome linkage | `Procedure`, `Event` | Prefer one mortality outcome procedure/event per subject |

Mapping rules for first-wave files:
- `Study` rows should be created once per cohort stream before file-level event loads begin.
- `Subject` rows should be created from the canonical identity map, not independently per file.
- `StudySubjectLink` should preserve the per-study legacy identifier whenever present.
- `Procedure` rows should represent stable assessment or data-collection types, not individual files.
- `Event` rows should capture the timepoint-specific observation, with variable source columns stored in `procedure_data` JSONB.

## 5. Canonical Mapping Strategy
## 5.1 Study Mapping
Create one `Study` per major cohort stream (initial recommendation):
- HCS3 (3-year)
- HCS10 (10-year)
- HCS20 (20-year)
- TRS_12FU (12-year)
- CRF_TRS (25-year)
- CDARS Longitudinal Linkage

Store source metadata in `Study.metadata_blob` (folder, inclusion notes, timeframe).

## 5.2 Subject Mapping
Create one unified `Subject` record per canonical person.

Identity resolution priority:
1. Existing crosswalks and reference-key files
2. Explicit study IDs (`HCS3_id`, `HCS10ID`, `HCS20ID`, `TRSID`)
3. CDARS `Reference_Key` linkage
4. HKID-based link only under governed access controls

Per-study participant identifiers are stored in `StudySubjectLink.legacy_code`.

## 5.3 Procedure Mapping
Define reusable procedures per study, such as:
- Baseline case-note extraction
- Follow-up interview battery
- Medication review
- Hospitalization review
- Mortality update

Use `Procedure.form_data_schema` to define field-level expected payload shape where stable.

## 5.4 Event Mapping
Each imported observation becomes an `Event` at the grain:
- `subject_id + study_id + procedure_id + event_datetime`

Use:
- `status = completed` for historical data
- `procedure_data` JSONB for variable/wide fields
- `metadata_blob` for provenance (source file, row index, parser version, import batch)

## 6. Required Enhancements Before Load
1. Add subject alias support (recommended):
   - New `subject_alias` table (or equivalent) to store multiple external IDs per subject.
2. Add import provenance fields:
   - `import_batch_id`, `source_file`, `source_row_number` (or equivalent metadata standard).
3. Add import control tables:
   - batch registry
   - error/rejection log
   - ambiguous-match queue

For the dry run, these support objects must be created only inside the `cras_dryrun` database and managed by the separate `dryrun_import` project, not by modifying existing `chan_cras` application code or `chan_cras` Alembic history.

## 6.1 Dry-Run Isolation Policy
Dry-run implementation must follow these constraints:
- Do not modify `chan_cras/backend/app/*`.
- Do not add dry-run scripts under `chan_cras/backend/*`.
- Do not add dry-run Alembic revisions to `chan_cras/backend/alembic`.
- Do not change frontend, backend runtime behavior, or existing CRAS APIs for rehearsal purposes.
- Place all rehearsal-only code, schema bootstrap logic, and reports in a separate top-level project: `dryrun_import/`.
- Apply any additional dry-run-only support tables, views, or helper functions only to the `cras_dryrun` database.

## 7. Staged ETL Pipeline
## 7.1 Stage A: Raw Landing
- Load source files as-is into raw staging tables.
- Minimal typing; no destructive transforms.
- Preserve exact row content and source hash.

## 7.2 Stage B: Conformed Layer
- Normalize missing codes (e.g., 888/999/blank semantics).
- Standardize dates and categorical values.
- Build harmonized identity fields.
- Produce deterministic conformed records ready for target loads.

## 7.3 Stage C: Production Load
Upsert order:
1. `Study`
2. `Procedure`
3. `Subject`
4. `StudySubjectLink`
5. `Event`

Every load run is batch-tagged and replay-safe.

## 8. Idempotency and Keying Rules
- `Study`: keyed by canonical title/code policy.
- `Procedure`: keyed by `(study_id, normalized_name)`.
- `Subject`: keyed by canonical identity map; never duplicate per study.
- `StudySubjectLink`: keyed by `(study_id, subject_id)`.
- `Event`: deduplicate by natural event key and source provenance.

Re-running the same batch should not create duplicate entities or links.

## 9. Data Quality and Validation Gates
## 9.1 Pre-load checks
- Required columns present in source file.
- Parseability checks (date, numeric domains).
- Identifier completeness checks.

## 9.2 In-load checks
- FK integrity failures
- Duplicate natural key collisions
- schema/form payload compatibility issues

## 9.3 Post-load checks
- Row-count reconciliation: source vs loaded vs rejected
- Subject uniqueness audit across all studies
- Event duplication audit
- Null-critical-field audit
- Summary report per study and per batch

## 10. Security and Governance
- HKID may be used only in controlled link workflows.
- Store least-necessary identifiers in core app tables.
- Keep identifiable linkage in restricted access paths.
- Audit all import actions via existing audit logging standards.

## 11. 2-Week Phased Execution Plan
## Day 1-2: Identity and Crosswalk Foundation
- Build canonical subject identity map
- Resolve and queue ambiguous/unmatched records
- Confirm subject merge policy

## Day 2-3: Import Contract + Schema Migration
- Finalize study/procedure/event granularity
- Add alias/provenance/import-control schema changes in the isolated dry-run project
- Prepare standalone schema bootstrap scripts for `cras_dryrun`

## Day 4-6: ETL Implementation
- Build raw landing loaders (CSV/XLSX)
- Build conformed transforms
- Implement production upsert pipeline

## Day 6-8: Initial Dataset Load
- Load Wave 1 datasets in dependency order
- Run idempotency tests (repeat batch)
- Fix mapping edge cases

## Day 8-9: QA and Reconciliation
- Complete all validation gates
- Produce load and rejection reports
- Review unresolved ambiguities

## Day 10: Analytics and Handoff
- Publish analysis-ready SQL views
- Deliver data dictionary + source-to-target mapping
- Document rerun/backfill procedure

## Day 11-12: Wave 1B Extension (FEP + TRS Parallel Projects)
- Execute Wave 1B ingestion in the order defined in Section 4.1
- Apply the same hard gates used for Wave 1 (exact-match reconciliation, unresolved ambiguity = fail)
- Run idempotency rerun for Wave 1B batch
- Produce Wave 1B-specific reconciliation and validation report

## 12. Deliverables
1. Standalone dry-run schema bootstrap scripts for import support additions
2. ETL scripts (staging, transform, load)
3. Batch execution runner and logs
4. Rejection and ambiguity reports
5. Mapping specification (source -> target)
6. Validation report template and completed run output
7. Analysis-ready views for R/Python consumption

## 13. Open Decisions (Must Confirm)
1. Wide longitudinal files (e.g., monthly columns):
   - explode to many events vs fewer events with richer JSON payloads?

Resolved decisions (confirmed):
- Include FEP and TRS parallel projects after Wave 1 as Wave 1B.
- Use one study per folder stream for Wave 1B.
- Keep medication workbooks as dedicated medication procedure families.
- Use masterlist workbooks as identity/linkage sources by default.
- Allow HKID-based matching only in restricted linkage workflows.
- Approve dry-run schema support objects only inside the isolated `dryrun_import` project and `cras_dryrun` database.

## 14. Success Criteria
The import is considered successful when:
- All in-scope datasets are loaded with deterministic rerun behavior.
- No unresolved FK violations or duplicate subject identities in production tables.
- Reconciliation reports are accepted by data owners.
- Analysts can query unified subject/event data directly from PostgreSQL for R/Python workflows.

## 15. Work Log

### Session 1 (2026-04-23)

**Completed:**
- ✅ Established strict dry-run isolation policy (no modifications to `chan_cras/backend/app/*` or Alembic histories)
- ✅ Scaffolded complete isolated `dryrun_import/` Python project with CLI entrypoint
- ✅ Installed `dryrun_import` as editable package into existing root `.venv`
- ✅ Fixed Python version compatibility (3.10 vs 3.11)
- ✅ Created schema-only PostgreSQL dump from `chan_cras` to `dryrun_import/sql/chan_cras_schema_only.sql`
- ✅ Recreated fresh `cras_dryrun` database and loaded baseline schema (10 public tables)
- ✅ Applied dry-run support schema bootstrap (9 new tables in `dryrun_import` schema)
- ✅ Implemented batch creation step (Step 00) with deterministic ID generation
- ✅ Implemented Wave 1 staging step (Step 10) with robust CSV parsing and encoding fallback
  - Fixed UnicodeDecodeError handling for mixed-encoding bytes (0xa0 sequences)
- ✅ Expanded Wave 1 scope from 3 foundation files to full 11-file set:
  - 3 identity/linkage files from `masterlist_linkage/`
  - 1 anchor baseline file: `HCS3data.csv`
  - 3 follow-up files: `hcs10`, `hcs20`, `TRS_12FU`
  - 3 CDARS derivatives from `1400cdars/`
- ✅ Implemented conform/load/validate/reconcile/idempotency/finalize steps (Steps 20-70)
- ✅ Executed full Wave 1 pipeline end-to-end:
  - **Batch ID:** `DRYRUN_WAVE1_20260422_200659`
  - **Source files staged:** 11
  - **Total rows landed:** 622,197
  - **Conformed rows:** 622,197 (100% match)
  - **Validation:** pass (raw_rows_present=true, conformed_matches_raw_count=true, duplicate_raw_keys=false)
  - **Reconciliation:** pass (exact file-by-file match, delta=0 on all 11 files)
  - **Idempotency:** pass (no new duplicates on rerun)
  - **Report artifact:** `dryrun_import/reports/DRYRUN_WAVE1_20260422_200659_wave1_report.json`
- ✅ Updated documentation:
  - [ImportPlan.md](ImportPlan.md): Added Section 6.1 "Dry-Run Isolation Policy", updated execution plan
  - [RehearsalRunbook.md](RehearsalRunbook.md): Updated confirmed decisions, removed Alembic references
  - [chan_cras/CHANGELOG.md](chan_cras/CHANGELOG.md): Documented isolated dry-run project and Wave 1 batch results
- ✅ Moved [CHANGELOG.md](CHANGELOG.md) from `chan_cras/` to workspace root

**Blockers Resolved:**
- Python version mismatch (3.10 vs 3.11): Patched `pyproject.toml` to accept 3.10+
- CSV encoding heterogeneity: Applied `errors='replace'` parameter to CSV reader
- Long-running terminal timeout: Used background execution with `await_terminal()`

**Current State:**
- `cras_dryrun` database: fully seeded with baseline schema + dry-run support objects
- Root `.venv`: `dryrun_import==0.1.0` installed and ready for CLI use
- Wave 1 pipeline: Steps 00-70 complete, all gates passing
- Wave 1B pipeline: Steps 80-130 scaffolded but not yet implemented

**Next Actions (Pending User Direction):**
- Implement Wave 1B pipeline steps (80-130) for FEP + TRS parallel projects
- Extend staging to Wave 1B source files (same encoding robustness pattern)
- Implement real production load logic in Step 30 (entity insertion with identity mapping)
- Build Wave 1B execution with full scope and validation

