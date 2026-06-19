# UrbanShift Couriers - AWS Architecture Document

**Project:** UrbanShift Couriers - Data & Analytics Capstone <br>
**Date:** 16/06/2026 <br>
**Companion diagram:** `project4_architecture_diagram.png` <br>
**AWS account:** 616601120321 · **Region:** US West 2 <br>

---


## 1. Overview

UrbanShift Couriers runs last-mile parcel delivery across six UK cities. Its operational data lives in four disconnected systems: customer accounts, the courier roster, parcel tracking, and incident reporting, which makes it impossible to see the business as a whole. Our brief is to bring that data together and answer three questions: which accounts are profitable, where operational risk concentrates, and which customers are at risk of churning.

This architecture is a small, serverless analytics pipeline on AWS that does exactly that and no more. Four CSV extracts land in object storage, are profiled and cleaned, then read by two independent pipelines off the same curated data; SQL analysis in Amazon Redshift, and churn modelling in Jupyter notebooks hosted in SageMaker Canvas. Every stage is access-controlled. The design favours managed, pay-per-use services because the workload is a fixed, one-week engagement with bursty usage, and we should never pay for idle infrastructure, and we should not hand-build anything a managed service already does well.

The six AWS services in scope are Amazon S3, AWS Glue DataBrew, Amazon SageMaker Data Wrangler, Amazon Redshift Serverless, Amazon SageMaker Canvas, and AWS IAM.


## 2. Pipeline walkthrough - the six sections

The architecture is organised into six sections, matching the numbered callouts on the companion diagram. Each one states what happens, which AWS services it uses, and why those services were chosen; the deeper service-by-service rationale is in section 4.

**1 · Data Sources.** The four operational extracts - `customers` (120), `couriers` (65), `deliveries` (~100,110, the central fact table) and `incidents` (~22,390), are uploaded to the Amazon S3 raw zone. *Why S3:* cheap, durable, effectively unlimited object storage that decouples storage from compute, so every later service reads the same canonical files; the raw zone is kept write-once so the original source is always reproducible.

**2 · Data Preparation.** AWS Glue DataBrew profiles the raw files and surfaces the data-quality issues; Amazon SageMaker Data Wrangler, run inside SageMaker Canvas, then cleans and standardises them (de-duplicate deliveries, fix city casing and date formats, replace missing courier IDs with a placeholder, flag unmatched incidents) and writes the result to the Amazon S3 curated zone. *Why these:* DataBrew gives no-code, reproducible profiling for the data audit; Data Wrangler gives a reusable, self-documenting cleaning flow; running it in Canvas means one no-code workspace serves both preparation and modelling.

**3 · Data Modelling** *(pipeline A off the curated data).* Jupyter notebooks in SageMaker Canvas read the curated data and build the churn model; engineering customer-snapshot features (60-day windows, leakage-controlled) and staging intermediate data through an Amazon S3 modelling zone between the feature-engineering, modelling and analysis steps, then export the ranked `churn_watchlist.csv`. *Why notebooks:* the snapshot/windowed feature logic is far cleaner and more efficient in code than in a visual tool; S3 staging keeps each notebook step reproducible and decoupled.

**4 · Data Analysis** *(pipeline B off the curated data).* Amazon Redshift Serverless loads the curated data and builds a curated analytical view; the Redshift Query Editor runs the SQL behind the profitability and operational-risk questions. *Why Redshift Serverless:* the analysis is join-heavy and repeated, ideal for a columnar warehouse, and the workload is bursty, so pay-per-use beats an always-on cluster. This pipeline reads the same curated bucket as Data Modelling, but the two never interact.

**5 · Data Security (AWS IAM).** AWS IAM should enforce least-privilege access across every stage. We design two scoped roles: a read-write pipeline role (builds the pipeline) and a read-only analyst role (query and model), under a permissions boundary. In the shared lab account all users currently share one permission set, so this is a recommended design rather than a deployed control (detailed in section 6).

**6 · Findings.** The outputs of both pipelines are brought together for leadership: the analysis pipeline produces graphs and CSV files (profitability and operational risk) and the modelling pipeline produces the ranked **`churn_watchlist.csv`** (retention). Together they answer the three business questions.


## 3. How the architecture answers the three business questions

The architecture is not abstract plumbing, every service exists to answer one of the three questions. All three run off the same curated analytical view (section 5), so one pipeline produces three answers.

| Business question                                      | Data joined (through `deliveries`)                                                                                       | Service & output |
|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|---|
| **Profitability** - which accounts make money?         | `customers` × `deliveries` - revenue per account vs. cost to serve (volume, failed/returned rate, incident load)         | Redshift SQL → chart of profit by account/segment |
| **Operational risk** - where do incidents concentrate? | `deliveries` × `incidents` × `couriers` - by courier type, shift pattern and city                                        | Redshift SQL → chart of incident rate by segment |
| **Customer retention** - who is likely to churn?       | a (customer × snapshot) feature table engineered in the Canvas notebooks from `deliveries` and `incidents` (section 5.3) | SageMaker Canvas notebooks → ranked `churn_watchlist.csv` |

The first two are SQL questions answered in the Redshift pipeline; the third is a prediction answered in the notebook pipeline. Both read the same curated data from S3 but run independently: a warehouse for descriptive SQL, notebooks for predictive modelling.


## 4. Service choices - and why

### 4.1 Amazon S3 - the data lake (raw and curated zones)
S3 is the backbone of the pipeline: cheap, effectively unlimited, durable object storage that every other service reads from and writes to. We use two prefixes with different rules. The `raw/` zone is our source of truth, so if a cleaning step is wrong we can always reproduce from the original extracts. The `curated/` zone holds the cleaned, analysis-ready outputs and is allowed to be overwritten as the cleaning flow is re-run. We chose S3 over loading the CSVs straight into the warehouse because decoupling storage from compute lets DataBrew, Data Wrangler, Redshift and Canvas all read the same canonical files independently, and because raw object storage is far cheaper than warehouse storage for data we are not actively querying.

### 4.2 AWS Glue DataBrew - data-quality profiling
DataBrew gives us automated, point-and-click data profiling over the raw files: null counts, value distributions, duplicates, and format inconsistencies, with no code to write. We chose it for the audit step because it surfaces issues quickly and produces shareable profile output that becomes evidence in the cleaning log. The alternative, profiling by hand in a notebook is slower and less reproducible, and the brief assigns DataBrew specifically to the audit.

### 4.3 Amazon SageMaker Data Wrangler - cleaning
Data Wrangler was run inside SageMaker Canvas letting us build the cleaning as a reusable visual flow: de-duplicating deliveries on `delivery_id`, standardising city casing and date formats across the datasets, replacing the ~4% missing courier IDs with a `Third Party` entry, and flagging and removing incident records whose `delivery_id` has no match (`INVALID`). The cleaned data is written to `curated/`. We chose a visual flow over hand-written pandas because it is reproducible, self-documenting and re-runnable, which matters for the cleaning log's accountability requirement; running it from Canvas also means one no-code workspace covers both cleaning and modelling.

### 4.4 Amazon Redshift Serverless - the analytical warehouse
Redshift is our SQL engine for the profitability and operational-risk questions, one of the two independent pipelines reading the curated S3 data (the other being the modelling notebooks). It holds the relational schema, a curated analytical view that joins the four tables through `deliveries`, and runs the multi-table queries. We chose the Serverless variant over a provisioned cluster, because the workload is bursty and short-lived over a few days of intermittent querying, so paying per-RPU-second for what we use beats paying for an always-on cluster. We chose a warehouse over querying the CSVs directly (e.g. with Athena) because the analysis is join-heavy and repeated, which is exactly what a columnar warehouse with a pre-built view is optimised for.

### 4.5 Amazon SageMaker Canvas - churn prediction
SageMaker Canvas is the managed SageMaker workspace we used for two jobs: running Data Wrangler for the cleaning (section 4.3), and hosting the Jupyter notebooks that do the churn feature engineering, modelling and analysis. The notebooks read the curated data straight from S3 (independently of the Redshift pipeline) and stage intermediate data back through S3 between the feature-engineering, modelling and analysis steps. We deliberately did this in notebooks rather than Data Wrangler or the no-code builder because it is easier to see precisely what is done to the data, and because the modelling and analysis can be refined and worked on in readable steps that are easy to follow, explain and defend. The model is kept interpretable (ROC-AUC and feature importance) so it can be defended in business language.

### 4.6 AWS IAM - access control
IAM is the control plane that decides who can do what across every service above. Its design is detailed in section 6. It is one of the six services precisely because, to an audit audience, who can touch the data is as important as what the pipeline does.

| Service | Role in the pipeline | Why this service (vs. the alternative) |
|---|---|---|
| Amazon S3 | Data lake (raw, curated and modelling zones) | Cheap, durable and effectively unlimited; decouples storage from compute so every stage reads the same canonical files (vs. loading CSVs straight into the warehouse) |
| AWS Glue DataBrew | Data preparation: profiles the raw data | Automated, no-code, reproducible data-quality audit (vs. profiling by hand in a notebook) |
| Amazon SageMaker Data Wrangler | Data preparation: cleaning, run inside Canvas | Reusable, self-documenting visual cleaning flow (vs. one-off pandas scripts) |
| Amazon Redshift Serverless | Data analysis: SQL warehouse + analytical view | Join-heavy, repeated and bursty workload, so a pay-per-use columnar warehouse fits (vs. a fixed cluster or raw Athena scans) |
| Amazon SageMaker Canvas | Data modelling: hosts the Jupyter notebooks for feature engineering and the churn model | Managed ML workspace; notebooks give transparent, refinable, step-by-step control over the complex snapshot feature engineering and keep the model interpretable (vs. the no-code builder, which cannot express it) |
| AWS IAM | Data security: access control | Least-privilege governance with two scoped roles under a permissions boundary (vs. broad, shared credentials) |


## 5. Data model and the two pipelines

### 5.1 Data model
The four sources form a simple star around the delivery event:

- **`deliveries`** (≈100,110 rows) is the central fact table; one row per parcel, carrying revenue, status, time taken, and the foreign keys `customer_id` and `courier_id`.
- **`customers`** (120) and **`couriers`** (65) are dimensions joined to deliveries on those keys.
- **`incidents`** (≈22,390) links back to a delivery on `delivery_id`, roughly one incident per five deliveries.

### 5.2 Two independent pipelines off the curated data
The curated data in S3 feeds two pipelines that do not interact, they simply read the same bucket:

- **Redshift pipeline (SQL):** Amazon Redshift Serverless loads the curated data and builds a curated analytical view (one row per delivery, joined to customer / courier / incident) to answer profitability and operational risk in SQL.
- **Notebook pipeline (modelling):** Jupyter notebooks in SageMaker Canvas read the curated data and engineer a (customer × monthly snapshot) feature table, then model and analyse, staging data in S3 between steps.

Keeping them separate means each consumer reads one canonical source (S3 `curated/`) without coupling, and either can change without breaking the other.

### 5.3 Where the feature engineering runs
The notebook pipeline engineers the (customer × monthly snapshot) feature table from the cleaned data inside the Canvas notebooks, staging intermediate data through the S3 modelling zone between steps. The feature definitions, target and leakage controls are owned by the Data Scientist / ML Engineer and documented in the Feature Specification; the architecture only provides where that work runs (Canvas notebooks) and where its inputs and outputs live (S3).


## 6. IAM role design

**Current reality.** The shared lab account was provisioned for us with a single permission set; everyone on the team signs in with the same broad permissions, and we do not control account-level IAM (there are no per-user groups or scoped roles). So the model below is the design we recommend, not a control deployed in the lab; we are upfront about that gap rather than claiming access controls we do not have.

**Recommended design (least privilege).** In a real deployment, access should follow least privilege, every identity gets only the minimum it needs. We would define two roles, both constrained by the permissions boundary the tutor provided (a ceiling that caps what a role can ever do, even if a policy is written too broadly).

**Pipeline role (read-write).** Used to build the pipeline. It can read and upload to `raw/` but cannot delete from it (protecting the source of truth), and has full read/write/overwrite on `curated/`, plus the access needed to run DataBrew, Data Wrangler, and load Redshift.

**Analyst role (read-only).** Used to query and model. It can read `curated/` and run `SELECT` queries in Redshift and read the curated data in Canvas, but cannot write to `raw/`, cannot write to `curated/`, and cannot delete anything.

We have written the role definitions, S3 policies, trust policy and boundary as deployable code in `aws_setup/` (`create_iam_roles.py` + `iam_policies/`), together with a test script (`test_iam_restrictions.py`) that assumes the analyst role and checks that write and delete attempts return *Access Denied*. In the shared lab account these roles are not deployed, so this is how we would create and validate the controls, not a result we can show today.


| Role | Can | Cannot | Used by |
|---|---|---|---|
| Pipeline (read-write) | Read/upload `raw/`; full `curated/`; run DataBrew, Data Wrangler; load Redshift | Delete from `raw/` | Data Engineer / pipeline |
| Analyst (read-only) | Read `curated/`; `SELECT` in Redshift; read curated data in Canvas | Write `raw/` or `curated/`; delete anything | Data Scientist, ML Engineer, analysts |


## 7. Security & data governance

Beyond IAM, the design applies standard guardrails appropriate to an audit audience:

- **Encryption.** S3 server-side encryption (SSE) is enabled by default on the bucket, and Redshift Serverless encrypts data at rest; all access is over TLS.
- **Source-of-truth integrity.** The `raw/` zone is write-once; reproducibility from raw is preserved.
- **No data in version control.** Raw CSVs stay in S3 and are never committed to Git; the repo's `.gitignore` excludes CSVs and the `config.py` holding account details.
- **Data sensitivity.** Customer and courier records are business-confidential (and although the names in this dataset are fictional, we treat the schema as if it carried real PII). Under the recommended role design (section 6), access to identifiable fields would sit with the read-only analyst role; nothing is exposed publicly.
- **Auditability.** Once the per-task roles are deployed (section 6), actions become attributable to a role; today the data cleaning log is the main audit trail, recording every data decision with rationale.


## 8. Scale reasoning - what changes at 10× volume

Today we process ~100k deliveries and ~22k incidents over nine months. The question an audit panel will ask is what happens at 10× (≈1M deliveries, ≈220k incidents) and beyond. The strength of this architecture is that most of it scales without redesign, but the cost and the operating model change in predictable ways.

**What does *not* need to change.** Amazon S3 scales to any volume automatically, storage is effectively unlimited, and we pay only for what we store. Redshift Serverless scales its compute (measured in RPUs) up and down automatically with query load, so larger scans are handled without us provisioning anything. SageMaker Canvas will simply train on more rows.

**What changes, and what we would do about it:**

- **Cleaning becomes the bottleneck.** DataBrew and Data Wrangler job time (and therefore cost) grows roughly with row count. At 10× we would profile on a representative sample rather than the full file, and run the cleaning flow as a scheduled job rather than an interactive session.
- **Loads go incremental.** A full reload of `curated/` into Redshift every run is fine at 100k rows; at 1M+ we would switch to incremental / append-only loads (only new deliveries), partition the curated data in S3 by city and month, and define Redshift distribution and sort keys (e.g. distribute `deliveries` on `customer_id`, sort on `delivery_date`) so joins and date-range scans stay fast.
- **The pipeline needs orchestration.** At one week and 100k rows we can run the steps by hand. At production scale we would add orchestration (e.g. AWS Step Functions or Glue workflows) to run profile → clean → load → retrain on a schedule, with failure alerts.
- **The model retrains on a cadence.** Churn prediction would move from a one-off Canvas build to a scheduled retrain (e.g. monthly) as new behaviour accrues, with monitoring for drift.


## 9. Cost framing

The architecture is deliberately pay-per-use, so cost tracks usage rather than provisioned capacity. The drivers, largest first:

| Cost driver | Billed on | Relative magnitude     | Control |
|---|---|------------------------|---|
| **SageMaker Data Wrangler** (`ml.m5.4xlarge`) | Per hour the session is open | Highest, easy to waste | Close the session the moment the flow is exported |
| **Amazon Redshift Serverless** | Per RPU-hour while querying | Medium, elastic        | Scales to zero when idle; sort/partition keys cut data scanned |
| **SageMaker Canvas** | Per session / model training | Low–medium             | Build one model, log out when done |
| **AWS Glue DataBrew** | Per node-hour of profiling/jobs | Low                    | Profile on a sample at scale |
| **Amazon S3** | Per GB-month + requests | Negligible (gigabytes) | Lifecycle rules move old raw extracts to cheaper storage |

The headline: compute is the cost, storage is rounding error. Because everything is serverless or session-based, the dominant lever is simply turning things off, which is why closing Data Wrangler and Canvas sessions is in our operating discipline.


## 10. Improvements & future enhancements

The architecture is deliberately minimal and fit for a one-week analysis. To mature it into a repeatable, production service we would prioritise the following, several of which also answer "what changes at scale" (section 8):

- **Orchestration & automation.** The stages are currently run by hand. AWS Step Functions (or Glue workflows) would orchestrate profile → clean → load → feature-engineer → retrain on a schedule, with failure alerts, removing manual hand-offs and making every run reproducible.
- **Productionise the modelling pipeline.** Promote the notebook feature engineering to a versioned SageMaker Pipeline so features and the model are reproducible and retrainable on a cadence, with SageMaker Model Monitor watching for data and prediction drift.
- **Automated data-quality gates.** Turn the DataBrew checks into enforced AWS Glue Data Quality rules that block bad data from reaching the curated zone, rather than relying on a manual pass.
- **Catalogue & ad-hoc query.** A Glue Data Catalog over the S3 zones would make the data discoverable and queryable, and enable Amazon Athena for ad-hoc questions without standing up Redshift.
- **Infrastructure as Code.** The S3 + IAM setup is already scripted (`aws_setup/`); extend it to full CloudFormation / Terraform so the whole stack is versioned and reproducible across accounts.
- **Observability & cost control.** Add Amazon CloudWatch dashboards and alarms (job failures, spend, idle Canvas / Data Wrangler sessions), S3 lifecycle policies to tier old raw extracts, and Redshift Serverless usage limits / budgets.
- **Security hardening.** Enable S3 versioning and CloudTrail, encrypt with AWS KMS customer-managed keys, and tighten the IAM roles further (per-prefix conditions, MFA on sensitive actions).
- **Consolidate the staging layers.** Formalise the raw / curated / modelling zones into a clear medallion layout and move from full reloads to incremental loads as volume grows (section 8).


## 11. Assumptions & limitations

An audit audience rewards honesty about what the design does *not* cover:

- **Single region, no DR.** The pipeline runs in one region with no disaster-recovery or multi-region failover, this is out of scope for a one-week analytics engagement, but the first thing to add for production.
- **Lab-account constraints.** Service configuration is bounded by the shared lab account and the provided permissions boundary; some production hardening (CloudTrail, GuardDuty, VPC isolation) is assumed rather than implemented.
- **Data-quality caveats flow downstream.** Deliveries with missing courier IDs (~4%) are kept and tagged `Third Party`, so no delivery activity is lost even though courier attribution is unknown. Incident records whose `delivery_id` cannot be matched to a delivery are flagged `INVALID` and removed, so a small number of unmatched incidents are excluded from the incident analysis. These decisions are recorded in the data cleaning log and must be caveated in the findings.
- **Batch, not real-time.** This is a batch analytics pipeline over a historical extract, not a live operational system. Which is appropriate for the questions asked, but it does not give leadership real-time dashboards.


## 12. Summary

This is a small, honest, least-privilege analytics pipeline that uses six managed AWS services to turn four disconnected CSV extracts into evidence for three business questions. It favours pay-per-use over provisioned capacity, protects the source of truth, controls access by role, serves all three questions from a shared curated dataset via two independent pipelines, and scales with predictable, compute-dominated cost by sampling, partitioning, and incremental loads rather than redesign.

**Companion artefacts:** `architecture_diagram.png` (diagram) · `aws_setup/` (S3 + IAM toolkit and the restriction test) · the data cleaning log and feature specification (governance / audit trail) · `ddl.sql` and `analytical_queries.sql`.