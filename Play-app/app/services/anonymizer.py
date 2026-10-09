# pyrefly: ignore [missing-import]
"""
services/anonymizer.py — Privacy-Preserving Differential Anonymizer for Public Health

Per Implementation Plan Step 10:
- This is the SINGLE place the minimum-group-size rule lives.
- Given an area + condition + time_bucket, if count < MIN_GROUP_SIZE, return an
  "insufficient data" sentinel instead of the real number.
- Every stats query MUST go through this service — never query `Stats` directly from a route or template.
- NO patient-level models (Patient, Visit) or PII identifiers are ever imported or touched here.
"""

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func
from app.config import MIN_GROUP_SIZE
from app.extensions import db
from app.models.stats import Stats

# Sentinel string displayed whenever sample size is too small to protect identity
INSUFFICIENT_DATA_SENTINEL = "< 5 (Insufficient Data)"


def get_min_group_size() -> int:
    """Return configured minimum cohort size for anonymity."""
    return MIN_GROUP_SIZE


def anonymize_value(raw_count: Optional[int]) -> Dict[str, Any]:
    """
    Applies the minimum-group-size rule to a single integer count.
    If count < MIN_GROUP_SIZE, suppresses the true count and flags insufficient data.
    """
    if raw_count is None:
        return {
            "display": "—",
            "is_suppressed": False,
            "numeric": 0,
        }

    if raw_count < MIN_GROUP_SIZE:
        return {
            "display": INSUFFICIENT_DATA_SENTINEL,
            "is_suppressed": True,
            "numeric": None,  # Strictly None to prevent leakage in JSON/payloads
        }

    return {
        "display": str(raw_count),
        "is_suppressed": False,
        "numeric": raw_count,
    }


def get_anonymized_count(area: str, condition: str, time_bucket: str) -> Dict[str, Any]:
    """
    Lookup a specific aggregate count from Stats and return anonymized result.
    """
    stat_row = Stats.query.filter_by(
        area=area.strip(),
        condition=condition.strip(),
        time_bucket=time_bucket.strip()
    ).first()

    if not stat_row:
        stat_row = Stats.query.filter(
            Stats.area.ilike(f"%{area.strip()}%"),
            Stats.condition.ilike(f"%{condition.strip()}%"),
            Stats.time_bucket == time_bucket.strip()
        ).first()

    if not stat_row:
        return {
            "area": area,
            "condition": condition,
            "time_bucket": time_bucket,
            "display_count": INSUFFICIENT_DATA_SENTINEL,
            "is_suppressed": True,
            "count": None,
        }

    anon = anonymize_value(stat_row.count)
    return {
        "area": stat_row.area,
        "condition": stat_row.condition,
        "time_bucket": stat_row.time_bucket,
        "display_count": anon["display"],
        "is_suppressed": anon["is_suppressed"],
        "count": anon["numeric"],
    }


def query_anonymized_stats(
    area: Optional[str] = None,
    condition: Optional[str] = None,
    time_bucket: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Primary query interface for public health aggregate statistics.
    Filters by optional area, condition, and time_bucket.
    Applies MIN_GROUP_SIZE suppression to every row.
    """
    query = Stats.query

    if area and area.strip():
        query = query.filter(Stats.area == area.strip())
    if condition and condition.strip():
        query = query.filter(Stats.condition == condition.strip())
    if time_bucket and time_bucket.strip():
        query = query.filter(Stats.time_bucket == time_bucket.strip())

    records = query.order_by(Stats.time_bucket.desc(), Stats.area.asc(), Stats.condition.asc()).all()

    results = []
    for r in records:
        anon = anonymize_value(r.count)
        results.append({
            "id": r.id,
            "area": r.area,
            "condition": r.condition,
            "time_bucket": r.time_bucket,
            "display_count": anon["display"],
            "is_suppressed": anon["is_suppressed"],
            "count": anon["numeric"],  # Safe: None if suppressed
        })

    return results


def get_filter_options() -> Dict[str, List[str]]:
    """Return unique lists of areas, conditions, and time_buckets for UI filters."""
    areas = [r[0] for r in db.session.query(Stats.area).distinct().order_by(Stats.area).all()]
    conditions = [r[0] for r in db.session.query(Stats.condition).distinct().order_by(Stats.condition).all()]
    buckets = [r[0] for r in db.session.query(Stats.time_bucket).distinct().order_by(Stats.time_bucket.desc()).all()]
    return {
        "areas": areas,
        "conditions": conditions,
        "time_buckets": buckets,
    }


def get_summary_metrics(time_bucket: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate high-level epidemiological dashboard summary metrics.
    Only totals that meet privacy threshold are presented numerically.
    """
    all_stats = query_anonymized_stats(time_bucket=time_bucket)

    total_records = len(all_stats)
    suppressed_records = sum(1 for r in all_stats if r["is_suppressed"])
    unsuppressed_records = total_records - suppressed_records

    # Sum of reportable aggregate patients
    valid_sum = sum(r["count"] for r in all_stats if r["count"] is not None)
    anon_sum = anonymize_value(valid_sum if unsuppressed_records > 0 else 0)

    # Condition count
    unique_conditions = len({r["condition"] for r in all_stats})
    unique_areas = len({r["area"] for r in all_stats})

    return {
        "total_cohorts": total_records,
        "suppressed_cohorts": suppressed_records,
        "unsuppressed_cohorts": unsuppressed_records,
        "reportable_aggregate_patients": anon_sum["display"],
        "unique_conditions": unique_conditions,
        "unique_areas": unique_areas,
        "min_group_size": MIN_GROUP_SIZE,
    }
