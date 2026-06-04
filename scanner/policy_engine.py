STRICT_MODE = True  # True = redact

def policy_decision(report): # Aligning Detection and Enforcement 
    if report.get("CREDIT_CARD", 0) > 0:
        return "BLOCK"
    if report.get("IBAN_CODE", 0) > 0:
        return "BLOCK"
    if report.get("INTERNAL_ID", 0) > 0:
        return "REDACT"

    person_count = report.get("PERSON", 0)
    location_count = report.get("LOCATION", 0)

    if STRICT_MODE: #strict GDPR-style mode — very defensible in regulated environments.
        if person_count >= 1 or location_count >= 1:
            return "REDACT"
    else:
        if person_count >= 3 or location_count >= 2:
            return "REDACT"
    return "ALLOW"


''' 1 person name in a doc
→ Could be a public contact or example
→ Low risk

3+ names
→ Looks like a customer list, HR doc, or internal report
→ Higher risk
'''

'''
How You Can Tune That Number
Threshold	            Behavior	        Good For
>=1	                    Very strict	        Regulated or legal data
>=2	                    Moderate	        Support tickets
>=3	                    Balanced	        Internal knowledge bases
>=5	                    Relaxed	            Public docs
'''
