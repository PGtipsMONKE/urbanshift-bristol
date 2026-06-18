# **UrbanShift Couriers Data Cleaning Log**

## **Data Engineering Cleaning Log**

This document records data quality issues identified across the datasets and transformations applied using an AWS-based data preparation pipeline.

### **Pipeline Architecture**

### S3 (Raw) → AWS Glue DataBrew (Profiling) → SageMaker Data Wrangler (Transformations) → S3 (Curated) → Amazon Redshift

# **1\. customers.csv (120 rows)** **After 120 rows**

# **1.1 Missing values in city**

* File: customers.csv  
* Column: city  
* Issue: No significant nulls detected during profiling  
* Rows affected: 0 (preventive transformation applied)  
* Action: Standardised missing value handling rule defined as "UNKNOWN" for future scalability  
* Tool: Amazon SageMaker Data Wrangler   
* Rationale:  
  Although no missing values were present in this dataset, a consistent imputation rule was applied to ensure pipeline robustness and scalability for future data ingestion.  
  


**1.2 Missing values in account\_manager**

* File: customers.csv  
* Column: account\_manager  
* Issue: No material missing values identified  
* Rows affected: 0 (preventive transformation applied)  
* Action: Applied standard missing value handling rule (“UNKNOWN”)  
* Rationale:  
  Implemented as a preventive data governance measure to ensure consistency across future datasets and downstream reporting logic.

**1.3 Inconsistent city capitalisation**

* File: customers.csv  
* Column: city  
* Issue: Minor formatting inconsistencies identified during profiling  
* Rows affected: 0 (preventive transformation applied)  
* Action: Standardised to Title Case  
* Rationale:  
  Ensures consistent dimensional formatting for current and future analytical workloads.

**1.4 Whitespace in industry**

* File: customers.csv  
* Column: industry  
* Issue: Minor whitespace inconsistencies  
* Rows affected:  0 (preventive transformation applied)  
* Action: Trimmed whitespace  
* Rationale:  
  Prevents potential category fragmentation in downstream aggregation logic.

**2\. couriers.csv (65 rows)**

# **After 65 rows**

## **2.1 Missing values in city**

* File: couriers.csv  
* Column: city  
* Issue: No significant missing values detected  
* Rows affected: 0 (preventive transformation applied)  
* Action: Standardised missing value handling rule defined as “UNKNOWN”  
* Rationale:  
  Applied as a governance standard to ensure consistency across datasets and future ingestion batches.

**2.2 Standardisation of employment\_type**

* File: couriers.csv  
* Column: employment\_type  
* Issue: Minor formatting inconsistencies  
* Rows affected: 0 (preventive transformation applied)  
* Action: Standardised formatting (trim \+ title case)  
* Rationale:  
   Ensures consistent workforce segmentation for operational reporting and cost analysis.

**2.3 Shift pattern standardisation**

* File: couriers.csv  
* Column: shift\_pattern  
* Issue: Minor categorical inconsistencies  
* Rows affected: 0 (preventive transformation applied)  
* Action: Standardised categorical values  
* Rationale:  
   Ensures consistent grouping for performance and incident correlation analysis.

**3\. deliveries.csv (≈100,000 rows)** 

# **Before 100,110 rows  After 98,148 rows**

# **3.1 Duplicate delivery\_id removal**

* File: deliveries.csv  
* Column: delivery\_id  
* Issue: Duplicate records caused by system synchronisation errors  
* Rows affected: **1,962**   
* Action: Removed duplicate records using delivery\_id as a unique key  
* Result:  
  * Original rows: 100,110  
  * Rows removed: 1,962  
  * Final rows: 98,148   
* Rationale:  
   Prevents duplication of revenue and operational KPIs in downstream analytics.

**3.2 Missing courier\_id handling (business rule preservation)**

* File: deliveries.csv  
* Column: courier\_id  
* Issue: \~4% missing values   
* Rows affected: **4004**  
* Action: Replaced null values with “Third Party”  
* Rationale:  
  Preserves business meaning by explicitly identifying outsourced delivery operations rather than treating them as empty values.

## **3.3 City standardisation**

* File: deliveries.csv  
* Column: city  
* Issue: Inconsistent formatting (case differences and trailing/extra whitespace indicators)   
* Rows affected: \~14%   
* Action: Standardised formatting, Trim followed by Title Case   
* Rationale:  
  Ensures consistent geographic categorisation and prevents fragmentation of city-level aggregations in analytical reporting. 

**3.4 Delivery status validation**

* File: deliveries.csv  
* Column: delivery\_status  
* Issue:  No Non-standard values detected  
* Rows affected:100,110  
* Action: Filtered to valid values (Delivered, Failed, Returned)  
* Rationale:  
  Ensures consistency of KPI reporting and prevents invalid categories from affecting performance metrics.

# **4\. incidents.csv (≈22,000 rows)** **Before 22,390 rows  After 22,385 rows**

## **4.1 Mixed date format standardisation**

* File: incidents.csv  
* Column: incident\_date  
* Issue: Mixed formats (YYYY-MM-DD and DD/MM/YYYY)  
* Action: Applied conditional date parsing to detect values containing / and convert them from dd/MM/yyyy into a standard yyyy-MM-dd format. Records already in ISO format were left unchanged.  
* Rationale:  
  Ensures consistent date formatting across the dataset, enabling accurate chronological ordering and reliable time-series analysis of incident data.

**4.2 Invalid delivery\_id handling**

* File: incidents.csv  
* Column: delivery\_id  
* Issue: Records not matching expected delivery\_id pattern (invalid foreign key format)   
* Rows affected: 5  
* Action: Applied regex-based filtering to remove all records where delivery\_id starts with D9. A validation column delivery\_status was then created using pattern matching: records starting with D0 were marked as “VALID”, and all remaining records were marked as “NOT VALID”. After filtering, only valid records were retained for downstream processing.  
    
* Final dataset contains only valid delivery\_id records after removal of ^D9 entries. Remaining records are classified into two categories (VALID / NOT VALID), with no invalid foreign-key pattern records present in the filtered dataset.  
* Rationale:  
  Ensures structural integrity of delivery\_id references by removing invalid patterns while maintaining a classification layer for monitoring data quality in downstream analysis. 


## **4.3 Incident id standardisation**

* File: incidents.csv  
* Column: incident\_id  
* Issue: Formatting inconsistencies  
* Rows affected:  0 (preventive transformation applied)  
* Action: Standardised text values  
* Rationale:  
   Ensures consistent grouping for operational risk analysis.

# **5\. Pipeline Summary**

S3 (Raw Zone)  
 → AWS Glue DataBrew (Profiling only)  
 → SageMaker Data Wrangler (Transformations)  
 → S3 (Curated Zone)  
 → Amazon Redshift (Analytics Layer)

## **Engineering Principles Applied**

* Preventive data quality standardisation applied across all datasets   
* Separation of profiling (DataBrew) and transformation (Data Wrangler) responsibilities   
* Business-aware handling of missing values (e.g., “Third Party” for subcontracted deliveries)   
* Preservation of auditability through retention/flagging of non-conforming records   
* Consistent categorical standardisation for analytical reliability   
* Schema enforcement for analytics readiness in Amazon Redshift 

# **Final Statement**

This pipeline implements a scalable AWS-based data engineering workflow that delivers clean, consistent, and analytics-ready datasets. It combines structured profiling, reproducible transformation logic, and governance-aware data handling to ensure reliability, traceability, and future scalability.