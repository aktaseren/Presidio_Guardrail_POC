##  How to Run the Demo (Local)

This project is designed to be **lightweight and reproducible**.
We do **not** commit virtual environments or spaCy models to Git.

### 1. Prerequisites

* Python **3.10+** (tested with 3.11)
* `pip`
* macOS / Linux / WSL recommended

Check:

```bash
python --version
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/aktaseren/Presidio_Guardrail_POC.git
cd Presidio_Guardrail_POC
```

---

### 3. Create and Activate a Virtual Environment

```bash
python -m venv presidio_poc
source presidio_poc/bin/activate
```

You should now see:

```bash
(presidio_poc)
```

---

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Download spaCy Language Model (Required)

Presidio uses spaCy under the hood for Named Entity Recognition (NER).
We intentionally **do not** commit this model because it is large (~400MB).

```bash
python -m spacy download en_core_web_lg
```

---

### 6. Run the Application

If using Streamlit:

```bash
streamlit run app.py
```

The UI will be available at:

```
http://localhost:8501
```

---

### 7. Run the Demo Use Cases

Use the files under `test_usecases/` **in order**:

1. `01_safe_internal.txt` → **ALLOW**
2. `02_support_ticket.txt` → **REDACT**
3. `03_payment_record.txt` → **BLOCK**
4. `04_hr_report.txt` → **REDACT (Custom Entity)**
5. `05_merchant_onboarding.txt` → **BLOCK**

Each file demonstrates:

* Detection results
* Risk score
* Policy decision
* Whether data is allowed into the vector store

---

### Deactivate Environment (When Done)

```bash
deactivate
```

---

## ⚠️ Important Notes

* **Do NOT commit**:

  * Virtual environments (`presidio_poc/`, `venv/`)
  * `site-packages`
  * spaCy models
* All dependencies are reproducible via:

  * `requirements.txt`
  * `spacy download en_core_web_lg`

---

# DEMO ARCHITECTURE OVERVIEW

i. Document Source (pdf, docx, txt or similar formats)

ii. Presidio Scanner (PII / PCI Data Detection)

iii. Policy Engine (Allow / Redact / Block)

iv. Vector Store (Databricks VS / Pinecone / FAISS / OpenSearch or similar) [Embeddings]

v. LLM / RAG System Pipeline


# LANGUAGE MODEL
en_core_web_lg is a high-accuracy English AI model from spaCy language models that helps Presidio recognize human names and places, not just patterns like numbers or emails.
(Detecting entities better compared to SpaCy small and medium language models. Fewer false negatives)

Breakdown of the name:
- en → English
- core → General-purpose model
- web → Trained on web text (news, blogs, articles, etc.)
- lg → Large model (higher accuracy, bigger size)

Why Presidio Needs It?: Presidio uses spaCy under the hood for:
Named Entity Recognition (NER)
→ Detecting things like:
PERSON names
LOCATIONS
ORGANIZATIONS

# DEMO STRUCTURE

In this demo, We use two main modules of Presidio():

- Analyzer → Detects entities
- Anonymizer → Redacts, masks, or replaces them
- **NOT Implemented: Image Redactor: Redacting PII entities from images using OCR
- **NOT Implemented: Structured: Detecting PII entities in structured/semi-structured data


It finds things like: Credit cards, Names, Emails, Phone numbers, IBAN, SSN, Locations, Custom specific entities (We can add these)

# Usecases (Demo Flow for Stakeholders):

Run them in this order:

    01_safe_internal.txt → “This goes straight into our AI”

        Demo result:

            Risk Report: Empty or very low

            Decision: ALLOW

            Sends to Vector DB

    02_support_ticket.txt → “We protect customer privacy automatically”
   
        Demo result:

        Detects: PERSON, EMAIL, PHONE, LOCATION

        Decision: REDACT

        Shows clean redacted doc

        Sends safe version to vector DB

    03_payment_record.txt → “This never even reaches the LLM”

        Demo result:

        Detects: CREDIT_CARD

        Decision: BLOCK

        Cannot send to vector DB

        Security/compliance moment in the demo

    04_hr_report.txt → “We can detect internal identifiers too”

        Demo result:

        Detects: PERSON, EMAIL, PHONE, LOCATION

        (Adding the custom entity: INTERNAL_ID)

        Decision: REDACT

        Great moment to show custom entity detection

    05_merchant_onboarding.txt → “Even test data gets caught”

        Demo result:

        Looks like a “normal RAG doc”

        But contains a test card number

        Decision: BLOCK

        Perfect example of why guardrails matter

# Tuning the Score
Score	    Meaning	            When to Use
0.5–0.7	    Low confidence	    Experimental patterns
0.7–0.85	Medium	            Emails, names
0.85–0.95	High	            Internal IDs, PCI

# Business Value
Four major benefits:

1. Regulatory compliance — PCI, GDPR, and internal policies enforced automatically
2. Risk reduction — Sensitive data never reaches embeddings or LLMs
3. Auditability — Every decision is logged and explainable
4. Scalability — This works for any data source feeding into AI

# Potential Competitors

- Open Source: OpenMetaData, NeMo (Might be MTP), HawkEye, 
- Commercial&Enterprise Grade: Strac, AWS Macie, Nightfall AI, Protecto
- Broader Data Protection Platforms: Microsoft Purview (DLP & Classification), Forcepoint & Symantec (Broadcom) DLP, Google Cloud DLP


# Q&A
Performance:
-Presidio runs as a stateless service and can be horizontally scaled. It only processes documents at ingestion time, not at query time.

Customization:
-We can add recognizers for internal formats, account numbers, merchant IDs, or proprietary data patterns.

Audit & Logs:
-Every scan produces a structured risk report that can be exported to SIEM or compliance systems.
