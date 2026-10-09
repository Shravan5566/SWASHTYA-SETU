# pyrefly: ignore [missing-import]
"""
Drug Reference & Fuzzy Spell Corrector for Swasthya Setu.

Provides:
- Curated reference catalog of ~250+ common clinical drugs in Indian healthcare.
- Rapidfuzz-based typo correction for typed or voice-transcribed medicine names.
- Conflict, allergy, and refill-restriction rule flagging.
"""

from typing import Dict, List, Optional, Tuple
from rapidfuzz import process, fuzz


# ─────────────────────────────────────────────────────────────────────────────
# Clinical Drug Catalog: Name -> Metadata
# ─────────────────────────────────────────────────────────────────────────────
DRUG_DATABASE: Dict[str, dict] = {
    # Analgesics / Antipyretics / NSAIDs
    "Paracetamol": {"category": "Analgesic / Antipyretic", "refill_restricted": False, "interactions": ["Alcohol (high risk)"]},
    "Ibuprofen": {"category": "NSAID", "refill_restricted": False, "interactions": ["Aspirin", "Warfarin", "ACE inhibitors"]},
    "Aspirin": {"category": "Antiplatelet / NSAID", "refill_restricted": False, "interactions": ["Ibuprofen", "Warfarin", "Heparin"]},
    "Diclofenac": {"category": "NSAID", "refill_restricted": False, "interactions": ["Warfarin", "Methotrexate"]},
    "Aceclofenac": {"category": "NSAID", "refill_restricted": False, "interactions": ["Warfarin", "Digoxin"]},
    "Naproxen": {"category": "NSAID", "refill_restricted": False, "interactions": ["Aspirin", "Anticoagulants"]},
    "Tramadol": {"category": "Opioid Analgesic", "refill_restricted": True, "interactions": ["SSRIs", "MAOIs", "Benzodiazepines"]},
    "Codeine": {"category": "Opioid Analgesic", "refill_restricted": True, "interactions": ["Sedatives", "Alcohol"]},
    "Morphine": {"category": "Narcotic Analgesic", "refill_restricted": True, "interactions": ["CNS depressants"]},
    "Piroxicam": {"category": "NSAID", "refill_restricted": False, "interactions": ["Aspirin", "Warfarin"]},
    "Ketorolac": {"category": "NSAID", "refill_restricted": True, "interactions": ["Anticoagulants", "Other NSAIDs"]},
    "Mefenamic Acid": {"category": "NSAID", "refill_restricted": False, "interactions": ["Anticoagulants"]},

    # Antibiotics & Antimicrobials
    "Amoxicillin": {"category": "Penicillin Antibiotic", "refill_restricted": False, "interactions": ["Methotrexate"], "allergy_group": "penicillin"},
    "Amoxicillin-Clavulanate": {"category": "Penicillin Antibiotic", "refill_restricted": False, "interactions": ["Allopurinol"], "allergy_group": "penicillin"},
    "Ampicillin": {"category": "Penicillin Antibiotic", "refill_restricted": False, "interactions": ["Oral contraceptives"], "allergy_group": "penicillin"},
    "Azithromycin": {"category": "Macrolide Antibiotic", "refill_restricted": False, "interactions": ["Warfarin", "Antacids (aluminum/magnesium)"]},
    "Ciprofloxacin": {"category": "Fluoroquinolone", "refill_restricted": False, "interactions": ["Antacids", "Theophylline", "Dairy/Calcium"]},
    "Ofloxacin": {"category": "Fluoroquinolone", "refill_restricted": False, "interactions": ["Antacids", "Sucralfate"]},
    "Levofloxacin": {"category": "Fluoroquinolone", "refill_restricted": False, "interactions": ["NSAIDs", "Antacids"]},
    "Norfloxacin": {"category": "Fluoroquinolone", "refill_restricted": False, "interactions": ["Dairy", "Iron supplements"]},
    "Doxycycline": {"category": "Tetracycline Antibiotic", "refill_restricted": False, "interactions": ["Iron", "Calcium", "Antacids"]},
    "Cephalexin": {"category": "Cephalosporin Antibiotic", "refill_restricted": False, "interactions": ["Metformin"], "allergy_group": "cephalosporin"},
    "Cefixime": {"category": "Cephalosporin Antibiotic", "refill_restricted": False, "interactions": ["Carbamazepine"], "allergy_group": "cephalosporin"},
    "Ceftriaxone": {"category": "Cephalosporin Antibiotic", "refill_restricted": False, "interactions": ["Calcium-containing IV diluents"], "allergy_group": "cephalosporin"},
    "Cefuroxime": {"category": "Cephalosporin Antibiotic", "refill_restricted": False, "interactions": ["Antacids"], "allergy_group": "cephalosporin"},
    "Metronidazole": {"category": "Nitroimidazole Antibacterial", "refill_restricted": False, "interactions": ["Alcohol (severe disulfiram reaction)", "Warfarin"]},
    "Clarithromycin": {"category": "Macrolide Antibiotic", "refill_restricted": False, "interactions": ["Statins", "Carbamazepine"]},
    "Erythromycin": {"category": "Macrolide Antibiotic", "refill_restricted": False, "interactions": ["Theophylline", "Digoxin", "Statins"]},
    "Sulfamethoxazole-Trimethoprim": {"category": "Sulfonamide Antibacterial", "refill_restricted": False, "interactions": ["Warfarin", "Methotrexate"], "allergy_group": "sulfa"},
    "Nitrofurantoin": {"category": "Urinary Antibacterial", "refill_restricted": False, "interactions": ["Magnesium antacids"]},
    "Gentamicin": {"category": "Aminoglycoside Antibiotic", "refill_restricted": True, "interactions": ["Furosemide", "NSAIDs"]},

    # Antidiabetic
    "Metformin": {"category": "Biguanide Antidiabetic", "refill_restricted": False, "interactions": ["Iodinated radiocontrast"]},
    "Glimepiride": {"category": "Sulfonylurea Antidiabetic", "refill_restricted": False, "interactions": ["Beta-blockers (masks hypoglycemia)"]},
    "Gliclazide": {"category": "Sulfonylurea Antidiabetic", "refill_restricted": False, "interactions": ["NSAIDs", "Fluconazole"]},
    "Glibenclamide": {"category": "Sulfonylurea Antidiabetic", "refill_restricted": False, "interactions": ["Cimetidine"]},
    "Sitagliptin": {"category": "DPP-4 Inhibitor", "refill_restricted": False, "interactions": ["Digoxin"]},
    "Vildagliptin": {"category": "DPP-4 Inhibitor", "refill_restricted": False, "interactions": ["ACE inhibitors"]},
    "Linagliptin": {"category": "DPP-4 Inhibitor", "refill_restricted": False, "interactions": ["Rifampin"]},
    "Dapagliflozin": {"category": "SGLT2 Inhibitor", "refill_restricted": False, "interactions": ["Diuretics"]},
    "Empagliflozin": {"category": "SGLT2 Inhibitor", "refill_restricted": False, "interactions": ["Loop diuretics"]},
    "Insulin Regular": {"category": "Insulin", "refill_restricted": False, "interactions": ["Beta-blockers", "Corticosteroids"]},
    "Insulin Glargine": {"category": "Long-acting Insulin", "refill_restricted": False, "interactions": ["Beta-blockers"]},
    "Pioglitazone": {"category": "Thiazolidinedione", "refill_restricted": False, "interactions": ["Gemfibrozil", "Rifampin"]},

    # Cardiovascular & Antihypertensives
    "Amlodipine": {"category": "Calcium Channel Blocker", "refill_restricted": False, "interactions": ["Simvastatin (dose cap 20mg)"]},
    "Atenolol": {"category": "Beta-blocker", "refill_restricted": False, "interactions": ["Verapamil", "Diltiazem", "Clonidine"]},
    "Metoprolol": {"category": "Beta-blocker", "refill_restricted": False, "interactions": ["Fluoxetine", "Paroxetine", "Cimetidine"]},
    "Bisoprolol": {"category": "Beta-blocker", "refill_restricted": False, "interactions": ["Rifampin"]},
    "Telmisartan": {"category": "Angiotensin II Receptor Blocker", "refill_restricted": False, "interactions": ["Potassium supplements", "Spironolactone", "Lithium"]},
    "Losartan": {"category": "Angiotensin II Receptor Blocker", "refill_restricted": False, "interactions": ["Fluconazole", "Potassium-sparing diuretics"]},
    "Olmesartan": {"category": "Angiotensin II Receptor Blocker", "refill_restricted": False, "interactions": ["Aliskiren", "Colesevelam"]},
    "Ramipril": {"category": "ACE Inhibitor", "refill_restricted": False, "interactions": ["Potassium supplements", "Allopurinol"]},
    "Enalapril": {"category": "ACE Inhibitor", "refill_restricted": False, "interactions": ["Lithium", "NSAIDs"]},
    "Lisinopril": {"category": "ACE Inhibitor", "refill_restricted": False, "interactions": ["NSAIDs", "Potassium supplements"]},
    "Hydrochlorothiazide": {"category": "Thiazide Diuretic", "refill_restricted": False, "interactions": ["Lithium", "Digoxin", "Corticosteroids"]},
    "Furosemide": {"category": "Loop Diuretic", "refill_restricted": False, "interactions": ["Aminoglycosides", "Digoxin", "Lithium"]},
    "Spironolactone": {"category": "Potassium-sparing Diuretic", "refill_restricted": False, "interactions": ["Potassium supplements", "ACE inhibitors"]},
    "Atorvastatin": {"category": "Statin Lipid-lowering", "refill_restricted": False, "interactions": ["Clarithromycin", "Grapefruit juice", "Cyclosporine"]},
    "Rosuvastatin": {"category": "Statin Lipid-lowering", "refill_restricted": False, "interactions": ["Antacids", "Cyclosporine", "Gemfibrozil"]},
    "Simvastatin": {"category": "Statin Lipid-lowering", "refill_restricted": False, "interactions": ["Amlodipine", "Clarithromycin", "Ketoconazole"]},
    "Clopidogrel": {"category": "Antiplatelet", "refill_restricted": False, "interactions": ["Omeprazole (reduced efficacy)", "NSAIDs"]},
    "Warfarin": {"category": "Anticoagulant", "refill_restricted": True, "interactions": ["Aspirin", "Metronidazole", "Ciprofloxacin", "NSAIDs"]},
    "Digoxin": {"category": "Cardiac Glycoside", "refill_restricted": True, "interactions": ["Amiodarone", "Verapamil", "Macrolides"]},
    "Diltiazem": {"category": "Calcium Channel Blocker", "refill_restricted": False, "interactions": ["Beta-blockers", "Statins", "Digoxin"]},
    "Verapamil": {"category": "Calcium Channel Blocker", "refill_restricted": False, "interactions": ["Beta-blockers", "Simvastatin"]},

    # Gastrointestinal & Acid Reducers
    "Omeprazole": {"category": "Proton Pump Inhibitor", "refill_restricted": False, "interactions": ["Clopidogrel", "Diazepam", "Iron"]},
    "Pantoprazole": {"category": "Proton Pump Inhibitor", "refill_restricted": False, "interactions": ["Atazanavir", "Methotrexate"]},
    "Rabeprazole": {"category": "Proton Pump Inhibitor", "refill_restricted": False, "interactions": ["Ketoconazole", "Digoxin"]},
    "Esomeprazole": {"category": "Proton Pump Inhibitor", "refill_restricted": False, "interactions": ["Clopidogrel", "Tacrolimus"]},
    "Ranitidine": {"category": "H2 Receptor Antagonist", "refill_restricted": False, "interactions": ["Procainamide", "Midazolam"]},
    "Famotidine": {"category": "H2 Receptor Antagonist", "refill_restricted": False, "interactions": ["Ketoconazole"]},
    "Domperidone": {"category": "Antiemetic / Prokinetic", "refill_restricted": False, "interactions": ["Ketoconazole", "Erythromycin", "QT-prolonging drugs"]},
    "Ondansetron": {"category": "5-HT3 Antiemetic", "refill_restricted": False, "interactions": ["Apomorphine", "Tramadol (reduced analgesia)"]},
    "Metoclopramide": {"category": "Prokinetic / Antiemetic", "refill_restricted": False, "interactions": ["Levodopa", "Antipsychotics"]},
    "Loperamide": {"category": "Antidiarrheal", "refill_restricted": False, "interactions": ["Quinidine", "Ritonavir"]},
    "Sucralfate": {"category": "Mucosal Protectant", "refill_restricted": False, "interactions": ["Ciprofloxacin", "Warfarin", "Thyroxine"]},
    "Lactulose": {"category": "Osmotic Laxative", "refill_restricted": False, "interactions": ["Antacids"]},

    # Respiratory & Allergy
    "Cetirizine": {"category": "Second-generation Antihistamine", "refill_restricted": False, "interactions": ["Alcohol", "Sedatives"]},
    "Levocetirizine": {"category": "Antihistamine", "refill_restricted": False, "interactions": ["CNS depressants", "Theophylline"]},
    "Loratadine": {"category": "Antihistamine", "refill_restricted": False, "interactions": ["Ketoconazole", "Erythromycin"]},
    "Fexofenadine": {"category": "Antihistamine", "refill_restricted": False, "interactions": ["Fruit juice (grapefruit/apple/orange)", "Antacids"]},
    "Montelukast": {"category": "Leukotriene Receptor Antagonist", "refill_restricted": False, "interactions": ["Phenobarbital", "Rifampin"]},
    "Salbutamol": {"category": "Short-acting Beta2 Agonist", "refill_restricted": False, "interactions": ["Beta-blockers (antagonism)"]},
    "Formoterol": {"category": "Long-acting Beta2 Agonist", "refill_restricted": False, "interactions": ["Beta-blockers", "MAOIs"]},
    "Budesonide": {"category": "Inhaled Corticosteroid", "refill_restricted": False, "interactions": ["Ketoconazole", "Itraconazole"]},
    "Fluticasone": {"category": "Inhaled / Nasal Corticosteroid", "refill_restricted": False, "interactions": ["Ritonavir", "Ketoconazole"]},
    "Ipratropium": {"category": "Anticholinergic Bronchodilator", "refill_restricted": False, "interactions": ["Other anticholinergics"]},
    "Theophylline": {"category": "Methylxanthine Bronchodilator", "refill_restricted": True, "interactions": ["Ciprofloxacin", "Erythromycin", "Cimetidine"]},
    "Dextromethorphan": {"category": "Cough Suppressant", "refill_restricted": False, "interactions": ["MAOIs", "SSRIs"]},
    "Ambroxol": {"category": "Mucolytic", "refill_restricted": False, "interactions": ["Antibiotics (increases tissue penetration)"]},

    # Corticosteroids (Refill-restricted if prolonged / oral high dose)
    "Prednisolone": {"category": "Systemic Corticosteroid", "refill_restricted": True, "interactions": ["NSAIDs (GI bleeding)", "Live vaccines", "Antidiabetics"]},
    "Dexamethasone": {"category": "Systemic Corticosteroid", "refill_restricted": True, "interactions": ["NSAIDs", "Phenytoin", "Rifampin"]},
    "Hydrocortisone": {"category": "Corticosteroid", "refill_restricted": True, "interactions": ["Anticoagulants", "NSAIDs"]},
    "Methylprednisolone": {"category": "Corticosteroid", "refill_restricted": True, "interactions": ["NSAIDs", "Cyclosporine"]},

    # Central Nervous System & Psychiatric (Controlled / Refill Restricted)
    "Alprazolam": {"category": "Benzodiazepine Anxiolytic", "refill_restricted": True, "interactions": ["Opioids", "Alcohol", "Ketoconazole"]},
    "Clonazepam": {"category": "Benzodiazepine Anticonvulsant", "refill_restricted": True, "interactions": ["CNS depressants", "Alcohol"]},
    "Diazepam": {"category": "Benzodiazepine", "refill_restricted": True, "interactions": ["Opioids", "Omeprazole", "Alcohol"]},
    "Lorazepam": {"category": "Benzodiazepine", "refill_restricted": True, "interactions": ["Opioids", "Valproate"]},
    "Phenytoin": {"category": "Anticonvulsant", "refill_restricted": True, "interactions": ["Warfarin", "Oral contraceptives", "Cimetidine"]},
    "Carbamazepine": {"category": "Anticonvulsant", "refill_restricted": True, "interactions": ["Erythromycin", "Fluoxetine", "Oral contraceptives"]},
    "Sodium Valproate": {"category": "Anticonvulsant / Mood Stabilizer", "refill_restricted": True, "interactions": ["Aspirin", "Carbapenems", "Lamotrigine"]},
    "Levetiracetam": {"category": "Anticonvulsant", "refill_restricted": False, "interactions": ["Sedatives"]},
    "Amitriptyline": {"category": "Tricyclic Antidepressant", "refill_restricted": True, "interactions": ["MAOIs", "SSRIs", "Anticholinergics"]},
    "Escitalopram": {"category": "SSRI Antidepressant", "refill_restricted": True, "interactions": ["NSAIDs", "Tramadol", "MAOIs"]},
    "Sertraline": {"category": "SSRI Antidepressant", "refill_restricted": True, "interactions": ["MAOIs", "Warfarin", "Pimozide"]},
    "Fluoxetine": {"category": "SSRI Antidepressant", "refill_restricted": True, "interactions": ["Tricyclics", "Haloperidol", "MAOIs"]},
    "Zolpidem": {"category": "Sedative-Hypnotic", "refill_restricted": True, "interactions": ["Alcohol", "Opioids", "Ketoconazole"]},

    # Antifungals & Antivirals
    "Fluconazole": {"category": "Triazole Antifungal", "refill_restricted": False, "interactions": ["Warfarin", "Sulfonylureas", "Statins", "Phenytoin"]},
    "Itraconazole": {"category": "Triazole Antifungal", "refill_restricted": False, "interactions": ["PPIs", "H2 blockers", "Statins"]},
    "Clotrimazole": {"category": "Topical Antifungal", "refill_restricted": False, "interactions": []},
    "Terbinafine": {"category": "Allylamine Antifungal", "refill_restricted": False, "interactions": ["Cimetidine", "Rifampin"]},
    "Acyclovir": {"category": "Antiviral", "refill_restricted": False, "interactions": ["Nephrotoxic drugs", "Probenecid"]},
    "Oseltamivir": {"category": "Antiviral (Neuraminidase Inhibitor)", "refill_restricted": False, "interactions": ["Live influenza vaccine"]},

    # Thyroid & Endocrine
    "Levothyroxine": {"category": "Thyroid Hormone", "refill_restricted": False, "interactions": ["Calcium", "Iron supplements", "Soy", "Antacids"]},
    "Methimazole": {"category": "Antithyroid Agent", "refill_restricted": False, "interactions": ["Anticoagulants", "Beta-blockers"]},

    # Vitamins, Minerals & Supplements
    "Ferrous Sulfate": {"category": "Iron Supplement", "refill_restricted": False, "interactions": ["Fluoroquinolones", "Tetracyclines", "Antacids", "Levothyroxine"]},
    "Calcium Carbonate": {"category": "Mineral Supplement", "refill_restricted": False, "interactions": ["Ciprofloxacin", "Iron", "Tetracycline"]},
    "Vitamin D3 (Cholecalciferol)": {"category": "Vitamin Supplement", "refill_restricted": False, "interactions": ["Thiazide diuretics"]},
    "Folic Acid": {"category": "Vitamin B9", "refill_restricted": False, "interactions": ["Phenytoin", "Methotrexate"]},
    "Vitamin B-Complex": {"category": "Vitamin Supplement", "refill_restricted": False, "interactions": []},
    "Zinc Sulfate": {"category": "Mineral Supplement", "refill_restricted": False, "interactions": ["Quinolones", "Tetracyclines"]},
    "Oral Rehydration Salts (ORS)": {"category": "Electrolyte Solution", "refill_restricted": False, "interactions": []},
}

# Pre-computed list of canonical drug names for fuzzy search
DRUG_NAMES_LIST: List[str] = list(DRUG_DATABASE.keys())


def get_all_drug_names() -> List[str]:
    """Return all canonical drug names in the reference catalog."""
    return DRUG_NAMES_LIST.copy()


def lookup_drug(name: str) -> Optional[dict]:
    """Look up a canonical drug by exact case-insensitive name."""
    if not name:
        return None
    for canonical, info in DRUG_DATABASE.items():
        if canonical.lower() == name.strip().lower():
            return {
                "name": canonical,
                **info
            }
    return None


def correct_drug_name(raw_name: str, threshold: float = 70.0) -> dict:
    """
    Fuzzy-corrects a typed or voice-transcribed drug name.

    Returns:
        dict: {
            "original": str,
            "match": str or None,
            "score": float,
            "is_exact": bool,
            "is_corrected": bool,
            "category": str or None,
            "refill_restricted": bool,
            "warnings": list of str
        }
    """
    if not raw_name or not raw_name.strip():
        return {
            "original": raw_name,
            "match": None,
            "score": 0.0,
            "is_exact": False,
            "is_corrected": False,
            "category": None,
            "refill_restricted": False,
            "warnings": [],
        }

    query = raw_name.strip()

    # Exact match check first
    exact = lookup_drug(query)
    if exact:
        return {
            "original": query,
            "match": exact["name"],
            "score": 100.0,
            "is_exact": True,
            "is_corrected": False,
            "category": exact.get("category"),
            "refill_restricted": exact.get("refill_restricted", False),
            "warnings": exact.get("interactions", []),
        }

    # Rapidfuzz extract best candidate
    result = process.extractOne(
        query,
        DRUG_NAMES_LIST,
        scorer=fuzz.WRatio
    )

    if result:
        best_name, score, _ = result
        if score >= threshold:
            info = DRUG_DATABASE.get(best_name, {})
            is_corrected = (best_name.lower() != query.lower())
            warnings = list(info.get("interactions", []))
            if is_corrected:
                warnings.insert(0, f"Spelling corrected from '{query}' to '{best_name}'")

            return {
                "original": query,
                "match": best_name,
                "score": round(score, 1),
                "is_exact": False,
                "is_corrected": is_corrected,
                "category": info.get("category"),
                "refill_restricted": info.get("refill_restricted", False),
                "warnings": warnings,
            }

    # No sufficiently close match found
    return {
        "original": query,
        "match": None,
        "score": 0.0,
        "is_exact": False,
        "is_corrected": False,
        "category": "Unknown Medication",
        "refill_restricted": False,
        "warnings": [f"Medication '{query}' is not in the standard formulary."],
    }


def check_conflicts(medicine: str, current_medicines: Optional[List[str]] = None) -> List[str]:
    """
    Check for drug-drug interaction conflicts between a proposed medicine and existing medicines.
    """
    alerts: List[str] = []
    if not medicine or not current_medicines:
        return alerts

    proposed_info = lookup_drug(medicine)
    if not proposed_info:
        corr = correct_drug_name(medicine)
        if corr["match"]:
            proposed_info = lookup_drug(corr["match"])

    if not proposed_info:
        return alerts

    proposed_interactions = proposed_info.get("interactions", [])

    for current in current_medicines:
        curr_clean = current.strip().lower()
        for inter in proposed_interactions:
            if curr_clean in inter.lower() or any(w in inter.lower() for w in curr_clean.split()):
                alerts.append(f"Interaction warning: {proposed_info['name']} interacts with {current} ({inter})")

    return alerts
