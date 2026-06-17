# UrbanShift Churn Model Summary

Version: 1.0
Status: Final

---

# 1. Model Objective

The objective of this model is to identify B2B customers showing early signs of reducing their business with UrbanShift and predict this behaviour approximately 60 days in advance.

The model is intended to support proactive customer retention efforts by identifying accounts exhibiting behavioural patterns associated with future decline.

---

# 2. Modelling Dataset

## Dataset Grain

One row represents:

**(Customer, Snapshot Date)**

A customer may appear multiple times across different monthly snapshots.

## Configuration

| Parameter                  | Value   |
| -------------------------- | ------- |
| Snapshot Frequency         | Monthly |
| Historical Lookback Window | 60 Days |
| Prediction Horizon         | 60 Days |
| Target Variable            | at_risk |

## Dataset Size

| Metric           | Value |
| ---------------- | ----- |
| Development Rows | 606   |
| Test Rows        | 108   |
| Predictor Count  | 29    |

The modelling dataset was generated using the feature engineering process documented in the Feature Specification and Feature Decision Register.

---

# 3. Target Definition

## at_risk

The target variable identifies customers whose future delivery decline materially exceeds wider market decline during the prediction horizon.

### Business Interpretation

A customer is considered at risk when their reduction in delivery activity is significantly worse than expected given broader market conditions.

This market-relative approach was chosen to distinguish customer-specific deterioration from market-wide contraction.

---

# 4. Model Selection

## Model Type

XGBoost Classifier

## Selection Metric

ROC-AUC

## Training Approach

* Randomized Search Cross Validation
* 50 hyperparameter search iterations
* 5-fold cross-validation
* Class weighting applied to address imbalance

### Class Weighting

scale_pos_weight = 10.43

This weighting was introduced because at-risk customers represented a minority class within the dataset.

---

# 5. Model Performance

## Cross-Validation Performance

| Metric                        | Value |
| ----------------------------- | ----- |
| Best Cross-Validation ROC-AUC | 0.946 |

## Test Set Performance (Selected Threshold = 0.70)

| Metric    | Value |
| --------- | ----- |
| ROC-AUC   | 0.955 |
| PR-AUC    | 0.743 |
| Accuracy  | 0.926 |
| Precision | 0.533 |
| Recall    | 0.889 |
| F1 Score  | 0.667 |

## Interpretation

The model demonstrates strong discriminatory power, achieving a ROC-AUC of 0.955 on unseen test data.

Recall was prioritised over precision because the business objective is early identification of potentially declining customers. Missing a genuinely at-risk customer is considered more costly than investigating a false positive.

---

# 6. Threshold Selection

The default classification threshold of 0.50 was reviewed against alternative operating points.

The final threshold was set to:

**0.70**

### Reason

The threshold of 0.70 improved precision while maintaining strong recall.

| Threshold | Precision | Recall | F1    |
| --------- | --------- | ------ | ----- |
| 0.50      | 0.564     | 0.830  | 0.672 |
| 0.70      | 0.712     | 0.698  | 0.705 |

The selected threshold provided the strongest balance between identifying genuine risk and limiting false positives during model development.

---

# 7. Feature Importance

The model found that recent changes in customer delivery behaviour were more predictive of future churn than static customer characteristics such as industry, location, or payment terms. Customers exhibiting declining delivery activity were significantly more likely to become at risk in the prediction window.

## Top Predictors

| Feature                               | Importance |
| ------------------------------------- | ---------- |
| relative_volume_growth_lookback       | 0.227      |
| volume_growth_lookback                | 0.136      |
| city_London                           | 0.067      |
| relative_volume_strength              | 0.050      |
| city_Leeds                            | 0.050      |
| industry_revenue_share                | 0.045      |
| avg_delivery_time_lookback_60d        | 0.043      |
| avg_revenue_per_delivery_lookback_60d | 0.043      |
| customer_tenure_days                  | 0.042      |
| failed_delivery_rate_lookback_60d     | 0.034      |

## Business Interpretation

### Relative Volume Growth

Customers whose delivery volume is declining relative to wider market activity are significantly more likely to become at risk.

### Volume Growth

Recent changes in delivery activity are strong indicators of future customer behaviour.

### Relative Volume Strength

Customers operating below the activity levels of comparable customers are more likely to exhibit future decline.

### Industry Context

Industry-level performance contributes important context by distinguishing customer-specific deterioration from broader sector trends.

### Service Quality Metrics

Delivery failures, longer delivery times, and operational incidents appear to contribute to elevated churn risk.

### Location, Location, Location

Customer location contributed meaningful predictive signal, with London and Leeds emerging as influential variables. This may reflect differences in customer composition, local market conditions, operational performance, or industry concentration. Further investigation would be required to determine whether these relationships represent stable business effects or patterns specific to the available observation period. Therefore, the buisness importance of these features is diminished compared to others at the same correlational level.

---

# 8. Model Limitations

The model should be interpreted as a risk identification tool rather than a definitive predictor of customer attrition.

Key limitations include:

## Limited Historical Coverage

The available dataset covers approximately nine months of operational history. Longer historical periods would provide more complete seasonal coverage.

## Missing Courier Assignments

A proportion of deliveries were missing courier attribution due to subcontractor activity. Operational performance measures may therefore be understated in some cases.

## Unmatched Incident Records

Some incidents could not be linked to valid deliveries and were excluded from downstream service-quality calculations.

## Behavioural Proxy Target

The model predicts future behavioural decline rather than confirmed customer cancellation. The target therefore represents elevated risk rather than guaranteed churn.

## Correlation vs Causation

Feature importance identifies variables associated with churn risk but does not prove causal relationships.

---

# 9. Churn Watchlist Generation

Following model validation, the trained model was applied to the latest available customer snapshots.

Each customer received:

* Churn probability score
* Risk classification
* Relative ranking

The resulting output was exported as:

`churn_watchlist.csv`

This watchlist provides a ranked view of customers most likely to reduce business activity within the next 60 days.

---

# 10. Recommended Use

The model should be used as a decision-support tool for account managers and operational leadership.

Recommended actions include:

* Prioritising high-risk customers for account review.
* Investigating customers exhibiting declining relative delivery activity.
* Monitoring customers with elevated operational incident rates.
* Combining model outputs with commercial knowledge before intervention.

The model is intended to support proactive retention activity and should not be used as the sole basis for customer management decisions.

---

# Relationship to Other Governance Documents

This document should be read alongside:

| Document                  | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| Data Cleaning Register    | Source data quality decisions             |
| Feature Specification     | Feature engineering definitions           |
| Feature Decision Register | Feature inclusion and exclusion rationale |
| Churn Watchlist           | Operational model output                  |

Together these documents provide a complete audit trail from raw source data through feature engineering, model development, and operational scoring.
