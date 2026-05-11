# Rehearsal Runbook: Wave 1 + Wave 1B Dry Run Import into chan_cras

## 1. Purpose
This runbook defines a full dress rehearsal for the Wave 1 import and the Wave 1B extension before production execution.

This rehearsal is designed to prove:
- Schema readiness in a fresh database
- End-to-end import execution
- Data integrity and reconciliation quality
- Idempotent rerun behavior

Decisions confirmed:
- Rehearsal database starts empty
- Same PostgreSQL instance as current chan_cras, different database
- Rehearsal database name: cras_dryrun
- Import scripts need to be built
- Dry-run code must be isolated from the existing `chan_cras` application codebase
- Scope: Wave 1 followed by Wave 1B (FEP + TRS parallel projects)
- Reconciliation tolerance: exact match
- Hard gate on unresolved ambiguities: yes, block promotion
- Performance timing target: not required for this phase
- Final sign-off owner: you
- Wave 1B sequence: run after Wave 1 passes hard gates
- Wave 1B study granularity: one study per folder stream
- Medication workbooks: dedicated medication procedure families
- Masterlists: identity/linkage source only by default
- HKID matching: allowed only in restricted linkage workflows

## 2. Scope
In scope for this rehearsal:
- Wave 1 datasets defined in ImportPlan.md
- Wave 1B datasets from `fep` and `treatment_resistant_schizophrenia`
- Schema deployment through the isolated `dryrun_import` project
- Staging, conformed, and production load logic
- Validation checks and reconciliation report
- Idempotency rerun test

Out of scope:
- Any modification to existing `chan_cras` application code, migrations, API routes, or frontend behavior
- Performance benchmarking and SLA timing targets

## 3. Environments and Safety
### 3.1 Environment profile
- Host: same PostgreSQL instance as chan_cras
- Target dry-run database: cras_dryrun
- Dry-run implementation root: dryrun_import

### 3.2 Safety controls
- Never run rehearsal commands against chan_cras production database
- Require explicit environment printout before migration or import
- Require database name check at start of every import command
- Keep all dry-run artifacts batch-tagged
- Do not write dry-run code into `chan_cras/backend` or `chan_cras/frontend`

### 3.3 Required operator checks before each run
- Confirm PG_HOST
- Confirm PG_PORT
- Confirm PG_USER
- Confirm PG_DB equals cras_dryrun
- Confirm migration target is latest Alembic head

## 4. Wave 1 File Scope
Use the dependency order below:

1. Identity and linkage foundation
- masterlist_linkage/overall_masterlist_crosswalk.csv
- masterlist_linkage/overall_masterlist_crosswalk_summary.csv
- 1400 sample/1400cdars/Ref.Keys_1400.csv

2. Anchor cohort
- 1400 sample/HCS3data.csv

3. Early follow-up streams
- 1400 sample/hcs10/Interview(209)_changeFrec.csv
- 1400 sample/hcs10/Data Entry_Med_combined_120724_update0726.csv
- 1400 sample/hcs20/qualitative_description_dataset.csv

4. TRS follow-up
- 1400 sample/TRS_12FU/Full_1400_clozform_20220607.csv

5. CDARS outcomes
- 1400 sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv
- 1400 sample/1400cdars/monthly_DDD_updated.csv
- 1400 sample/1400cdars/mortality20year.csv

## 4.1 Wave 1B File Scope (run after Wave 1)
Use the dependency order below:

1. Identity and enrollment foundation (identity source only)
- fep/Masterlist eye gaze_2.xlsx
- treatment_resistant_schizophrenia/GRF TRS/Masterlist_GRF.xlsx
- treatment_resistant_schizophrenia/VS/Masterlist copy.xlsx
- treatment_resistant_schizophrenia/clozapine dosage/Cloz_dosage_masterlist.xlsx

2. TRS_GRF core clinical datasets
- treatment_resistant_schizophrenia/GRF TRS/TRS_Database.xlsx
- treatment_resistant_schizophrenia/GRF TRS/Treatment_Responsive_Database.xlsx
- treatment_resistant_schizophrenia/GRF TRS/HC_Database.xlsx
- treatment_resistant_schizophrenia/GRF TRS/GABA_TRS_GRF.xlsx
- treatment_resistant_schizophrenia/GRF TRS/UTRS_dataset.xlsx

3. TRS_VS core clinical datasets
- treatment_resistant_schizophrenia/VS/Study1_TRS_Database copy.xlsx
- treatment_resistant_schizophrenia/VS/Study2_FEP_Database copy.xlsx
- treatment_resistant_schizophrenia/VS/Study2_Chronic_Database copy.xlsx
- treatment_resistant_schizophrenia/VS/Study2_HC_Database copy.xlsx

4. Medication-focused datasets (dedicated procedures)
- treatment_resistant_schizophrenia/VS/Study1_TRS_medication.xlsx
- treatment_resistant_schizophrenia/VS/Study2_FEP_medication.xlsx
- treatment_resistant_schizophrenia/VS/Study2_Chronic_medication.xlsx
- treatment_resistant_schizophrenia/clozapine dosage/Cloz_dosage_database.xlsx
- treatment_resistant_schizophrenia/clozapine dosage/meds_25.xlsx

5. Casenote/review datasets
- treatment_resistant_schizophrenia/VS/Study1_TRS_casenote_review.xlsx

## 5. Rehearsal Architecture
### 5.1 Required script set (to implement)
Create these scripts under dryrun_import/src/dryrun_import/pipeline:
- 00_create_batch.py
- 10_stage_wave1.py
- 20_conform_wave1.py
- 30_load_wave1.py
- 40_validate_wave1.py
- 50_reconcile_wave1.py
- 60_idempotency_rerun.py
- 70_finalize_report.py
- 80_stage_wave1b.py
- 90_conform_wave1b.py
- 100_load_wave1b.py
- 110_validate_wave1b.py
- 120_reconcile_wave1b.py
- 130_idempotency_rerun_wave1b.py

### 5.2 Required database support objects (via Alembic)
Add dry-run-only support objects for:
- subject_alias table
- import_batch registry table
- import_rejection_log table
- import_ambiguity_queue table
- Optional helper views for reconciliation summaries

These objects must be created by the isolated `dryrun_import` project in `cras_dryrun` only, without changing `chan_cras` Alembic revisions or ORM models.

### 5.3 Batch identity standard
Each rehearsal run uses one immutable batch identifier, for example:
- DRYRUN_WAVE1_YYYYMMDD_HHMM
- DRYRUN_WAVE1B_YYYYMMDD_HHMM

Persist batch_id in all staging, conformed, load, rejection, and report records.

## 6. Detailed Execution Steps
### Step 1: Create empty dry-run database
From a privileged PostgreSQL account, create the database:

    CREATE DATABASE cras_dryrun;

Optional hardening:
- Restrict create/drop rights for non-admin users
- Grant only required DML and DDL rights to import role

### Step 2: Point application tooling to dry-run DB
Set environment values so the isolated dry-run tooling targets cras_dryrun:
- PG_HOST = existing PostgreSQL host
- PG_PORT = existing PostgreSQL port
- PG_USER = import-capable user
- PG_PASSWORD = user password
- PG_DB = cras_dryrun

Mandatory check:
- Print resolved connection target before running any migration/import step

### Step 3: Apply schema to head
Run the dry-run schema bootstrap for the dry-run database.

Acceptance:
- Schema bootstrap completes without error
- Expected dry-run support objects exist in `cras_dryrun`

### Step 4: Register batch and preflight
- Create one new import batch record
- Validate required source files exist
- Validate required columns are present
- Validate parser contracts for dates and numeric fields
- Validate identity-linkage prerequisites are readable

Hard fail conditions:
- Missing required file
- Missing required column
- Unparseable mandatory field above allowed threshold

### Step 5: Stage raw data
- Load each Wave 1 source file to raw staging tables with no destructive transformations
- Preserve original values and row number
- Store source hash for file version traceability

Acceptance:
- Row counts in staging match source file counts exactly

### Step 6: Conform and harmonize
- Normalize missing-value semantics
- Standardize date and category representations
- Build harmonized identity keys
- Emit explicit ambiguity records to queue

Hard fail condition:
- Any unresolved ambiguity record remains in queue

### Step 7: Production load order
Load in this order:
1. Study
2. Procedure
3. Subject
4. StudySubjectLink
5. Event

Rules:
- Upsert logic must be deterministic
- All records include source provenance metadata
- Subject creation must come from canonical identity map, not per-file free creation

### Step 8: Post-load validation
Run all integrity and consistency checks listed in Section 7.

Acceptance:
- All critical checks return zero violations

### Step 9: Reconciliation report
Create exact-match reconciliation output by source file and table target:
- Source rows
- Staged rows
- Conformed rows
- Loaded rows
- Rejected rows
- Ambiguous rows

Acceptance:
- Exact match where expected
- Every non-loaded row accounted for as rejected or ambiguous

### Step 10: Idempotency rerun
- Rerun the same batch inputs without changes
- Compare row deltas after rerun

Acceptance:
- No duplicate Study, Procedure, Subject, StudySubjectLink, Event rows
- No drift in reconciled totals
- Deterministic no-op behavior for already loaded records

### Step 11: Wave 1B Execution
- Start Wave 1B only after Wave 1 passes all hard gates
- Apply the same stage, conform, load, validate, reconcile, and idempotency pattern
- Repeat Steps 5 through 10 for Wave 1B source files and Wave 1B batch ID
- Create `Study` rows at one-study-per-folder granularity:
    - FEP
    - TRS_GRF
    - TRS_VS
    - TRS_CLOZ_DOSAGE
- Enforce masterlist-as-identity-only policy unless explicitly overridden in mapping spec
- Enforce dedicated medication procedure families for medication workbooks

### Step 12: Sign-off Decision
Review:
- Validation results
- Reconciliation outputs
- Ambiguity queue status
- Idempotency rerun results for both Wave 1 and Wave 1B

Decision outcomes:
- Approve production preparation
- Reject and return to remediation

## 7. Validation Query Pack
Run these queries after Step 8 and Step 10 for each wave (Wave 1 and Wave 1B).

### 7.1 FK orphan checks
Event rows with missing parent links:

    SELECT COUNT(*) AS orphan_events
    FROM event e
    LEFT JOIN study s ON s.id = e.study_id
    LEFT JOIN subject su ON su.id = e.subject_id
    LEFT JOIN procedure p ON p.id = e.procedure_id
    WHERE s.id IS NULL OR su.id IS NULL OR p.id IS NULL;

StudySubjectLink rows with missing parent links:

    SELECT COUNT(*) AS orphan_study_subject_links
    FROM studysubjectlink l
    LEFT JOIN study s ON s.id = l.study_id
    LEFT JOIN subject su ON su.id = l.subject_id
    WHERE s.id IS NULL OR su.id IS NULL;

Expected result: 0 for both.

### 7.2 Cross-consistency checks
Event study must match procedure study:

    SELECT COUNT(*) AS mismatched_event_procedure_study
    FROM event e
    JOIN procedure p ON p.id = e.procedure_id
    WHERE e.study_id <> p.study_id;

Expected result: 0.

Event subject must be enrolled in event study:

    SELECT COUNT(*) AS unenrolled_event_subjects
    FROM event e
    LEFT JOIN studysubjectlink l
      ON l.study_id = e.study_id
     AND l.subject_id = e.subject_id
    WHERE l.subject_id IS NULL;

Expected result: 0.

### 7.3 Domain checks
Invalid status values:

    SELECT COUNT(*) AS invalid_event_status
    FROM event
    WHERE status NOT IN ('pending','completed','cancelled','no_show');

Invalid datetime ordering:

    SELECT COUNT(*) AS invalid_event_time_order
    FROM event
    WHERE end_datetime IS NOT NULL
      AND end_datetime < start_datetime;

Expected result: 0 for both.

### 7.4 Duplicate risk checks
Duplicate StudySubjectLink keys:

    SELECT study_id, subject_id, COUNT(*) AS n
    FROM studysubjectlink
    GROUP BY study_id, subject_id
    HAVING COUNT(*) > 1;

Expected result: no rows.

Candidate duplicate Event rows (natural key baseline):

    SELECT study_id, subject_id, procedure_id, start_datetime, COUNT(*) AS n
    FROM event
    GROUP BY study_id, subject_id, procedure_id, start_datetime
    HAVING COUNT(*) > 1;

Expected result: no rows unless explicitly justified and documented.

## 8. Exact-Match Reconciliation Standard
For each source file and each target stage:
- source_count must equal staged_count
- conformed_count must equal staged_count minus conformed_reject_count
- loaded_count must equal conformed_count minus load_reject_count minus ambiguity_count

No silent row loss is permitted.

Any mismatch without explicit rejection or ambiguity attribution is a hard failure.

## 9. Hard Gates (Go/No-Go)
Production promotion is blocked if any of the following is true:
- Any unresolved ambiguity remains
- Any critical integrity query fails
- Any exact-match reconciliation check fails
- Idempotency rerun creates new duplicates
- Dry-run schema bootstrap state differs from expected project definition

## 10. Deliverables from Rehearsal
Required artifacts:
- Rehearsal batch manifest
- Validation query output log
- Reconciliation report by file and table
- Ambiguity queue export
- Rejection log export
- Idempotency rerun comparison report
- Separate Wave 1 and Wave 1B validation/reconciliation packs
- Final sign-off note

## 11. Wave 1B Ingest Summary
1. Run Wave 1 batch end to end and pass all gates.
2. Start Wave 1B batch with identity/masterlist staging only.
3. Build canonical matches to existing `Subject` map; route any uncertainty to ambiguity queue.
4. Load clinical datasets by folder stream with one `Study` per folder.
5. Load medication workbooks to dedicated medication procedures.
6. Validate integrity and exact-match reconciliation.
7. Re-run same Wave 1B batch unchanged to verify idempotency.
8. Prepare combined promotion packet for your approval.

## 12. Immediate Next Actions
1. Scaffold the isolated `dryrun_import` project and schema bootstrap scripts.
2. Implement the dry-run support tables defined in Section 5.2 for `cras_dryrun` only.
3. Build and validate preflight checks.
4. Implement validation and reconciliation query runner.
5. Execute first dry-run batch on cras_dryrun.
