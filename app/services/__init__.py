"""services package — provides domain, cryptographic, AI, and utility services for Swasthya Setu."""

from .anonymizer import (
    anonymize_value,
    get_anonymized_count,
    query_anonymized_stats,
    get_filter_options,
    get_summary_metrics,
    INSUFFICIENT_DATA_SENTINEL,
)
from .otp_service import (
    generate_and_send_otp,
    verify_otp,
    validate_access_token,
    revoke_token,
)
from .qr_service import (
    lookup_patient_by_card,
    generate_card_id,
    generate_qr_code,
    issue_patient_card,
    get_all_patient_cards,
)
from .card_image_service import generate_digital_health_card_image
from .drug_reference import (
    lookup_drug,
    correct_drug_name,
    check_conflicts,
    get_all_drug_names,
)
from .email_service import (
    send_staff_approval_email,
    send_staff_rejection_email,
    send_patient_approval_email,
    send_patient_rejection_email,
    send_otp_email,
)
from .ai_service import (
    get_summary,
    invalidate_summary,
    parse_voice_prescription,
    detect_trends,
    predict_all_trends,
    generate_ai_epidemiological_intelligence,
)

__all__ = [
    "anonymize_value",
    "get_anonymized_count",
    "query_anonymized_stats",
    "get_filter_options",
    "get_summary_metrics",
    "INSUFFICIENT_DATA_SENTINEL",
    "generate_and_send_otp",
    "verify_otp",
    "validate_access_token",
    "revoke_token",
    "lookup_patient_by_card",
    "generate_card_id",
    "generate_qr_code",
    "issue_patient_card",
    "get_all_patient_cards",
    "generate_digital_health_card_image",
    "lookup_drug",
    "correct_drug_name",
    "check_conflicts",
    "get_all_drug_names",
    "send_staff_approval_email",
    "send_staff_rejection_email",
    "send_patient_approval_email",
    "send_patient_rejection_email",
    "send_otp_email",
    "get_summary",
    "invalidate_summary",
    "parse_voice_prescription",
    "detect_trends",
    "predict_all_trends",
    "generate_ai_epidemiological_intelligence",
]
