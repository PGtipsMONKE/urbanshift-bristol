# UrbanShift Data Cleaning Register

Version: 1.1
Status: ???

## Purpose

This document records all data quality issues identified during the UrbanShift customer churn project, the remediation actions taken, and the rationale for those actions.

The objective is to ensure the data preparation process is:

* Reproducible
* Auditable
* Explainable
* Platform-independent
* Suitable for future AWS deployment

This document describes business rules rather than implementation details.

---

# Cleaning Decision Categories

| Category               | Definition                                |
| ---------------------- | ----------------------------------------- |
| Standardisation        | Values reformatted for consistency        |
| Deduplication          | Duplicate records removed                 |
| Missing Value Handling | Missing values treated or replaced        |
| Validation             | Data checked against business rules       |
| Flagging               | Issue retained but explicitly identified  |
| No Action Required     | Issue reviewed and intentionally retained |

---

# Source Datasets

The cleaning process was applied to the following source datasets:

| Dataset    | Purpose                      |
| ---------- | ---------------------------- |
| Customers  | Customer information         |
| Couriers   | Courier information          |
| Deliveries | Delivery transaction records |
| Incidents  | Delivery incident records    |

---

# Cleaning Decisions

## DC-001 City Name Standardisation

### Datasets

* Customers
* Couriers
* Deliveries

### Issue

City values contained inconsistent formatting.

Examples:

* london
* LONDON
* London

### Action

City names were standardised to a consistent format.

Leading and trailing whitespace was removed and values were converted to title case.

Examples:

* london → London
* LONDON → London

### Category

Standardisation

### Rationale

Prevents fragmentation during grouping, aggregation, reporting, and feature generation.

### Impact

No records removed.

---

## DC-002 Date Standardisation

### Datasets

* Customers
* Couriers
* Deliveries
* Incidents

### Issue

Date fields contained multiple formats.

Examples:

* 2025-01-31
* 31/01/2025

### Action

All date values were converted into a single standard date format.

### Standard Format

YYYY-MM-DD

### Category

Standardisation

### Rationale

Required for reliable time-window calculations, temporal analysis, and feature engineering.

### Impact

No records removed.

---

## DC-003 Duplicate Delivery Removal

### Dataset

Deliveries

### Issue

Duplicate delivery records were identified.

### Action

Delivery records were evaluated using delivery_id as the business key.

Where multiple records shared the same delivery_id, one valid record was retained and duplicate occurrences were removed.

### Category

Deduplication

### Rationale

Duplicate deliveries artificially inflate:

* Delivery volume
* Revenue
* Customer activity metrics
* Service quality metrics

### Impact

Duplicate records removed.

---

## DC-004 Missing Courier Assignment Handling

### Dataset

Deliveries

### Issue

Some delivery records contained missing courier assignments.

### Action

Missing courier assignments were replaced with a standard placeholder value.

### Replacement Value

SUBCONTRACTOR_UNKNOWN

### Category

Missing Value Handling

### Rationale

The delivery itself remained valid even though courier attribution was unavailable.

Removing the records would have resulted in the loss of legitimate business activity.

The placeholder preserves operational activity while explicitly identifying uncertainty.

### Impact

No records removed.

---

## DC-005 Delivery Reference Validation

### Dataset

Incidents

### Issue

Some incident records referenced delivery identifiers that could not be matched to the deliveries dataset.

### Action

A validation flag was created to identify unmatched records.

### Validation Flag

is_unmatched_delivery_id

Values:

* 1 = Unmatched
* 0 = Matched

### Category

Flagging

### Rationale

No reliable correction could be determined.

Retaining the records preserves auditability while preventing unmatched incidents from influencing downstream service quality metrics.

### Impact

No records removed.

---

## DC-006 Customer Dataset Validation

### Dataset

Customers

### Validation Performed

Reviewed:

* Unique customer identifiers
* Expected schema
* Missing values
* Referential integrity

### Result

No remediation required.

### Category

No Action Required

### Rationale

No material data quality issues were identified.

---

## DC-007 Courier Dataset Validation

### Dataset

Couriers

### Validation Performed

Reviewed:

* Unique courier identifiers
* Expected schema
* Missing values
* Referential integrity

### Result

No remediation required.

### Category

No Action Required

### Rationale

No material data quality issues were identified.

---

# Data Quality Principles Applied

The following principles governed all cleaning decisions:

1. Preserve valid business activity wherever possible.
2. Prefer flagging over deletion when uncertainty exists.
3. Standardise values before analysis.
4. Remove only demonstrably invalid duplicate records.
5. Maintain a complete audit trail.
6. Avoid introducing artificial information.
7. Ensure reproducibility across implementation platforms.
8. Support future migration to AWS-based processing pipelines.

---

# Approved Outputs

???

---

# Relationship to Other Governance Documents

This document should be read alongside:

| Document                  | Purpose                               |
| ------------------------- | ------------------------------------- |
| Data Cleaning Register    | Why the source data changed           |
| Feature Specification     | How modelling features are calculated |
| Feature Decision Register | Why features were retained or removed |

Together these documents provide a complete audit trail from raw data to final churn model dataset.

