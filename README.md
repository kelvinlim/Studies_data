# Studies_data

Central workspace for longitudinal psychiatry research datasets, cross-study masterlists, and the linked application project (chan_cras) used for structured data management.

## Folder Overview

- 1400 sample/
  - Anchor cohort and follow-up streams.
  - Includes baseline and long-term follow-up datasets (hcs10, hcs20, TRS_12FU, crf_trs, 1400cdars).
- treatment_resistant_schizophrenia/
  - TRS-focused parallel projects (GRF TRS, VS, clozapine dosage).
- fep/
  - Additional first-episode psychosis project datasets.
- masterlist_linkage/
  - Crosswalk/linkage outputs (overall_masterlist_crosswalk*.csv).
- chan_cras/
  - Clinical research management application codebase (backend/frontend).

## Key Top-Level Files

- Overall_Masterlist.xlsx
  - Cross-cutting coordination/recruitment masterlist.
- Blood_masterlist.xlsx
  - Blood sample tracking masterlist.
- ImportPlan.md
  - Current plan for importing studies, subjects, procedures, and events into the database.

## Data Organization Conventions

- Study folders usually contain a local README.txt with the canonical context for that study stream.
- File names often encode timepoint or cohort identity (for example `hcs10`, `hcs20`, `12-year`, `25-year`).
- Masterlist files are typically coordination/logging assets; cleaned analysis files are usually marked with names like `cleaned`, `database`, or `.csv` derivatives.

## Recommended Workflow

1. Read the relevant study folder README.txt before interpreting or transforming data.
2. Use masterlist_linkage/ crosswalk outputs when reconciling subject identity across streams.
3. Preserve original source files and write transformed outputs as new files with clear suffixes.
4. Keep cohort labels and coding terms unchanged unless you are applying an explicitly documented harmonization rule.

## Data Dictionary Index

### Core Anchor Cohort

- [1400 sample/README.txt](1400%20sample/README.txt): Study background and stream definitions.
- [1400 sample/HCS3data.csv](1400%20sample/HCS3data.csv): Baseline 3-year cleaned case-note dataset.

### Follow-Up Streams from 1400 Sample

- HCS10 (10-year FES)
  - [1400 sample/hcs10/README.txt](1400%20sample/hcs10/README.txt)
  - [1400 sample/hcs10/Interview(209)_changeFrec.csv](1400%20sample/hcs10/Interview(209)_changeFrec.csv)
  - [1400 sample/hcs10/Data Entry_Med_combined_120724_update0726.csv](1400%20sample/hcs10/Data%20Entry_Med_combined_120724_update0726.csv)

- HCS20 (20-year FES/FEBAD/HC)
  - [1400 sample/hcs20/README.txt](1400%20sample/hcs20/README.txt)
  - [1400 sample/hcs20/qualitative_description_dataset.csv](1400%20sample/hcs20/qualitative_description_dataset.csv)

- TRS_12FU (12-year TRS vs non-TRS)
  - [1400 sample/TRS_12FU/README.txt](1400%20sample/TRS_12FU/README.txt)
  - [1400 sample/TRS_12FU/Full_1400_clozform_20220607.csv](1400%20sample/TRS_12FU/Full_1400_clozform_20220607.csv)

- CRF_TRS (25-year TRS follow-up + intervention)
  - [1400 sample/crf_trs/README.txt](1400%20sample/crf_trs/README.txt)

- CDARS stream
  - [1400 sample/1400cdars/README.txt](1400%20sample/1400cdars/README.txt)
  - [1400 sample/1400cdars/Ref.Keys_1400.csv](1400%20sample/1400cdars/Ref.Keys_1400.csv)
  - [1400 sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv](1400%20sample/1400cdars/cleaned_Rx_Antipsychotic202411.csv)
  - [1400 sample/1400cdars/monthly_DDD_updated.csv](1400%20sample/1400cdars/monthly_DDD_updated.csv)
  - [1400 sample/1400cdars/mortality20year.csv](1400%20sample/1400cdars/mortality20year.csv)

### Cross-Study Linkage and Masterlists

- Top-level masterlists
  - [Overall_Masterlist.xlsx](Overall_Masterlist.xlsx)
  - [Blood_masterlist.xlsx](Blood_masterlist.xlsx)

- Linkage outputs
  - [masterlist_linkage/overall_masterlist_crosswalk.csv](masterlist_linkage/overall_masterlist_crosswalk.csv)
  - [masterlist_linkage/overall_masterlist_crosswalk_summary.csv](masterlist_linkage/overall_masterlist_crosswalk_summary.csv)
  - [masterlist_linkage/overall_masterlist_crosswalk_ambiguous.csv](masterlist_linkage/overall_masterlist_crosswalk_ambiguous.csv)
  - [masterlist_linkage/overall_masterlist_crosswalk_unmatched.csv](masterlist_linkage/overall_masterlist_crosswalk_unmatched.csv)

### Parallel Project Areas

- TRS parallel projects: [treatment_resistant_schizophrenia](treatment_resistant_schizophrenia)
  - [treatment_resistant_schizophrenia/GRF TRS](treatment_resistant_schizophrenia/GRF%20TRS)
  - [treatment_resistant_schizophrenia/VS](treatment_resistant_schizophrenia/VS)
  - [treatment_resistant_schizophrenia/clozapine dosage](treatment_resistant_schizophrenia/clozapine%20dosage)

- Additional FEP data: [fep/Masterlist eye gaze_2.xlsx](fep/Masterlist%20eye%20gaze_2.xlsx)

### Application Project

- Import and schema implementation target app: [chan_cras](chan_cras)
- Current import strategy document: [ImportPlan.md](ImportPlan.md)

## Notes

- This workspace is dataset-centric and does not define a single global build/test pipeline.
- Application-specific development and migrations are managed inside chan_cras/.
