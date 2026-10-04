# Video Presentation Script & Talking Points (5–7 Minutes)
**Role:** Technical Project Manager — Ajaia LLC  
**Candidate:** SivaVignesh L  
**Assessment:** Corrigan Peak Logistics — Dispatch Exception Triage (DET)  
**Format:** Screen Share + Face Camera (Loom or unlisted YouTube with "Ajaia" in the title)

---

### Timing Breakdown
* **0:00 – 1:00:** Context & Task 1 (Weekly Triage & Real Risk vs. Noise)
* **1:00 – 2:30:** Task 2 Build Demo (Live terminal execution of `clean_exceptions.py` and `test_clean_exceptions.py`)
* **2:30 – 4:00:** Task 3 Client Status Update & Scope Defense (Why Yellow, how we protect Dana’s board date)
* **4:00 – 4:45:** Task 4 AI Workflow (Where AI helped, what was kept human, what was rejected)
* **4:45 – 6:00:** Personal Introduction, Why This Role, Why Ajaia, and Salary Expectations

---

### Step-by-Step Script & Talking Points

#### 1. Introduction & Triage Rationale (1:00)
> *"Hi Ajaia team, I'm Siva Vignesh, and this is my walkthrough for the Corrigan Peak Logistics Dispatch Exception Triage project. With three weeks until the September 8 go-live, our primary objective is to protect Dana Okafor's board-committed date with total transparency and engineering rigor.*
> 
> *Looking at this week’s incoming requests, I triaged them by separating core operational risk from noise:*
> * **Rank 1 (Worked):** Priya’s flag on retry behavior and queue concurrency. If a queue push succeeds but the database update fails, an exception gets pushed twice. In dispatch, duplicate tickets mean two dispatchers booking duplicate backup carriers. That destroys user trust on Day 1. Priya is implementing an idempotent state claim this week before PR merge.
> * **Rank 2 (Worked):** DET-121 (Terminal 3 EDI schema mismatch). Terminal 3 is 33% of the fleet, and urgency scores are returning null. It’s been sitting since August 6. I’ve escalated to Corrigan Peak IT today for an answer by Wednesday so Priya can turn around the 2-day parser fix.
> * **Rank 3 (Worked):** DET-118 (Terminal Lead routing-rules review). Code is only half the battle; if terminal leads don't validate the routing thresholds, dispatchers will bypass the tool. I’m locking in their calendar slots today for next week.
> * **Rank 4 (Declined for Sept 8):** Dana’s COO asked to auto-reassign missed pickups to backup carriers. Moving from decision support to autonomous carrier booking introduces rate tables, carrier API writes, and liability. Adding that in 3 weeks guarantees a blown launch. We protect the date by holding it for Phase 2.
> * **Rank 5 (Deferred):** The request to swap the UI shade of blue. This is pure noise—a cosmetic passing comment that creates CSS churn while our data pipelines and concurrency need hardening.*"

---

#### 2. Live Demo of Task 2 Build (1:30)
*(Screen share your terminal / IDE with `clean_exceptions.py` and `test_clean_exceptions.py`)*

> *"Now let's look at Task 2. Material 3 gave us messy FreightWorks EDI export data with inconsistent terminal names, mixed-case SCAC codes, and multiple timestamp formats.*
> 
> *(Run: `python clean_exceptions.py`)*
> 
> *As you can see, the script:*
> 1. *Canonicalizes terminal names ('T3' and 'Terminal 3' mapped uniformly to 'Terminal 3').*
> 2. *Standardizes carrier codes ('swft', 'Swft' to uppercase 'SWFT').*
> 3. *Parses heterogeneous dates—including standard strings, slash formats, and ISO strings with Z—into standard ISO 8601 UTC.*
> 4. *Aggregates clean counts: 2 missed pickups, 2 document mismatches, and 1 carrier substitution.*
> 5. *Most importantly, it flags record CPX-88216 as uncleaned. Its carrier code is completely empty. In EDI freight logistics, carrier code is a mandatory foreign key for queue routing and billing. Rather than hallucinating a placeholder, we flag it for upstream join with the master shipment table.*
> 
> *(Run: `python test_clean_exceptions.py`)*
> 
> *To prove that this didn't just run, but actually worked, I built a 6-assertion automated test suite verifying edge cases, terminal synonyms, timestamp parsing, and failure isolation. All 6 tests pass in 0.05 seconds."*

---

#### 3. Client Status Update & Managing Dana (1:30)
*(Show the email draft in `SUBMISSION.md`)*

> *"In Task 3, I reset the status update from last Friday's artificial 'Green' to an honest 'Yellow'. Vendors often fear the color Yellow, but clients appreciate realistic accountability that protects their commitments.*
> 
> *Key elements of how I communicated to Dana:*
> 1. *Tone: Supportive partnership. I affirmed our shared goal—protecting her September 8 board delivery.*
> 2. *Managing the COO request: I gave her a defensible, airtight rationale to take back to her COO: Sept 8 delivers the core triage tool and baselines dispatcher accuracy; automated carrier booking is our headline Phase 2 capability.*
> 3. *Clear Asks: I didn't say 'IT is blocking us.' I gave a specific cutoff: Corrigan Peak IT must confirm the Terminal 3 EDI fields by Wednesday at noon so Priya can deliver the fix by Friday, and I asked for her backing to ensure terminal leads attend next week's reviews.*"

---

#### 4. Task 4: AI Workflow Reflection (0:45)
> *"Regarding AI usage: I used AI as a high-velocity accelerator to scaffold the regex patterns, datetime formats, and unit test mocks.*
> 
> *What I kept strictly human was the engineering judgment and strategic client posture: choosing to prioritize Priya's concurrency risk over the VP's feature request, and having the courage to tell the client 'no' on auto-reassignment.*
> 
> *One thing I explicitly rejected: the AI originally suggested auto-filling the missing carrier code in record CPX-88216 with 'UNKNOWN' or copying from the prior row to make the dataset look 100% clean. In enterprise data systems, silent imputation causes downstream corruption. I overrode that to enforce strict data contracts and explicit audit flagging."*

---

#### 5. Close: Personal Pitch, Why Ajaia & Salary Expectations (1:15)
> *"A quick bit about me:*
> * *I have 10+ years in IT, currently serving as IT Project Manager at Optimapharm, a global CRO. Over the past several years, I've single-handedly architected and deployed over 10 AI, automation, and serverless solutions—including a 7-agent CrewAI research service, LLM-powered Teams bots with strict guardrails, and enterprise ERP/CRM integrations.*
> * *Why this role and why Ajaia? Ajaia is building real, AI-native forward-deployed engineering solutions for live operations. I thrive in seats where technical depth meets delivery ownership—where you can write the Python script, audit the distributed system architecture, and command the executive room with honest client management.*
> * *Compensation Expectations: My salary expectation for this Technical Project Manager role is [INSERT YOUR TARGET RANGE, e.g., $110,000 – $130,000 USD / competitive annual package depending on benefits and equity structure].*
> 
> *Thank you for your time and this fantastic real-world assessment. I look forward to working together at Ajaia!"*
