"""
services/card_image_service.py — Digital Health Card PNG Graphic Generator

Generates a high-resolution, printable Digital Health Identity Card (PNG)
formatted like a Smart National Health / Voter ID Card for Swasthya Setu citizens.
Includes cardholder name, unique card identifier, security seals, and the embedded QR code.
"""

import io
import datetime
from typing import Optional
import qrcode
from PIL import Image, ImageDraw, ImageFont


def generate_digital_health_card_image(card_id: str, full_name: str, issue_date_str: Optional[str] = None) -> bytes:
    """
    Generate a complete Digital Health ID Card image as PNG bytes.
    Dimensions: 860 x 520 (standard card proportion, high-contrast, clean).
    """
    width = 860
    height = 520

    # Card background (Deep Navy / Healthcare slate)
    card = Image.new("RGB", (width, height), color=(15, 23, 42))  # #0f172a
    draw = ImageDraw.Draw(card)

    # Top Header banner (Dark Teal / Cyan accent)
    draw.rectangle([(0, 0), (width, 84)], fill=(13, 71, 161))  # PMC Blue
    draw.rectangle([(0, 80), (width, 85)], fill=(16, 185, 129))  # Emerald accent stripe

    # Header Texts
    draw.text((36, 18), "PUNE MUNICIPAL CORPORATION - HEALTH DEPARTMENT", fill=(241, 245, 249))
    draw.text((36, 44), "SWASTHYA SETU - DIGITAL CITIZEN HEALTH CARD", fill=(52, 211, 153))

    # Decorative Badge at top right
    draw.rectangle([(width - 150, 18), (width - 36, 62)], fill=(30, 58, 138), outline=(52, 211, 153), width=1)
    draw.text((width - 138, 30), "PMC VERIFIED", fill=(255, 255, 255))

    # Field 1: Cardholder Name
    draw.text((36, 110), "CARDHOLDER NAME", fill=(148, 163, 184))
    display_name = full_name.upper().strip()
    draw.text((36, 132), display_name, fill=(255, 255, 255))

    # Field 2: Health Card ID
    draw.text((36, 185), "DIGITAL HEALTH CARD ID", fill=(148, 163, 184))
    draw.text((36, 208), card_id.strip(), fill=(56, 189, 248))

    # Field 3: Issue Date & Validity
    if not issue_date_str:
        issue_date_str = datetime.date.today().strftime("%d %B %Y")
    draw.text((36, 260), "DATE OF ISSUANCE / VALIDITY", fill=(148, 163, 184))
    draw.text((36, 282), f"{issue_date_str}  -  PERMANENT (LIFETIME)", fill=(241, 245, 249))

    # Field 4: Health Authority / Network
    draw.text((36, 335), "ISSUING HEALTH JURISDICTION", fill=(148, 163, 184))
    draw.text((36, 357), "Pune Metropolitan Urban Health Network", fill=(203, 213, 225))

    # Field 5: Coverage & Status Badge
    draw.rectangle([(36, 405), (280, 442)], fill=(6, 78, 59), outline=(16, 185, 129), width=1)
    draw.text((48, 416), "STATUS: ACTIVE & ENROLLED", fill=(167, 243, 208))

    # Right side: QR Code Box
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(card_id.strip())
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    qr_img = qr_img.resize((210, 210))

    # QR Container Panel (clean white container with emerald border)
    container_x1 = width - 265
    container_y1 = 110
    container_x2 = width - 35
    container_y2 = 380

    draw.rectangle(
        [(container_x1, container_y1), (container_x2, container_y2)],
        fill=(255, 255, 255),
        outline=(16, 185, 129),
        width=3,
    )
    card.paste(qr_img, (container_x1 + 10, container_y1 + 10))

    # QR Label inside container
    draw.rectangle([(container_x1 + 10, container_y1 + 225), (container_x2 - 10, container_y2 - 8)], fill=(241, 245, 249))
    draw.text((container_x1 + 22, container_y1 + 233), "SCAN FOR CLINICAL CARE", fill=(15, 23, 42))

    # Instructions box next to QR
    draw.text((container_x1, 400), "Present this card at any PMC hospital,", fill=(148, 163, 184))
    draw.text((container_x1, 420), "clinic or empanelled pharmacy.", fill=(148, 163, 184))

    # Bottom security footer strip
    draw.rectangle([(0, height - 38), (width, height)], fill=(2, 6, 23))
    draw.text(
        (36, height - 26),
        "Official Digital Health Document | Government of Maharashtra | PMC Urban Health Mission",
        fill=(100, 116, 139),
    )

    buf = io.BytesIO()
    card.save(buf, format="PNG", quality=95)
    return buf.getvalue()
