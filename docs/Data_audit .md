# **UrbanShift Couriers Data Audit Document**

# **1\. Executive Summary**

UrbanShift Couriers provided nine months of operational data across four CSV datasets representing customer, courier, delivery, and incident activity.

These datasets were supplied as flat file extracts and do not form part of a documented system architecture. No formal data model, governance framework, or upstream validation rules were provided with the data.

This audit identified five material data quality issues and three structural governance gaps that may affect the reliability of analytical outputs and reporting consistency.

Key issues observed include duplicate delivery records, likely resulting from data synchronisation issues during capture, and inconsistent date formatting within the incident dataset, where multiple formats (YYYY-MM-DD and DD/MM/YYYY) coexist within the same field.

If not addressed, these issues may reduce:  
Revenue and reporting accuracy  
Consistency of derived outputs  
Reliability of dataset-level insights

Overall, while the datasets are suitable for analysis following remediation, the current state presents a moderate to high risk of misinterpretation in downstream analytical outputs.

# **2\. Audit Scope and Methodology**

## **2.1 Scope**

The audit covered:

Data completeness  
Data accuracy  
Data consistency  
Referential integrity  
Metadata and governance maturity  
Downstream analytical impact

## **2.2 Methodology**

A structured data audit approach was applied:

Data profiling using AWS Glue DataBrew  
Root cause analysis through cross-table reconciliation  
Governance maturity assessment aligned to industry data management practices  
Risk scoring using a five-point severity scale  
End-to-end pipeline traceability review using AWS-based processing workflows

# **3\. Key Findings: Data Quality Issues**

## **3.1 Duplicate Delivery Records High Impact Risk**

**Source:** deliveries.csv  
**Affected records:** 1,962

**Observation**  
Duplicate delivery\_id values were identified, likely resulting from data synchronisation behaviour during capture.

**Risk Assessment**  
Inflation of recorded metrics  
Reduced reliability of aggregated outputs  
Distortion of dataset relationships  
Reduced integrity of joined datasets

**Downstream Impact**  
May result in overstated or inconsistent analytical outputs, reducing confidence in derived performance measures.

**Conclusion**  
High severity issue requiring remediation through deduplication and ingestion controls.

## **3.2 Missing Courier Assignments High Impact Risk**

**Source:** deliveries.csv  
**Affected records:** 4,004 (\~4%)

**Observation**  
Courier identifiers are missing for a subset of records, primarily associated with subcontracted fulfilment activity not captured in the dataset extract.

**Risk Assessment**  
Reduced completeness of entity-level attribution  
Bias in record-level comparisons  
Reduced consistency across grouped outputs

**Downstream Impact**  
May reduce completeness and accuracy of derived outputs where entity assignment is required, increasing risk of misrepresentation in analysis.

**Conclusion**  
High-severity structural data gap requiring explicit classification rules for third-party records.

## **3.3 Inconsistent City Naming Significant Risk**

**Source:** deliveries.csv

**Affected records:** \~14% of deliveries

**Observation**  
City values are inconsistently formatted, including case differences, whitespace variations, and naming inconsistencies.

**Risk Assessment**  
Reduced consistency in grouped outputs  
Fragmentation of categorical values  
Reduced comparability across datasets

**Conclusion**  
Requires standardisation and enforcement of controlled vocabulary across all datasets.

## **3.4 Mixed Date Formats Significant Risk**

**Source:** incidents.csv  
 **Column:** incident\_date  
 **Affected records:** All records potentially impacted

**Observation**  
Incident date values contain mixed formats, including ISO 8601 and DD/MM/YYYY within the same field.

**Risk Assessment**  
 Reduced consistency in temporal ordering  
 Increased risk of incorrect sequencing in outputs  
 Reduced reliability of time-based aggregation

**Conclusion**  
 Requires full standardisation to ISO 8601 format to ensure analytical consistency.

## **3.5 Invalid Foreign Key References Significant Risk**

**Source:** incidents.csv  
**Affected records:** 5

**Observation**  
A small number of records contain delivery\_id values that do not match expected patterns in the deliveries dataset.

**Risk Assessment**  
Reduced integrity of cross-dataset relationships  
Incomplete linkage between related records  
Reduced traceability across datasets

**Conclusion**  
Invalid records should be isolated or classified for monitoring and audit traceability.

# **4\. Governance and Structural Gaps**

## **4.1 Lack of Master Data Standards**

There is no consistent definition framework across the provided datasets for:

City naming conventions  
Employment classification  
Delivery status categories  
Incident classification

**Impact:** Reduced consistency across datasets and variability in derived outputs.

## **4.2 Absence of Referential Integrity Controls**

No constraints exist across the CSV datasets to enforce:

Unique delivery identifiers  
Valid courier relationships  
Customer delivery consistency

**Impact:** Increased reliance on manual reconciliation and reduced confidence in cross-dataset relationships.

## **4.3 Absence of Data Ownership Model**

There is no formal governance structure defining:

Data ownership  
Data stewardship  
Data quality accountability  
Issue escalation processes

**Impact:** Data issues may not be consistently managed or resolved in a structured manner.

# **5\. Data Processing and Remediation Approach**

All data processing and remediation were performed using an AWS-based analytical pipeline following receipt of the datasets. 

The workflow implemented was:

S3 (Raw Zone)  
→ AWS Glue DataBrew (profiling only)  
→ SageMaker Data Wrangler (transformations)  
→ S3 (curated zone)  
→ Amazon Redshift (analytics layer)

**Key remediation actions:**

Removal of 1,962 duplicate delivery records using delivery\_id deduplication logic  
Standardisation of missing courier assignments using “Third Party” classification  
City standardisation using trim and title case formatting  
Conversion of all timestamps to ISO 8601 format  
Removal and classification of invalid foreign key references in incident data

# **6\. Residual Risks and Caveats**

Following remediation, the following residual risks remain:

* Historical inconsistencies in source extracts cannot be fully reversed due to limitations in the original data capture process  
* Certain third-party courier activity is not fully captured within the dataset, limiting complete visibility of all delivery operations  
* Analytical outputs remain dependent on the completeness and quality of the underlying source data, particularly for time-based comparisons

# **7\. Recommendations**

## **7.1 Establish Data Governance Framework**

Define ownership across data domains  
Introduce stewardship responsibilities  
Implement data quality service level agreements

## **7.2 Implement Master Data Management**

Standardise controlled vocabularies across datasets  
Enforce consistent city and classification structures

## **7.3 Introduce Data Quality Controls**

Enforce uniqueness constraints on delivery identifiers  
Validate date formats at ingestion  
Flag missing courier assignments systematically

## **7.4 Centralise Data Model Architecture**

Integrate datasets into a unified analytical model  
Enforce referential integrity upstream  
Reduce reconciliation effort in downstream reporting

# **8\. Conclusion**

UrbanShift Couriers’ datasets are suitable for analytical use only following remediation of identified data quality issues.

Without these controls, analytical outputs would be materially affected in terms of consistency, reliability, and interpretability across derived datasets.

