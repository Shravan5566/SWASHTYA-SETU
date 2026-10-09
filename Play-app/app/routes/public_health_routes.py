# pyrefly: ignore [missing-import]
"""
routes/public_health_routes.py — Public Health Surveillance & Aggregates Panel

Enforces:
- @role_required('public_health_admin')
- ONLY aggregate counts rendered; zero patient identifiers (no card_id, no patient name, no visits)
- Every query passes through services/anonymizer.py to strictly enforce MIN_GROUP_SIZE privacy rules
- Outbreak trend alerts via services/ai_service.py detect_trends()
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.middleware.role_required import role_required
from app.services.anonymizer import (
    query_anonymized_stats,
    get_summary_metrics,
    get_filter_options,
    get_min_group_size,
    INSUFFICIENT_DATA_SENTINEL,
)
from app.services.ai_service import detect_trends, predict_all_trends

public_health_routes = Blueprint(
    "public_health_routes",
    __name__,
    url_prefix="/public-health"
)


@public_health_routes.route("/dashboard", methods=["GET"])
@role_required("public_health_admin")
def dashboard():
    """
    Main epidemiological surveillance dashboard.
    Renders aggregate condition counts by area and time bucket.
    Guaranteed privacy: small cohorts (< MIN_GROUP_SIZE) are masked with "Insufficient Data".
    """
    selected_area = request.args.get("area", "").strip() or None
    selected_condition = request.args.get("condition", "").strip() or None
    selected_bucket = request.args.get("time_bucket", "").strip() or None

    # Fetch anonymized stats through privacy service
    stats = query_anonymized_stats(
        area=selected_area,
        condition=selected_condition,
        time_bucket=selected_bucket
    )

    metrics = get_summary_metrics(time_bucket=selected_bucket)
    filter_options = get_filter_options()

    return render_template(
        "public_health/dashboard.html",
        stats=stats,
        metrics=metrics,
        filter_options=filter_options,
        selected_area=selected_area or "",
        selected_condition=selected_condition or "",
        selected_bucket=selected_bucket or "",
        min_group_size=get_min_group_size(),
        sentinel_text=INSUFFICIENT_DATA_SENTINEL,
    )


@public_health_routes.route("/trend-alerts", methods=["GET"])
@role_required("public_health_admin")
def trend_alerts():
    """
    Outbreak Trend Alerts page.
    Renders alerts flagged by the rolling-average + 2-sigma trend detector.
    """
    alerts = detect_trends()

    return render_template(
        "public_health/trend_alerts.html",
        alerts=alerts,
        alert_count=len(alerts),
    )


@public_health_routes.route("/api/anonymized-stats", methods=["GET"])
@role_required("public_health_admin")
def api_anonymized_stats():
    """
    JSON API endpoint for dashboard charts / maps.
    Returns strictly sanitized aggregate objects; suppressed cohorts show count: null.
    """
    selected_area = request.args.get("area", "").strip() or None
    selected_condition = request.args.get("condition", "").strip() or None
    selected_bucket = request.args.get("time_bucket", "").strip() or None

    stats = query_anonymized_stats(
        area=selected_area,
        condition=selected_condition,
        time_bucket=selected_bucket
    )

    return jsonify({
        "success": True,
        "min_group_size": get_min_group_size(),
        "total_records": len(stats),
        "data": stats
    })


@public_health_routes.route("/trend-forecast", methods=["GET"])
@role_required("public_health_admin")
def trend_forecast():
    """
    Disease Trend Detector: Shows 3-day and 7-day predictive forecasts for ALL
    monitored (area, condition) pairs — not just those already spiking.

    Allows health officers to spot rising trends (WATCH / ELEVATED) 3-7 days
    before they breach the outbreak alert threshold.
    """
    trends = predict_all_trends()

    # Counts per risk level for summary bar
    summary = {
        "CRITICAL": sum(1 for t in trends if t["risk_level"] == "CRITICAL"),
        "ELEVATED": sum(1 for t in trends if t["risk_level"] == "ELEVATED"),
        "WATCH":    sum(1 for t in trends if t["risk_level"] == "WATCH"),
        "STABLE":   sum(1 for t in trends if t["risk_level"] == "STABLE"),
        "RECEDING": sum(1 for t in trends if t["risk_level"] == "RECEDING"),
    }

    return render_template(
        "public_health/trend_forecast.html",
        trends=trends,
        summary=summary,
        total=len(trends),
    )
