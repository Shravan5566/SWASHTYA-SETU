# pyrefly: ignore [missing-import]
"""
AI Service Layer for Swasthya Setu.

Provides:
1. Patient History Summarizer (Gemini LLM with in-memory caching and invalidation).
2. Voice-to-Prescription Parser (Gemini LLM with regex/NLP rule-based fallback).
3. Drug Typo & Safety Corrector Integration (via services/drug_reference.py).
4. Epidemiological Outbreak Trend Detector (Rolling average + 2-sigma rule-based detection for Step 10).
"""

import json
import logging
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from app.config import GEMINI_API_KEY, AI_API_KEY
from app.services.drug_reference import correct_drug_name, check_conflicts

logger = logging.getLogger(__name__)

# Primary in-memory cache for patient clinical summaries: patient_id -> { "summary": str, "timestamp": datetime }
_SUMMARY_CACHE: Dict[int, Dict[str, Any]] = {}

# Active Gemini API endpoints
GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
]
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def get_gemini_api_key() -> str:
    """Return the active Gemini API key from environment / config."""
    return (GEMINI_API_KEY or AI_API_KEY or "").strip()


def call_gemini(prompt: str, system_instruction: Optional[str] = None, max_tokens: int = 300, temperature: float = 0.2) -> Optional[str]:
    """
    Call Google Gemini REST API.
    Returns generated string or None on failure/missing key.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        logger.info("No GEMINI_API_KEY configured; using fallback AI engine.")
        return None

    headers = {"Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    # Try model endpoints in order
    for model in GEMINI_MODELS:
        url = f"{GEMINI_API_BASE}/{model}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            else:
                logger.warning("Gemini API %s error %d: %s", model, resp.status_code, resp.text[:200])
        except Exception as e:
            logger.warning("Gemini API call failed on model %s: %s", model, e)

    return None


# ─────────────────────────────────────────────────────────────────────────────
# 1. Patient Clinical Summarizer (LLM + In-Memory Cache)
# ─────────────────────────────────────────────────────────────────────────────

def invalidate_summary(patient_id: int) -> None:
    """Invalidate cached clinical summary for a patient when new visits are logged."""
    _SUMMARY_CACHE.pop(patient_id, None)


def get_cached_summary(patient_id: int) -> Optional[str]:
    """Return cached summary if available."""
    entry = _SUMMARY_CACHE.get(patient_id)
    if entry:
        return entry.get("summary")
    return None


def _format_visits_for_llm(visits: List[Any]) -> str:
    """Format structured visit list into readable clinical notes."""
    lines = []
    # Sort visits by creation date ascending
    sorted_visits = sorted(visits, key=lambda v: getattr(v, "created_at", datetime.min))
    for idx, v in enumerate(sorted_visits, 1):
        dt_str = v.created_at.strftime("%Y-%m-%d") if getattr(v, "created_at", None) else "Unknown Date"
        notes = getattr(v, "diagnosis_notes", "") or "None"
        medicine = getattr(v, "medicine", "") or "None"
        dosage = getattr(v, "dosage", "") or ""
        restricted = " [Refill Restricted]" if getattr(v, "refill_restricted", False) else ""
        lines.append(
            f"{idx}. Date: {dt_str} | Area: {v.area} | Condition: {v.condition} | "
            f"Notes: {notes} | Rx: {medicine} {dosage}{restricted}"
        )
    return "\n".join(lines)


def _generate_fallback_summary(visits: List[Any]) -> str:
    """Deterministic, explainable clinical summary when API key is missing or offline."""
    if not visits:
        return "No prior visits recorded. First consultation on file."

    sorted_visits = sorted(visits, key=lambda v: getattr(v, "created_at", datetime.min))
    conditions = [v.condition for v in sorted_visits if getattr(v, "condition", None)]
    unique_conds = list(dict.fromkeys(conditions))
    recent = sorted_visits[-1]
    dt_str = recent.created_at.strftime("%b %d, %Y") if getattr(recent, "created_at", None) else "recently"

    cond_str = ", ".join(unique_conds[:3])
    rx_str = f"{recent.medicine} ({recent.dosage})" if getattr(recent, "medicine", None) else "Supportive care"

    summary = (
        f"Patient presented with history of {cond_str}. "
        f"Most recent consultation on {dt_str} for {recent.condition} in {recent.area}. "
        f"Active prescription: {rx_str}. "
        f"Recommended continued monitoring, adherence to current dosage regimen, and clinical review."
    )
    return summary


def get_summary(patient_id: int, visits: List[Any]) -> str:
    """
    Produce a concise plain-language clinical summary (~60 words) for doctor view.
    Checks memory cache first; regenerates and caches if not present.
    """
    cached = get_cached_summary(patient_id)
    if cached:
        return cached

    if not visits:
        summary = "No prior consultation records on file for this patient."
        _SUMMARY_CACHE[patient_id] = {"summary": summary, "timestamp": datetime.utcnow()}
        return summary

    history_text = _format_visits_for_llm(visits)
    prompt = (
        "You are an expert clinical medical assistant for Swasthya Setu. "
        "Review this patient's sequential visit history and write a short, professional, "
        "plain-language clinical summary of about 60 words. "
        "Mention chronic or recurring conditions, key medications prescribed, and recent progress.\n\n"
        f"Patient Visit History:\n{history_text}\n\n"
        "Summary:"
    )

    llm_output = call_gemini(
        prompt=prompt,
        system_instruction="You are a concise clinical documentation assistant. Output only the clinical summary in 50-70 words without bullet points or conversational pleasantries.",
        max_tokens=150,
        temperature=0.2,
    )

    if not llm_output or len(llm_output.strip()) < 10:
        llm_output = _generate_fallback_summary(visits)

    cleaned_summary = llm_output.strip()
    _SUMMARY_CACHE[patient_id] = {"summary": cleaned_summary, "timestamp": datetime.utcnow()}
    return cleaned_summary


# ─────────────────────────────────────────────────────────────────────────────
# 2. Voice-to-Prescription Parser
# ─────────────────────────────────────────────────────────────────────────────

def _rule_based_voice_parser(transcript: str) -> dict:
    """Rule-based extractor for transcription when Gemini LLM is offline."""
    t = transcript.strip()

    # Default structure
    res = {
        "area": "",
        "condition": "",
        "diagnosis_notes": t,
        "medicine": "",
        "dosage": "",
        "refill_restricted": False,
    }

    # Match Area / Ward
    area_match = re.search(r"\b(Ward\s+[A-Za-z0-9]+|Community\s+Clinic|Rural\s+Health\s+Center|OPD\s+[0-9]+|Block\s+[A-Za-z0-9]+)\b", t, re.IGNORECASE)
    if area_match:
        res["area"] = area_match.group(1).title()

    # Match common conditions
    cond_patterns = [
        r"\b(Viral Fever|Acute Bronchitis|Influenza|Hypertension|Type 2 Diabetes|Gastroenteritis|Asthma|Allergic Rhinitis|Migraine|UTI|Urinary Tract Infection|Malaria|Dengue|Pneumonia|Flu|Fever|Cough)\b"
    ]
    for cp in cond_patterns:
        m = re.search(cp, t, re.IGNORECASE)
        if m:
            res["condition"] = m.group(1).title()
            break

    # Match common dosage patterns (e.g. 500mg TDS, 10mg OD, 250mg twice daily, 1 tablet once daily, etc.)
    dosage_match = re.search(
        r"\b(\d+\s*(?:mg|ml|mcg|g)?\s*(?:OD|BD|TDS|QDS|once daily|twice daily|thrice daily|stat|SOS|daily|at night))\b",
        t,
        re.IGNORECASE
    )
    if dosage_match:
        res["dosage"] = dosage_match.group(1).strip()

    # Match refill restricted phrases
    if re.search(r"\b(refill restricted|controlled substance|no refill|do not refill|narcotic)\b", t, re.IGNORECASE):
        res["refill_restricted"] = True

    # Match medicine name using fuzzy lookup over candidate words/bigrams in transcript
    words = re.findall(r"[A-Za-z\-]+", t)
    best_candidate = None
    best_score = 0.0

    for w in words:
        if len(w) < 4:
            continue
        corr = correct_drug_name(w, threshold=75.0)
        if corr.get("match") and corr.get("score", 0) > best_score:
            best_score = corr["score"]
            best_candidate = corr["match"]

    if best_candidate:
        res["medicine"] = best_candidate
    else:
        # Fallback search for any drug in text
        for word in words:
            corr = correct_drug_name(word, threshold=70.0)
            if corr.get("match"):
                res["medicine"] = corr["match"]
                break

    return res


def parse_voice_prescription(transcript: str) -> dict:
    """
    Parse a doctor's speech-to-text transcript into structured checkup fields.
    Runs medicine extraction through drug_reference corrector.
    """
    if not transcript or not transcript.strip():
        return {
            "area": "",
            "condition": "",
            "diagnosis_notes": "",
            "medicine": "",
            "dosage": "",
            "refill_restricted": False,
            "corrections": {},
        }

    extracted = None

    prompt = (
        "Extract structured medical prescription fields from this doctor dictation into a JSON object.\n"
        "Required keys:\n"
        "- area: string (e.g. Ward A, Clinic 2, or empty string if not mentioned)\n"
        "- condition: string (e.g. Influenza, Hypertension, Acute Gastritis)\n"
        "- diagnosis_notes: string (clinical observations, symptoms, or examination findings)\n"
        "- medicine: string (prescribed drug name, e.g. Paracetamol, Amoxicillin)\n"
        "- dosage: string (e.g. 500mg TDS, 10mg OD for 5 days)\n"
        "- refill_restricted: boolean (true if refill should be restricted or controlled, else false)\n\n"
        f"Dictation Transcript:\n\"{transcript.strip()}\"\n\n"
        "Return ONLY the valid JSON object with no markdown fences, no explanation."
    )

    llm_resp = call_gemini(
        prompt=prompt,
        system_instruction="You are a medical speech-to-text NLP parser. Extract the structured fields strictly into JSON.",
        max_tokens=250,
        temperature=0.1
    )

    if llm_resp:
        # Extract JSON from potential markdown tags
        clean_json = re.sub(r"^```(?:json)?|```$", "", llm_resp.strip(), flags=re.MULTILINE).strip()
        try:
            parsed = json.loads(clean_json)
            if isinstance(parsed, dict) and "condition" in parsed:
                extracted = parsed
        except Exception:
            pass

    if not extracted:
        extracted = _rule_based_voice_parser(transcript)

    # Validate and fuzzy-correct drug name using drug_reference
    raw_med = extracted.get("medicine", "")
    correction_info = {}
    if raw_med:
        correction_info = correct_drug_name(raw_med, threshold=70.0)
        if correction_info.get("match"):
            extracted["medicine"] = correction_info["match"]
            if correction_info.get("refill_restricted"):
                extracted["refill_restricted"] = True

    extracted["corrections"] = correction_info
    return extracted


# ─────────────────────────────────────────────────────────────────────────────
# 3. Epidemiological Outbreak Trend Detector & Predictive Spike Forecaster
# ─────────────────────────────────────────────────────────────────────────────

def forecast_disease_spike(counts: List[int]) -> Dict[str, Any]:
    """
    Predictive disease velocity and spike forecaster.
    Analyzes case momentum over recent cohorts to project spread 3 to 7 days ahead.

    Returns:
        {
            "growth_rate_pct": float,
            "forecast_3d": int,
            "forecast_7d": int,
            "is_accelerating": bool,
            "velocity_label": str,
            "projected_peak_days": int,
        }
    """
    if not counts or len(counts) < 2:
        return {
            "growth_rate_pct": 0.0,
            "forecast_3d": counts[-1] if counts else 0,
            "forecast_7d": counts[-1] if counts else 0,
            "is_accelerating": False,
            "velocity_label": "STABLE",
            "projected_peak_days": 14,
        }

    latest = counts[-1]
    previous = counts[-2]

    # Growth rate between the last two observed time windows
    delta = latest - previous
    growth_rate = (delta / max(previous, 1))

    # Weekly to daily rate approximation
    daily_rate = growth_rate / 7.0

    # Project trajectory for next 3 days and 7 days (capped realistically)
    proj_3d = max(1, int(round(latest * max(0.5, 1.0 + (daily_rate * 3)))))
    proj_7d = max(1, int(round(latest * max(0.5, 1.0 + (daily_rate * 7)))))

    is_accelerating = growth_rate > 0.25 and latest >= 5

    if growth_rate >= 0.75:
        velocity_label = "EXPONENTIAL SURGE"
        projected_peak_days = 3
    elif growth_rate >= 0.30:
        velocity_label = "HIGH SPREAD VELOCITY"
        projected_peak_days = 5
    elif growth_rate > 0.0:
        velocity_label = "MODERATE INFLUX"
        projected_peak_days = 9
    elif growth_rate < -0.15:
        velocity_label = "RECEDING / STABILIZING"
        projected_peak_days = 0
    else:
        velocity_label = "STABLE BASELINE"
        projected_peak_days = 14

    return {
        "growth_rate_pct": round(growth_rate * 100.0, 1),
        "forecast_3d": proj_3d,
        "forecast_7d": proj_7d,
        "is_accelerating": is_accelerating,
        "velocity_label": velocity_label,
        "projected_peak_days": projected_peak_days,
    }


def get_recommended_intervention(condition: str, severity: str, area: str) -> str:
    """Provides actionable municipal public health recommendations based on pathogen profile."""
    cond_lower = condition.lower()
    if any(k in cond_lower for k in ["dengue", "malaria", "chikungunya"]):
        return (
            f"Deploy PMC vector-control fogging in {area}, inspect stagnant water coolers, "
            f"and distribute abate granules. Mobilize ASHA workers for fever survey door-to-door."
        )
    elif any(k in cond_lower for k in ["flu", "cold", "cough", "respiratory", "bronchitis"]):
        return (
            f"Activate outpatient respiratory isolation tents at {area} dispensaries. "
            f"Issue public advisories on mask-wearing and ventilation in crowded transit areas."
        )
    elif any(k in cond_lower for k in ["typhoid", "cholera", "gastro", "diarrhea"]):
        return (
            f"Dispatch Pune water quality inspection teams to test residual chlorine at {area} distribution points. "
            f"Distribute ORS sachets and halogen tablets to residents."
        )
    return (
        f"Increase primary care medical staffing in {area}, verify rapid diagnostic test kits inventory, "
        f"and monitor daily syndromic admissions."
    )


def detect_outbreak_anomaly(counts: List[int]) -> Tuple[bool, float, float, str]:
    """
    Compare latest count against rolling average + 2 * standard deviation of historical counts.

    Returns:
        (is_spike, mean, threshold, reason)
    """
    if not counts or len(counts) < 2:
        return False, 0.0, 0.0, "Insufficient historical data points"

    history = counts[:-1]
    latest = counts[-1]

    n = len(history)
    mean = sum(history) / n
    variance = sum((x - mean) ** 2 for x in history) / n
    std_dev = math.sqrt(variance)

    # 2-sigma threshold (with minimum baseline margin of 2 cases to avoid small-number noise)
    threshold = mean + (2.0 * std_dev)
    if threshold < mean + 2.0:
        threshold = mean + 2.0

    is_spike = bool(latest > threshold and latest >= 3)
    reason = (
        f"Latest count {latest} exceeds 2-sigma threshold {threshold:.1f} "
        f"(historical mean: {mean:.1f}, std dev: {std_dev:.1f})"
        if is_spike else
        f"Count {latest} is within expected range (threshold {threshold:.1f})"
    )

    return is_spike, round(mean, 1), round(threshold, 1), reason


def detect_trends(stats_records: Optional[List[dict]] = None) -> List[dict]:
    """
    Given aggregated stats records [{area, condition, time_bucket, count}, ...],
    detects statistically significant outbreaks and anomalies with predictive spread forecasting.
    """
    if stats_records is None:
        # Lazy load from DB if available
        try:
            from app.models.stats import Stats
            rows = Stats.query.order_by(Stats.time_bucket.asc()).all()
            stats_records = [
                {
                    "area": r.area,
                    "condition": r.condition,
                    "time_bucket": r.time_bucket,
                    "count": r.count,
                }
                for r in rows
            ]
        except Exception:
            stats_records = []

    # Group counts by (area, condition) ordered chronologically
    grouped: Dict[Tuple[str, str], List[int]] = {}
    for r in stats_records:
        key = (r["area"], r["condition"])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(int(r["count"]))

    alerts = []
    for (area, condition), counts in grouped.items():
        if len(counts) < 2:
            continue

        is_spike, mean, threshold, reason = detect_outbreak_anomaly(counts)
        forecast = forecast_disease_spike(counts)

        # Flag alert if mathematical spike breached OR pre-outbreak accelerating rapidly
        should_alert = is_spike or (forecast["is_accelerating"] and counts[-1] >= 8)

        if should_alert:
            latest = counts[-1]
            severity = "HIGH" if (latest > threshold * 1.5 or forecast["growth_rate_pct"] >= 80.0) else "ELEVATED"
            intervention = get_recommended_intervention(condition, severity, area)

            alerts.append({
                "area": area,
                "condition": condition,
                "latest_count": latest,
                "baseline_mean": mean,
                "threshold": threshold,
                "severity": severity,
                "reason": reason,
                "growth_rate_pct": forecast["growth_rate_pct"],
                "forecast_3d": forecast["forecast_3d"],
                "forecast_7d": forecast["forecast_7d"],
                "velocity_label": forecast["velocity_label"],
                "projected_peak_days": forecast["projected_peak_days"],
                "recommended_intervention": intervention,
                "detected_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            })

    # Sort alerts by severity and excess over threshold
    alerts.sort(key=lambda a: a["latest_count"] - a["threshold"], reverse=True)
    return alerts


# ─────────────────────────────────────────────────────────────────────────────
# 5. Disease Trend Detector: Proactive 7-Day Spread Predictor
#    Covers ALL monitored conditions (not just outbreak alerts)
# ─────────────────────────────────────────────────────────────────────────────

def predict_all_trends(stats_records: Optional[List[dict]] = None) -> List[dict]:
    """
    Disease Trend Detector: Analyzes spread velocity and projects 3-day and
    7-day case counts for every (area, condition) pair being tracked.

    Unlike detect_trends() which only returns spike-breaching alerts, this
    returns ALL monitored pairs — STABLE, WATCH, ELEVATED, CRITICAL — giving
    health officers 3-7 days advance warning before an outbreak threshold is
    crossed.

    Returns a list sorted by growth_rate_pct descending so the fastest-growing
    diseases appear first.
    """
    if stats_records is None:
        try:
            from app.models.stats import Stats
            rows = Stats.query.order_by(Stats.time_bucket.asc()).all()
            stats_records = [
                {
                    "area": r.area,
                    "condition": r.condition,
                    "time_bucket": r.time_bucket,
                    "count": r.count,
                }
                for r in rows
            ]
        except Exception:
            stats_records = []

    # Group by (area, condition) in chronological order
    grouped: Dict[Tuple[str, str], List[int]] = {}
    for r in stats_records:
        key = (r["area"], r["condition"])
        grouped.setdefault(key, []).append(int(r["count"]))

    trends = []
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    for (area, condition), counts in grouped.items():
        if not counts:
            continue

        forecast = forecast_disease_spike(counts)
        if len(counts) >= 2:
            is_spike, mean, threshold, reason = detect_outbreak_anomaly(counts)
        else:
            is_spike, mean, threshold, reason = False, float(counts[0]), float(counts[0]) + 2, "Single data point"

        growth = forecast["growth_rate_pct"]

        # Classify risk level for colour-coded dashboard cards
        if is_spike or growth >= 75.0:
            risk_level, risk_color = "CRITICAL", "#dc2626"
        elif growth >= 30.0 or forecast["is_accelerating"]:
            risk_level, risk_color = "ELEVATED", "#ea580c"
        elif growth >= 10.0:
            risk_level, risk_color = "WATCH", "#ca8a04"
        elif growth < -10.0:
            risk_level, risk_color = "RECEDING", "#16a34a"
        else:
            risk_level, risk_color = "STABLE", "#0284c7"

        trends.append({
            "area": area,
            "condition": condition,
            "current_count": counts[-1],
            "previous_count": counts[-2] if len(counts) >= 2 else counts[-1],
            "historical_mean": mean,
            "spike_threshold": threshold,
            "growth_rate_pct": growth,
            "forecast_3d": forecast["forecast_3d"],
            "forecast_7d": forecast["forecast_7d"],
            "velocity_label": forecast["velocity_label"],
            "projected_peak_days": forecast["projected_peak_days"],
            "is_accelerating": forecast["is_accelerating"],
            "is_spike": is_spike,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "reason": reason,
            "recommended_intervention": (
                get_recommended_intervention(condition, risk_level, area)
                if risk_level in ("CRITICAL", "ELEVATED") else ""
            ),
            "evaluated_at": now_str,
        })

    # Fastest-growing diseases first
    trends.sort(key=lambda t: t["growth_rate_pct"], reverse=True)
    return trends
