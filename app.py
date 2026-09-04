import streamlit as st
from scanner.presidio_scanner import scan_text, redact_text, build_risk_report
from scanner.policy_engine import policy_decision
from rag.vector_stub import embed_and_store
from pypdf import PdfReader
import tempfile
import pandas as pd

st.set_page_config(page_title="RAG Compliance Gateway", layout="wide")

st.title("🛡️ RAG Compliance Gateway — Presidio POC")
st.markdown("Upload a document to scan for **PII / PCI** before sending it to your RAG system.")

uploaded_file = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"])

def read_file(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    else:
        return file.read().decode("utf-8")

if uploaded_file:
    text = read_file(uploaded_file)

    st.subheader("📄 Original Document")
    st.text_area("Original", text, height=250)

    if st.button("Scan Document"):
        with st.spinner("Scanning for sensitive data..."):
            results = scan_text(text)
            report = build_risk_report(results)
            decision = policy_decision(report)
        st.session_state["scan_result"] = {
            "text": text,
            "results": results,
            "report": report,
            "decision": decision,
        }

    scan_result = st.session_state.get("scan_result")
    if scan_result and scan_result["text"] == text:
        results = scan_result["results"]
        report = scan_result["report"]
        decision = scan_result["decision"]

        confidence_data = []
        for r in results:
            confidence_data.append({
                "Entity": r.entity_type,
                "Start": r.start,
                "End": r.end,
                "Confidence": round(r.score, 2),
                "Matched Text": text[r.start:r.end]
            })

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Risk Report")
            st.json(report)

            st.subheader("🔍 Detection Details")
            if confidence_data:
                st.dataframe(pd.DataFrame(confidence_data), use_container_width=True)
            else:
                st.write("No entities detected.")

            st.subheader("Policy Decision")
            if decision == "BLOCK":
                st.error("BLOCK — PCI detected")
            elif decision == "REDACT":
                st.warning("REDACT — High PII volume")
            else:
                st.success("ALLOW — Safe to ingest")

        with col2:
            st.subheader("Redacted Document")
            content_to_store = text
            if decision == "BLOCK":
                st.info("This document was blocked due to PCI data. No content is displayed or stored.")
            elif decision == "REDACT":
                PII_ENTITIES = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "INTERNAL_ID"]
                filtered_results = [r for r in results if r.entity_type in PII_ENTITIES]
                content_to_store = redact_text(text, filtered_results)
                st.text_area("Redacted", content_to_store, height=250)
            else:
                st.text_area("Approved (No Redaction Needed)", text, height=250)

        if decision != "BLOCK":
            if st.button("Send to Vector DB"):
                embed_and_store(content_to_store)
                st.success("Stored in vector DB (stub)")
