# Ajaia LLC — Technical Project Manager Assessment
**Candidate:** SivaVignesh L  
**Email:** sivavignesh.it@gmail.com  
**Portfolio / GitHub:** [https://github.com/sivavigneshl/Ajaia-LLC---Technical-Project-Manager-Assessment](https://github.com/sivavigneshl/Ajaia-LLC---Technical-Project-Manager-Assessment.git)  
**Engagement Reference:** [Ajaia AI Engagement Platform](https://ajaia.ai)  
**Video Presentation Link:** [INSERT_YOUR_VIDEO_LINK_HERE] *(Public / Unlisted link tested in Incognito)*  

---

## Executive Summary
This submission delivers the Technical Project Manager assessment for the **Corrigan Peak Logistics: Dispatch Exception Triage (DET)** engagement. It encompasses:
1. **Task 1: Rigorous Triage & Backlog Ranking** protecting the committed September 8 board go-live.
2. **Task 2: Working Data Normalization Engine (`clean_exceptions.py`)** with automated tests (`test_clean_exceptions.py`) handling dirty EDI feeds.
3. **Task 3: Production-Ready Client Status Update** resetting communication from false optimism to transparent, accountable partnership.
4. **Task 4: AI Workflow Reflection** documenting AI assistance, human judgment, and rejected AI recommendations.

---

## Task 1. Triage & Ranking

| Rank | Item | Source | Decision | Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Item B: Concurrency / Double-Push Race Condition** | Priya Anand (Slack) | **Worked this week** | **P0 Architectural Risk.** In live freight dispatch, duplicate queue pushes result in two dispatchers acting on the same exception, double-booking backup carriers, and immediately destroying user trust on Day 1. Fixing concurrency and non-atomic queue/DB state transitions during launch week under live traffic is a disaster; Priya must implement an idempotent state lock (atomic DB state claim prior to queue push) before this PR merges. |
| **2** | **Item C: DET-121 (Terminal 3 EDI Schema & Null Urgency Scores)** | Jira / DET-121 | **Worked this week** | **P0 Operational Blocker.** Terminal 3 accounts for one-third of Corrigan Peak’s freight network. Exceptions entering with null urgency scores defeat the entire purpose of automated triage. Sitting unaddressed since August 6, this requires immediate TPM escalation to Corrigan Peak IT today to unblock Priya's 2-day schema fix before the end of the week. |
| **3** | **Item D: DET-118 (Terminal Lead Routing-Rules Review Scheduling)** | Jira / DET-118 | **Worked this week** | **P1 Operational Readiness.** Routing rules dictate where exceptions land; without terminal lead validation, dispatcher adoption will fail regardless of code quality. As TPM, I am personally taking ownership today to draft the review agenda and lock slots on their calendars for early next week to preserve UAT and training timelines. |
| **4** | **Item A: COO Request for Automated Carrier Reassignment** | Dana Okafor (Email) | **Declined for Sept 8 (Deferred to Phase 2)** | **Unbounded Scope Creep.** Moving from *decision support* (flagging/routing for human review) to *autonomous execution* (automated carrier re-tendering) requires rate-table logic, carrier dispatch write-back APIs, contract liability checks, and rollback safety. Adding this 3 weeks out guarantees blowing the September 8 board deadline. We protect Dana’s commitment by declining this for launch and positioning it as the Phase 2 headline. |
| **5** | **Item E: UI Color Swap (Different Shade of Blue)** | Marcus Lin (Slack) | **Deferred (Post-Launch)** | **Pure Noise.** A casual cosmetic remark made "in passing" with zero operational impact. Introducing CSS churn and visual re-review cycles three weeks out when data integrity and concurrency require hardening is an unnecessary distraction. |

---

## Task 2. Build Something That Works

### Summary & Verification Note
The production script [`clean_exceptions.py`](file:///clean_exceptions.py) ingests raw, heterogeneous FreightWorks EDI exception exports, canonicalizes non-standard terminal names (`T3`, `TERMINAL 3` $\rightarrow$ `Terminal 3`), standardizes carrier SCAC codes into clean uppercase alphanumeric tokens (`swft`, `Swft` $\rightarrow$ `SWFT`), and parses inconsistent timestamp formats (`YYYY-MM-DD HH:MM:SS`, `MM/DD/YYYY HH:MM`, and ISO 8601 with `Z`) into uniform ISO 8601 UTC timestamps (`YYYY-MM-DDTHH:MM:SSZ`). 

The script generates clean summary counts by `event_type` (`carrier_substitution`: 1, `doc_mismatch`: 2, `missed_pickup`: 2) and isolates unconfident records. Specifically, record **`CPX-88216`** is programmatically flagged because its `carrier_code` is empty in the EDI feed; in FreightWorks, carrier identification is a mandatory foreign key for dispatcher queue assignment and rate lookup, requiring an upstream master shipment join before it can be safely routed. 

To verify that the code **actually worked and did not just run**, a comprehensive automated test suite [`test_clean_exceptions.py`](file:///test_clean_exceptions.py) was built and executed. The suite runs 6 deterministic unit and integration test assertions verifying terminal synonym resolution, SCAC casing, timestamp edge cases, aggregations, and error isolation—all passing cleanly (`Ran 6 tests in 0.051s, OK`).

### Ingestion & Normalization Output

```
================================================================================
CORRIGAN PEAK LOGISTICS - DISPATCH EXCEPTION TRIAGE (DET)
MATERIAL 3: DATA NORMALIZATION AND EXCEPTION AUDIT REPORT
Reference: https://ajaia.ai | Candidate: SivaVignesh L
================================================================================

--- 1. SUMMARY COUNT OF EXCEPTIONS BY EVENT TYPE ---
  - carrier_substitution     : 1 record(s)
  - doc_mismatch             : 2 record(s)
  - missed_pickup            : 2 record(s)
  Total Ingested Exceptions  : 5
  Clean / Validated Records  : 4
  Flagged / Uncleaned Records: 1

--- 2. NORMALIZED RECORDS DATASET ---
ID          | Terminal     | Event Type             | Carrier  | Standardized Timestamp (UTC) | Clean?
------------------------------------------------------------------------------------------------------
CPX-88213   | Terminal 3   | missed_pickup          | SWFT     | 2026-08-14T09:12:00Z     | PASS
CPX-88214   | Terminal 3   | doc_mismatch           | SWFT     | 2026-08-14T09:45:00Z     | PASS
CPX-88215   | Terminal 3   | missed_pickup          | SWFT     | 2026-08-14T10:03:00Z     | PASS
CPX-88216   | Terminal 3   | doc_mismatch           |          | 2026-08-14T11:47:00Z     | FLAGGED
CPX-88217   | Terminal 3   | carrier_substitution   | RLCX     | 2026-08-15T08:02:00Z     | PASS

--- 3. UNCONFIDENT / UNCLEANED RECORDS AUDIT NOTES ---
  [FLAGGED] Record ID: CPX-88216 (Event: doc_mismatch)
    Raw Values     : {'terminal': 'Terminal 3', 'carrier_code': '', 'event_ts': '2026-08-14 11:47:00'}
    Failure Reason : Missing carrier code (empty in EDI feed)
    Impact & Action: Cannot confidently route or score urgency. In FreightWorks EDI,
                     carrier_code is a mandatory foreign key to the carrier dispatch table.
                     Action required: Fallback lookup on FreightWorks master shipment payload.

--- 4. ARTIFACTS EXPORTED ---
  [+] Clean CSV Export : normalized_exceptions.csv
  [+] Audit JSON Export: audit_summary.json
================================================================================
```

---

## Task 3. Client Status Update

**To:** Dana Okafor, VP of Operations, Corrigan Peak Logistics  
**From:** SivaVignesh L, Technical Project Manager, Ajaia ([https://ajaia.ai](https://ajaia.ai))  
**Date:** August 15, 2026  
**Subject:** Corrigan Peak DET — Weekly Project Status & Scope Clarification (September 8 Go-Live)  

---

**Hi Dana,**

Here is our updated project status for the Dispatch Exception Triage (DET) deployment. 

### Overall Health: **YELLOW (At Risk, Critical Path Actions Identified)**
Our primary objective is to protect your committed **September 8 go-live** to the board. To ensure complete alignment, I am recalibrating last Friday’s status report to reflect two dependencies on our critical path that require joint action this week.

---

### 1. Scope Decision: COO Auto-Reassignment Request
Regarding your note on automatically reassigning missed pickups to backup carriers:
* **Our Recommendation:** We recommend **holding this capability for Phase 2** immediately following our September 8 launch, rather than adding it to the current release.
* **Why:** The current build delivers intelligent exception detection, scoring, and routing to human dispatchers. Moving from *decision support* to *automated carrier re-tendering* introduces contractual liability, carrier rate-table lookups, and dispatch write-back logic. Building, testing, and validating automated carrier booking in the remaining 3 weeks would introduce unacceptable risk to the September 8 board deadline.
* **Path Forward:** On September 8, dispatchers will receive prioritized missed-pickup alerts with one-click carrier contact info. We will baseline triage accuracy during the first two weeks of live ops, and scope automated reassignment as our first major post-launch enhancement.

---

### 2. Critical Path & Immediate Actions for This Week

| Item | Status & Impact | Action Required / Owner |
| :--- | :--- | :--- |
| **Terminal 3 EDI Schema (DET-121)** | **Active Blocker.** Urgency scores are returning null for a segment of Terminal 3 exceptions due to unmapped EDI fields. Once confirmed, Priya requires 2 days to update the ingestion parser. | **Corrigan Peak IT:** Confirm Terminal 3 EDI field mappings by **Wednesday, August 16, 12:00 PM EDT**. *(I have flagged the exact fields in a direct note to your IT lead).* |
| **Terminal Lead Routing Reviews (DET-118)** | **Scheduling.** Dispatcher adoption requires sign-off from your three terminal leads on routing thresholds before end-user training begins. | **Ajaia TPM (Siva):** Sending 45-minute calendar invites today for **Tuesday / Wednesday, Aug 22–23**. Asking for your support to ensure attendance. |
| **Queue Concurrency & Idempotency** | **In Progress (Engineering).** Priya identified and is resolving an edge case in dispatcher queue polling to prevent duplicate notifications during network retries. | **Ajaia Engineering (Priya):** Fix merging by Thursday; zero client impact. |

---

### 3. Timeline Outlook
If we receive the Terminal 3 field confirmation by Wednesday at noon, we remain fully on track to deliver:
* **Aug 22–23:** Terminal Lead Routing Rules Sign-off
* **Aug 28 – Sep 1:** Dispatcher End-to-End UAT & Shadow Shifts
* **Sep 8:** **Go-Live across all three terminals**

I will provide our next checkpoint this Thursday afternoon once Terminal 3 ingestion is validated. Please let me know if you would like to connect for 10 minutes today to review the IT escalation.

Best regards,

**SivaVignesh L**  
Technical Project Manager, Ajaia  
[https://ajaia.ai](https://ajaia.ai)  

---

## Task 4. AI Workflow Note

* **Where AI was used:** I utilized an AI coding agent (Antigravity) to rapidly scaffold the initial regex patterns and datetime parsing formats for heterogeneous EDI timestamps in Task 2, generate boilerplate test cases in `test_clean_exceptions.py`, and draft baseline structure for the client update.
* **What was kept strictly human:**
  1. **Strategic Client Stance & Risk Caliber:** The decision to decline Dana’s COO request outright and downgrade the project status from Green to Yellow. An AI assistant initially proposed compromising with a "partial feature toggle" or "experimental automated flag" to avoid saying no to an executive; I rejected that approach because experimental automated carrier dispatching creates real contractual liability and operational chaos.
  2. **Technical Architecture Prioritization:** Elevating Priya’s Slack flag on concurrency and double-queuing (Task 1B) to Rank 1 over the VP’s feature request. Knowing distributed systems and real-world ops, if two dispatchers receive the same exception, trust in the tool collapses on Day 1.
  3. **Operational Empathy:** Crafting the tone of Dana's status update so that it demonstrates executive partnership and shields her board commitment rather than reading like vendor defensiveness.
* **One specific thing an AI tool got wrong or rejected:**
  When generating the initial data normalization logic, the AI attempted to "impute" or fill in the missing `carrier_code` in record `CPX-88216` with `"UNKNOWN"` or copy the carrier from the previous row (`"SWFT"`), marking it as successfully cleaned. I rejected this hallucinated imputation; in transportation EDI systems, fabricating a carrier code corrupts downstream billing and routing tables. I enforced strict data contract validation: if the carrier key is absent, the record must be surfaced and flagged for upstream resolution.

---

## Verification & File Manifest
* [`clean_exceptions.py`](file:///clean_exceptions.py) — Core Python 3 normalization & audit engine.
* [`test_clean_exceptions.py`](file:///test_clean_exceptions.py) — Comprehensive automated test suite (6 tests passing).
* [`material3_input.csv`](file:///material3_input.csv) — Raw input data from Material 3.
* [`SUBMISSION.md`](file:///SUBMISSION.md) — Master submission document.
