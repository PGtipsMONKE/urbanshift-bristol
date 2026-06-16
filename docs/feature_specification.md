# UrbanShift Churn Model Feature Specification

Version: 2.4
Status: ???

## Purpose

This document defines the complete feature engineering process used to generate the UrbanShift customer churn modelling dataset.

The objective of the model is:

> Identify B2B customers showing early signs of reducing their business with UrbanShift and predict this behaviour approximately 60 days in advance.

This document provides:

* Dataset grain
* Snapshot methodology
* Feature definitions
* Intermediate calculations
* Target definition
* Leakage controls
* Final export schema

This document describes business logic and calculation rules rather than implementation details.

---

# Dataset Grain

## Final Dataset Grain

One row represents:

**(Customer, Snapshot Date)**

Example:

| customer_id | snapshot_date |
| ----------- | ------------- |
| CUST001     | 2025-03-31    |
| CUST001     | 2025-04-30    |
| CUST001     | 2025-05-31    |

A customer may appear multiple times at different snapshot dates.

This design enables churn prediction across time while preserving a tabular dataset structure.

---

# Snapshot Configuration

| Parameter                  | Value         |
| -------------------------- | ------------- |
| Snapshot Frequency         | Monthly       |
| Snapshot Date              | Month End     |
| Historical Lookback Window | 60 Days       |
| Prediction Horizon         | 60 Days       |
| Minimum Activity Threshold | 10 Deliveries |

---

## Historical Window

The historical window contains all activity occurring during the 60 days immediately preceding the snapshot date.

Example:

| Snapshot Date | Historical Window        |
| ------------- | ------------------------ |
| 2025-04-30    | 2025-03-01 to 2025-04-30 |

---

## Prediction Window

The prediction window contains all activity occurring during the 60 days immediately following the snapshot date.

Example:

| Snapshot Date | Prediction Window        |
| ------------- | ------------------------ |
| 2025-04-30    | 2025-05-01 to 2025-06-30 |

---

# Source Datasets

| Dataset    | Purpose                          |
| ---------- | -------------------------------- |
| Customers  | Customer attributes              |
| Deliveries | Operational activity and revenue |
| Incidents  | Service quality metrics          |
| Couriers   | Data quality validation only     |

---

# Historical Activity Features

Generated using activity within the historical lookback window.

---

## deliveries_lookback_60d

### Description

Total deliveries completed during the historical window.

### Calculation

Count of deliveries.

### Feature Type

Behaviour

### Exported

No

---

## revenue_lookback_60d

### Description

Total revenue generated during the historical window.

### Calculation

Sum of delivery revenue.

### Feature Type

Commercial

### Exported

No

---

## delivered_deliveries_lookback_60d

### Description

Number of successfully delivered shipments.

### Calculation

Count of deliveries with Delivered status.

### Feature Type

Operational

### Exported

No

---

## failed_deliveries_lookback_60d

### Description

Number of failed deliveries.

### Calculation

Count of deliveries with Failed status.

### Feature Type

Operational

### Exported

No

---

## returned_deliveries_lookback_60d

### Description

Number of returned deliveries.

### Calculation

Count of deliveries with Returned status.

### Feature Type

Operational

### Exported

No

---

## avg_delivery_time_lookback_60d

### Description

Average delivery duration during the historical window.

### Calculation

Average delivery time.

### Feature Type

Service Quality

### Exported

Yes

---

# Historical Incident Features

Only incidents linked to valid deliveries are included.

---

## incident_count_lookback_60d

Count of incidents.

Exported: No

---

## complaint_count_lookback_60d

Count of customer complaints.

Exported: No

---

## late_delivery_count_lookback_60d

Count of late delivery incidents.

Exported: No

---

## damaged_parcel_count_lookback_60d

Count of damaged parcel incidents.

Exported: No

---

## lost_parcel_count_lookback_60d

Count of lost parcel incidents.

Exported: No

---

# Customer Profile Features

---

## customer_size

Customer size classification.

Exported: Yes

---

## city

Customer operating city.

Exported: Yes

---

## industry

Customer industry classification.

Exported: Yes

---

## payment_terms_days

Contractual payment period.

Exported: Yes

---

## customer_tenure_days

### Description

Length of customer relationship.

### Calculation

Days between customer signup date and snapshot date.

### Exported

Yes

---

# Service Quality Features

All rates use delivery volume as the denominator.

---

## failed_delivery_rate_lookback_60d

Failed deliveries divided by total deliveries.

Exported: Yes

---

## return_rate_lookback_60d

Returned deliveries divided by total deliveries.

Exported: Yes

---

## success_rate_lookback_60d

Successful deliveries divided by total deliveries.

Exported: No

Reason:

Redundant with retained failure-based metrics.

---

## incident_rate_lookback_60d

Incidents divided by total deliveries.

Exported: Yes

---

## complaint_rate_lookback_60d

Complaints divided by total deliveries.

Exported: Yes

---

## late_delivery_rate_lookback_60d

Late deliveries divided by total deliveries.

Exported: Yes

---

## damaged_parcel_rate_lookback_60d

Damaged parcel incidents divided by total deliveries.

Exported: Yes

---

## lost_parcel_rate_lookback_60d

Lost parcel incidents divided by total deliveries.

Exported: Yes

---

# Revenue Efficiency Features

## avg_revenue_per_delivery_lookback_60d

### Description

Average revenue generated per delivery.

### Calculation

Revenue divided by delivery volume.

### Feature Type

Commercial

### Exported

Yes

---

# Trend Features

The 60-day lookback period is divided into:

* Previous 30 Days
* Latest 30 Days

---

## deliveries_prev_30d

Delivery volume during previous period.

Exported: No

---

## deliveries_latest_30d

Delivery volume during latest period.

Exported: No

---

## revenue_prev_30d

Revenue during previous period.

Exported: No

---

## revenue_latest_30d

Revenue during latest period.

Exported: No

---

## volume_growth_lookback

### Description

Recent delivery growth or decline.

### Calculation

Change between latest and previous delivery periods.

### Exported

Yes

---

# Market Context Features

---

## median_deliveries_60d

Median customer delivery volume at the same snapshot date.

Exported: No

---

## median_revenue_60d

Median customer revenue at the same snapshot date.

Exported: No

---

## relative_volume_strength

### Description

Customer delivery volume relative to peers.

### Calculation

Customer delivery volume divided by median customer delivery volume.

### Exported

Yes

---

## market_volume_growth_lookback

### Description

Overall market delivery growth.

### Exported

No

---

## market_revenue_growth_lookback

### Description

Overall market revenue growth.

### Exported

No

---

## industry_revenue_share

### Description

Industry revenue as a proportion of total UrbanShift revenue.

### Exported

Yes

---

## industry_relative_revenue_strength

### Description

Industry performance relative to wider market performance.

### Calculation

Industry growth minus market growth.

### Exported

Yes

---

## relative_revenue_strength

### Description

Customer revenue relative to peer revenue.

### Exported

No

Reason:

Removed following feature review due to overlap with retained metrics.

---

## revenue_growth_lookback

### Description

Recent revenue growth or decline.

### Exported

No

Reason:

Lower incremental value than retained volume-based metrics.

---

## relative_revenue_growth_lookback

### Description

Revenue growth relative to market growth.

### Exported

No

Reason:

Removed following multicollinearity assessment.

---

# Intermediate Pipeline Features

These variables are required during feature engineering but are not included in the final modelling dataset.

| Feature                           |
| --------------------------------- |
| deliveries_lookback_60d           |
| revenue_lookback_60d              |
| delivered_deliveries_lookback_60d |
| failed_deliveries_lookback_60d    |
| returned_deliveries_lookback_60d  |
| incident_count_lookback_60d       |
| complaint_count_lookback_60d      |
| late_delivery_count_lookback_60d  |
| damaged_parcel_count_lookback_60d |
| lost_parcel_count_lookback_60d    |
| deliveries_prev_30d               |
| deliveries_latest_30d             |
| revenue_prev_30d                  |
| revenue_latest_30d                |
| median_deliveries_60d             |
| median_revenue_60d                |
| market_volume_growth_lookback     |
| market_revenue_growth_lookback    |
| eligible_for_training             |

---

# Target Definition

## at_risk

### Description

Customer decline materially exceeds broader market decline during the prediction horizon.

### Business Meaning

The customer is reducing business with UrbanShift faster than expected given prevailing market conditions.

### Exported

Yes

### Target Variable

Yes

---

# Label Generation Features

These features are required to generate the target but must never be used as predictors.

---

## deliveries_future_60d

Future delivery volume.

---

## revenue_future_60d

Future revenue.

---

## delivery_volume_decline_pct

Future delivery decline percentage.

---

## revenue_decline_pct

Future revenue decline percentage.

---

## market_volume_decline_pct

Future market delivery decline percentage.

---

## market_revenue_decline_pct

Future market revenue decline percentage.

---

## relative_volume_decline_pct

Customer decline relative to market decline.

---

## relative_revenue_decline_pct

Revenue decline relative to market decline.

---

# Leakage Controls

The following features must never be available during model training:

* deliveries_future_60d
* revenue_future_60d
* delivery_volume_decline_pct
* revenue_decline_pct
* market_volume_decline_pct
* market_revenue_decline_pct
* relative_volume_decline_pct
* relative_revenue_decline_pct

These variables use information from the future prediction window and are used exclusively for target generation.

---

# Final Export Schema

## Traceability Fields

* customer_id
* snapshot_date

## Predictor Fields

* customer_size
* city
* industry
* industry_revenue_share
* industry_relative_revenue_strength
* payment_terms_days
* customer_tenure_days
* avg_revenue_per_delivery_lookback_60d
* relative_volume_strength
* volume_growth_lookback
* relative_volume_growth_lookback
* failed_delivery_rate_lookback_60d
* return_rate_lookback_60d
* avg_delivery_time_lookback_60d
* incident_rate_lookback_60d
* complaint_rate_lookback_60d
* late_delivery_rate_lookback_60d
* damaged_parcel_rate_lookback_60d
* lost_parcel_rate_lookback_60d

## Target

* at_risk

---

# Relationship to Other Governance Documents

This document should be read alongside:

| Document                  | Purpose                               |
| ------------------------- | ------------------------------------- |
| Data Cleaning Register    | Why the source data changed           |
| Feature Specification     | How modelling features are calculated |
| Feature Decision Register | Why features were retained or removed |

Together these documents provide a complete audit trail from raw data to final churn model dataset.
