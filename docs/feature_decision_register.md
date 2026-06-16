# UrbanShift Churn Model Feature Decision Register

Version: 2.1 (Final)
Status: Approved for Modelling and AWS Migration

## Purpose

This document records every feature considered during churn model development, the rationale for inclusion or exclusion, and the supporting evidence.

The objective of the model is:

> Identify B2B customers showing early signs of reducing their business with UrbanShift and predict this behaviour approximately 60 days in advance.

Feature decisions were evaluated against four criteria:

1. Business relevance
2. Leakage risk
3. Statistical usefulness
4. Model interpretability

---

# Decision Categories

| Category                  | Definition                                                     |
| ------------------------- | -------------------------------------------------------------- |
| Kept                      | Included in final modelling dataset and available for training |
| Retained for Traceability | Present in exported dataset but excluded from predictor set    |
| Excluded – Leakage        | Uses future information unavailable at prediction time         |
| Excluded – Redundant      | Similar signal already captured by a stronger retained feature |
| Excluded – Business Scope | Does not directly describe customer behaviour                  |
| Excluded – Governance     | Identifier, metadata, or modelling artefact                    |

---

# Retained Features

## Customer Context Features

| Feature              | Status | Business Rationale                                                                                            | Evidence                                            |
| -------------------- | ------ | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| customer_size        | Kept   | Larger customers often exhibit different ordering patterns, retention profiles, and operational requirements. | Commercially meaningful segmentation variable.      |
| city                 | Kept   | Geography may influence delivery performance, customer expectations, and operational reliability.             | Known operational variation by region.              |
| industry             | Kept   | Customer industries exhibit different demand patterns and seasonality.                                        | Strong business relevance.                          |
| payment_terms_days   | Kept   | Captures commercial relationship structure and purchasing behaviour.                                          | Potential indicator of customer maturity and value. |
| customer_tenure_days | Kept   | Long-standing customers may behave differently from recently acquired customers.                              | Widely used retention feature.                      |

---

## Industry Context Features

| Feature                            | Status | Business Rationale                                                                                        | Evidence                                                                |
| ---------------------------------- | ------ | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| industry_revenue_share             | Kept   | Measures the relative importance of the customer's industry within UrbanShift's portfolio.                | Provides market context unavailable from customer-level metrics alone.  |
| industry_relative_revenue_strength | Kept   | Measures whether the customer's industry is outperforming or underperforming the wider UrbanShift market. | Helps distinguish customer-specific decline from industry-wide decline. |

**Decision Note**

Although industry information appears in multiple forms (`industry`, `industry_revenue_share`, `industry_relative_revenue_strength`), each serves a different purpose:

* `industry` identifies customer segment.
* `industry_revenue_share` measures industry scale.
* `industry_relative_revenue_strength` measures industry performance.

The features were therefore retained as complementary rather than redundant.

---

## Customer Behaviour Features

| Feature                               | Status | Business Rationale                                                      | Evidence                                                                          |
| ------------------------------------- | ------ | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| avg_revenue_per_delivery_lookback_60d | Kept   | Measures customer value beyond shipment volume.                         | Complements volume-based metrics.                                                 |
| relative_volume_strength              | Kept   | Measures customer activity relative to peers at the same point in time. | More informative than raw delivery counts.                                        |
| volume_growth_lookback                | Kept   | Captures short-term behavioural change prior to prediction.             | Direct indicator of customer engagement trend.                                    |
| relative_volume_growth_lookback       | Kept   | Measures customer growth or decline relative to wider market movement.  | Closely aligned with business objective. Retained after multicollinearity review. |

---

## Service Quality Features

| Feature                           | Status | Business Rationale                                      | Evidence                            |
| --------------------------------- | ------ | ------------------------------------------------------- | ----------------------------------- |
| failed_delivery_rate_lookback_60d | Kept   | Delivery failures may damage customer satisfaction.     | Strong operational relevance.       |
| return_rate_lookback_60d          | Kept   | High return levels may indicate service quality issues. | Customer experience metric.         |
| avg_delivery_time_lookback_60d    | Kept   | Slow deliveries may contribute to dissatisfaction.      | Operational performance indicator.  |
| incident_rate_lookback_60d        | Kept   | Measures overall operational friction.                  | Scaled by customer size.            |
| complaint_rate_lookback_60d       | Kept   | Direct signal of customer dissatisfaction.              | Strong behavioural interpretation.  |
| late_delivery_rate_lookback_60d   | Kept   | Reliability indicator.                                  | Directly linked to service quality. |
| damaged_parcel_rate_lookback_60d  | Kept   | Reflects fulfilment quality.                            | Potential churn driver.             |
| lost_parcel_rate_lookback_60d     | Kept   | Severe service failure indicator.                       | High business significance.         |

---

# Retained for Traceability

| Feature       | Status                    | Reason                                                                                                                               |
| ------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| customer_id   | Retained for Traceability | Required for watchlists, customer identification, reporting, and auditability. Explicitly excluded from model training.              |
| snapshot_date | Retained for Traceability | Required for temporal auditability, model monitoring, performance tracking, and governance. Explicitly excluded from model training. |

---

# Target Variable

| Feature | Status | Reason                                                                                                                            |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------- |
| at_risk | Target | Final binary target representing customers whose decline materially exceeds broader market decline during the prediction horizon. |

---

# Excluded Features – Leakage

These features use information from the future prediction window and therefore cannot be available at prediction time.

| Feature                      | Reason                          |
| ---------------------------- | ------------------------------- |
| deliveries_future_60d        | Future information.             |
| revenue_future_60d           | Future information.             |
| delivery_volume_decline_pct  | Derived from future behaviour.  |
| revenue_decline_pct          | Derived from future behaviour.  |
| market_volume_decline_pct    | Uses future market activity.    |
| market_revenue_decline_pct   | Uses future market activity.    |
| relative_volume_decline_pct  | Used to construct target label. |
| relative_revenue_decline_pct | Used to construct target label. |

---

# Excluded Features – Redundant

Removed because the same information was captured more effectively elsewhere.

| Feature                          | Reason                                                                                                                                   | Evidence                                               |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| deliveries_lookback_60d          | Raw volume already represented through relative measures.                                                                                | Relative metrics improve comparability.                |
| revenue_lookback_60d             | Revenue already represented through efficiency and contextual measures.                                                                  | Reduces duplication.                                   |
| revenue_growth_lookback          | Revenue trend information became unnecessary once the model retained volume-based trend features and market-relative behaviour measures. | Lower incremental value and increased feature overlap. |
| relative_revenue_growth_lookback | Highly collinear with `relative_volume_growth_lookback`.                                                                                 | Removed following multicollinearity assessment.        |
| relative_revenue_strength        | Similar signal captured by retained volume-based strength metrics.                                                                       | Reduced overlap.                                       |
| success_rate_lookback_60d        | Inverse of failure-based metrics already retained.                                                                                       | Redundant information.                                 |
| incident_count_lookback_60d      | Incident rate captures the same signal while controlling for customer size.                                                              | Rate preferred over count.                             |

---

# Excluded Features – Business Scope

Removed because they do not describe customer behaviour.

| Feature         | Reason                                                                                                                                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| account_manager | Internal UrbanShift assignment variable. No plausible causal relationship with a customer's decision to increase or reduce shipping volume. The modelling objective is customer behaviour, not organisational behaviour. |

---

# Excluded Features – Governance

Removed because they are identifiers, modelling artefacts, or superseded development concepts.

| Feature               | Reason                                                                                                                                                                                                                                                                              |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| customer_name         | Identifier only.                                                                                                                                                                                                                                                                    |
| eligible_for_training | Dataset construction flag used during label generation.                                                                                                                                                                                                                             |
| critical_risk         | Experimental monitoring/escalation label created during development. Not used for model training, evaluation, or deployment.                                                                                                                                                        |
| at_risk_absolute      | Experimental target used during target-design evaluation. Removed after adopting a market-relative churn definition. Absolute decline was considered less aligned with the business objective because it cannot distinguish customer-specific decline from market-wide contraction. |

---

# Feature Selection Principles

The final feature set follows seven principles:

1. Use only information available before the prediction date.
2. Prefer customer behaviour over internal operational metadata.
3. Prefer rates over raw counts.
4. Prefer relative measures over absolute measures.
5. Remove highly collinear features.
6. Separate customer decline from market-wide decline.
7. Preserve business interpretability.

---

# Final Predictor Set

### Customer Context

* customer_size
* city
* industry
* payment_terms_days
* customer_tenure_days

### Industry Context

* industry_revenue_share
* industry_relative_revenue_strength

### Customer Behaviour

* avg_revenue_per_delivery_lookback_60d
* relative_volume_strength
* volume_growth_lookback
* relative_volume_growth_lookback

### Service Quality

* failed_delivery_rate_lookback_60d
* return_rate_lookback_60d
* avg_delivery_time_lookback_60d
* incident_rate_lookback_60d
* complaint_rate_lookback_60d
* late_delivery_rate_lookback_60d
* damaged_parcel_rate_lookback_60d
* lost_parcel_rate_lookback_60d

### Target

* at_risk

---

# Final Model Philosophy

The final model prioritises behavioural change over absolute activity, focuses on customer-specific decline rather than market-wide contraction, removes leakage-prone information, and retains only features that are interpretable, actionable, and available at prediction time.

---

# Relationship to Other Governance Documents

This document should be read alongside:

| Document                  | Purpose                               |
| ------------------------- | ------------------------------------- |
| Data Cleaning Register    | Why the source data changed           |
| Feature Specification     | How modelling features are calculated |
| Feature Decision Register | Why features were retained or removed |

Together these documents provide a complete audit trail from raw data to final churn model dataset.
