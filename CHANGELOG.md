# Changelog: Import Rehearsal Project

All notable changes to the dry-run import rehearsal project will be documented in this file.

The format is based on Keep a Changelog.

## Unreleased

### Completed (2026-04-25)
- Step 30/100 Production Load - Real Writes on `cras_dryrun` — **FULLY COMPLETE**
  - **Step 30** (`30_load_wave1.py`) writes to `public.subject`, `dryrun_import.subject_alias`, and `public.studysubjectlink` with checkpointed pagination (chunk_size=2000).
  - **Step 100** (`100_load_wave1b.py`) mirrors the same write path for Wave 1B; upgraded from `LIMIT 5000` to the same checkpointed paginated loader pattern.
  - **Schema fix**: switched from old `chan_cras.*` assumptions to `public.*` tables in `cras_dryrun` and corrected alias handling to use `subject_id`.
  - **Batch selection fix**: loaders pick latest non-empty batch by conformed row volume.
  - **Wave 1 full load results (2026-04-25):**
    - Batch `DRYRUN_WAVE1_20260422_200659` (622,197 conformed records): 31 loop iterations, all rows processed.
    - 3,427 subjects enrolled, 3,427 study links created. Batch status: `loaded_wave1_production`.
  - **Wave 1B full load results (2026-04-25):**
    - Batch `DRYRUN_WAVE1B_20260422_225455` (10,966 conformed records): 6 chunks, all rows processed.
    - 460 subjects enrolled, 10,506 no-ID rows skipped (expected non-subject detail rows). Batch status: `loaded_wave1b_production`.
  - **Final `cras_dryrun` totals (2026-04-25):**
    - `public.subject`: 3,887
    - `dryrun_import.subject_alias`: 3,887
    - `public.studysubjectlink`: 3,887
    - Link distribution: `HCS3` 1,400 · `STUDY` 1,557 · `TRS12` 470 · `FEP` 338 · `TRS_GRF` 122

### Planned
- Ambiguity queue resolution and rejection handling workflows

## [Wave 1B Dry-Run] - 2026-04-23

### Added
- Wave 1B pipeline implementations for FEP + TRS datasets:
  - **Step 80** (`80_stage_wave1b.py`): Stage ingestion for CSV/TXT/XLSX/XLS from `fep/` and `treatment_resistant_schizophrenia/`
  - **Step 90** (`90_conform_wave1b.py`): Conformation into `conformed_record` with payload hash
  - **Step 100** (`100_load_wave1b.py`): Dry-run load summary recording (no production entity writes)
  - **Step 110** (`110_validate_wave1b.py`): Validation checks for presence, raw/conformed parity, and duplicate raw keys
  - **Step 120** (`120_reconcile_wave1b.py`): File-level source-to-staged reconciliation
  - **Step 130** (`130_idempotency_rerun_wave1b.py`): Idempotency duplicate-key verification
- Wave 1B report finalization step:
  - **Step 140** (`140_finalize_report_wave1b.py`): JSON report generation including stage, validation, reconciliation, and rejection log sections
- Wave 1B shared file discovery support in `pipeline/common.py` for deterministic file scanning under configured roots

### Executed
- Wave 1B batch: `DRYRUN_WAVE1B_20260422_225455`
  - **Source files discovered/staged:** 19
  - **Total rows landed:** 10,966
  - **Conformed rows:** 10,966 (100% match to staged raw rows)
  - **Validation status:** pass
  - **Reconciliation status:** pass (all staged files delta=0)
  - **Idempotency status:** pass
  - **Final batch status:** `finalized_wave1b`
  - **Report artifact:** `dryrun_import/reports/DRYRUN_WAVE1B_20260422_225455_wave1b_report.json`

### Fixed
- Wave 1B Excel robustness: stage step now logs malformed workbooks to `import_rejection_log` and continues processing remaining files instead of aborting the whole batch

### Noted During Execution
- Two source workbooks were rejected due to malformed stylesheet XML and recorded in `import_rejection_log`:
  - `treatment_resistant_schizophrenia/GRF TRS/HC_Database.xlsx`
  - `treatment_resistant_schizophrenia/clozapine dosage/Cloz_dosage_database.xlsx`

## [Wave 1 Dry-Run] - 2026-04-23

### Added
- Isolated dry-run import project scaffold in `dryrun_import/`:
  - Python package + CLI entrypoint for bootstrap and step execution
  - Dry-run schema bootstrap SQL and rollback scripts for `cras_dryrun`
  - Wave 1 and Wave 1B pipeline step files (Steps 00-130 scaffolded)
  - Report output folder with JSON batch reporting
- Wave 1 dry-run support objects in `cras_dryrun` database (`dryrun_import` schema):
  - `subject_alias` - identity mapping and deduplication
  - `import_batch` - batch-level tracking and status
  - `import_rejection_log` - failed record tracking
  - `import_ambiguity_queue` - unresolved identity conflicts
  - `raw_file_landing` - raw CSV data landing zone
  - `stage_file_summary` - file-level staging metadata
  - `conformed_record` - conformed/standardized records
  - `load_run_summary` - load execution tracking
  - `validation_result` - validation check results
  - `reconciliation_result` - source-to-staged row count verification
- Baseline schema-only PostgreSQL dump from production `chan_cras` database
  - Restored into `cras_dryrun` (10 public tables: Study, Subject, Procedure, Event, etc.)
- Wave 1 pipeline step implementations:
  - **Step 00** (`00_create_batch.py`): Batch creation with deterministic ID generation (format: `DRYRUN_WAVE1_YYYYMMDD_HHMMSS`)
  - **Step 10** (`10_stage_wave1.py`): CSV parsing with robust encoding handling (UTF-8-SIG + Latin-1 fallback)
  - **Step 20** (`20_conform_wave1.py`): Conformation with MD5 payload hashing
  - **Step 30** (`30_load_wave1.py`): Load summary recording (dry-run, no entity insertion yet)
  - **Step 40** (`40_validate_wave1.py`): Post-load validation checks (raw_rows_present, conformed_matches_raw_count, duplicate_raw_keys)
  - **Step 50** (`50_reconcile_wave1.py`): File-by-file source-to-staged reconciliation
  - **Step 60** (`60_idempotency_rerun.py`): Idempotency verification
  - **Step 70** (`70_finalize_report.py`): JSON report aggregation and output
- Wave 1 file scope: 11 datasets from `1400 sample` + `masterlist_linkage` + `1400cdars`:
  - 3 identity/linkage files (crosswalk masterlist variants)
  - 1 anchor baseline: `HCS3data.csv`
  - 3 follow-up files: `hcs10`, `hcs20`, `TRS_12FU`
  - 3 CDARS derivatives: cleaned antipsychotic Rx, monthly DDD, mortality, reference keys

### Executed
- Wave 1 batch: `DRYRUN_WAVE1_20260422_200659`
  - **Source files staged:** 11
  - **Total rows landed:** 622,197
  - **Conformed rows:** 622,197 (100% match to raw)
  - **Validation status:** pass
    - raw_rows_present: ✅
    - conformed_matches_raw_count: ✅
    - duplicate_raw_keys: ✅ (no duplicates)
  - **Reconciliation status:** pass (exact file-by-file match, delta=0 on all 11 files)
  - **Idempotency status:** pass (no new duplicates on rerun)
  - **Report artifact:** `dryrun_import/reports/DRYRUN_WAVE1_20260422_200659_wave1_report.json`

### Fixed
- CSV encoding heterogeneity: Applied `errors='replace'` to handle mixed-encoding bytes (0xa0 sequences)
- Python version compatibility: Updated `pyproject.toml` to accept Python 3.10+ (existing root `.venv` is 3.10.12)

### Planning & Documentation
- Added ImportPlan Section 6.1: "Dry-Run Isolation Policy" (no modifications to `chan_cras/backend/app/*`)
- Updated RehearsalRunbook with confirmed decisions and dry-run constraints
- Created work log in ImportPlan Section 15 tracking all session milestones
