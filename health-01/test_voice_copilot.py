from app import create_app
from app.services.ai_service import parse_voice_prescription

app = create_app()
with app.app_context():
    # Test 1: Marathi voice dictation
    marathi_input = "रुग्णाला कात्रज भागात तीव्र ताप, सांधेदुखी आणि थंडी भरून येत आहे, डेंग्यूचा संशय आहे. पॅरासिटामॉल ६५० आणि ओआरएस द्या दिवसातून तीन वेळा."
    p1 = parse_voice_prescription(marathi_input)
    print("\n--- TEST 1: MARATHI VOICE DICTATION ---")
    print("Detected Language:", p1.get("detected_language"))
    print("Condition:", p1.get("condition"))
    print("Ward:", p1.get("ward"))
    print("Medicines:", p1.get("medicines"))
    print("Dosage:", p1.get("dosage"))
    print("Notes:", p1.get("notes"))
    print("Corrections:", p1.get("corrections_made"))

    # Test 2: Hindi voice dictation with drug typo
    hindi_input = "मरीज को कोथरुड वार्ड से है, तीन दिन से मलेरिया के लक्षण हैं, तेज कपकपी और बुखार. क्लोरोक्वीन 250mg और पेरासिटामोल लिख दो दो बार खाने के बाद."
    p2 = parse_voice_prescription(hindi_input)
    print("\n--- TEST 2: HINDI VOICE DICTATION ---")
    print("Detected Language:", p2.get("detected_language"))
    print("Condition:", p2.get("condition"))
    print("Ward:", p2.get("ward"))
    print("Medicines:", p2.get("medicines"))
    print("Dosage:", p2.get("dosage"))
    print("Corrections:", p2.get("corrections_made"))

    # Test 3: English voice dictation with typos and schedule H
    english_input = "Patient presenting from Hadapsar ward with severe acute diarrhea, vomiting and dehydration. Prescribe paracetmol 650 and ors sachets, and azithro 500mg once daily. Restrict refills."
    p3 = parse_voice_prescription(english_input)
    print("\n--- TEST 3: ENGLISH VOICE DICTATION ---")
    print("Detected Language:", p3.get("detected_language"))
    print("Condition:", p3.get("condition"))
    print("Ward:", p3.get("ward"))
    print("Medicines:", p3.get("medicines"))
    print("Dosage:", p3.get("dosage"))
    print("Refill Restricted:", p3.get("refill_restricted"))
    print("Corrections:", p3.get("corrections_made"))
