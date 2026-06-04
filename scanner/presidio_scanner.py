from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# ---- Custom Internal ID Recognizer ----
pattern = Pattern(
    name="Internal ID Pattern",
    regex=r"\d{6}",
    score=0.85
)

recognizer = PatternRecognizer(
    supported_entity="INTERNAL_ID",
    patterns=[pattern]
)

analyzer.registry.add_recognizer(recognizer)

# ---- Entities to Scan ----
ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "LOCATION",
    "IBAN_CODE",
    "INTERNAL_ID"  #  Custom entity added
]

def scan_text(text):
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=ENTITIES
    )
    return results

def redact_text(text, results):
    return anonymizer.anonymize(
        text=text,
        analyzer_results=results
    ).text

def build_risk_report(results):
    report = {}
    for r in results:
        report.setdefault(r.entity_type, 0)
        report[r.entity_type] += 1
    return report
