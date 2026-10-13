"""
services/card_image_service.py — Digital Health Card PNG Graphic Generator

Generates high-resolution, printable Digital Health Identity Cards (PNG)
accurately adhering to the official Swasthya Setu smart card design:
- Front: NFC wave, 4 security status dots, central hands & QR-heart emblem,
         "Swasthya Setu", "SCAN • CARE • TOGETHER", "PATIENT HEALTH ID" with tricolor bar.
- Back: Framing brackets, real scannable QR code, card ID, demographic list
        (Name, Age, Gender, Blood Group), and the official security seal.
"""

import io
import os
import datetime
from typing import Optional
import qrcode
from PIL import Image, ImageDraw, ImageFont


def _find_asset_path(filename: str) -> Optional[str]:
    """Search common asset locations for card templates."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "static", filename),
        os.path.join(os.path.dirname(__file__), "..", "..", "public", filename),
        os.path.join(os.path.dirname(__file__), "..", "dist", filename),
        os.path.join("public", filename),
        os.path.join("app", "static", filename),
    ]
    for c in candidates:
        abs_c = os.path.abspath(c)
        if os.path.exists(abs_c):
            return abs_c
    return None


def generate_digital_health_card_image(
    card_id: str,
    full_name: str,
    issue_date_str: Optional[str] = None,
    age_str: str = "XX Years",
    gender_str: str = "—",
    blood_group_str: str = "O+",
    side: str = "composite",  # 'composite' (front + back), 'back', or 'front'
) -> bytes:
    """
    Generate the official Swasthya Setu Digital Health ID Card image as PNG bytes.
    Default mode 'composite' creates a side-by-side presentation of Front and Back.
    """
    back_template_path = _find_asset_path("card-back-clean-template.png")
    front_template_path = _find_asset_path("card-front-bg.png")

    # If assets exist, use the authentic template pipeline
    if back_template_path:
        try:
            back = Image.open(back_template_path).convert("RGBA")
            bw, bh = back.size

            # 1. Generate real QR code for this specific card_id
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=1,
            )
            qr.add_data(card_id.strip())
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#1e293b", back_color="#ffffff").convert("RGBA")
            qr_img = qr_img.resize((230, 230))
            back.paste(qr_img, (277, 151), qr_img)

            # 2. Draw dynamic patient attributes
            draw = ImageDraw.Draw(back)
            try:
                font_id = ImageFont.truetype("arialbd.ttf", 20)
                font_lbl = ImageFont.truetype("arial.ttf", 16)
                font_val = ImageFont.truetype("arialbd.ttf", 23)
            except Exception:
                font_id = font_lbl = font_val = ImageFont.load_default()

            clean_id = card_id.strip()
            tw = draw.textbbox((0, 0), clean_id, font=font_id)[2]
            draw.text(((bw - tw) // 2, 421), clean_id, fill=(30, 41, 59), font=font_id)

            # Patient details list (Icon on left at x~240, Label + Value aligned at x=330)
            display_name = (full_name or "Citizen Patient").strip()[:24]
            draw.text((330, 502), "Name", fill=(100, 116, 139), font=font_lbl)
            draw.text((330, 524), display_name, fill=(30, 41, 59), font=font_val)

            display_age = str(age_str or "28 Years").strip()
            draw.text((330, 574), "Age", fill=(100, 116, 139), font=font_lbl)
            draw.text((330, 596), display_age, fill=(30, 41, 59), font=font_val)

            display_gender = str(gender_str or "—").strip()
            draw.text((330, 644), "Gender", fill=(100, 116, 139), font=font_lbl)
            draw.text((330, 666), display_gender, fill=(30, 41, 59), font=font_val)

            display_blood = str(blood_group_str or "O+").strip()
            draw.text((330, 718), "Blood Group", fill=(100, 116, 139), font=font_lbl)
            draw.text((330, 740), display_blood, fill=(185, 28, 28), font=font_val)


            if side == "back":
                buf = io.BytesIO()
                back.convert("RGB").save(buf, format="PNG", quality=95)
                return buf.getvalue()

            # If front template exists and side is 'composite', create side-by-side card pair
            if front_template_path and side == "composite":
                front = Image.open(front_template_path).convert("RGBA")
                target_h = 420
                front_res = front.resize(
                    (int(front.width * target_h / front.height), target_h),
                    Image.Resampling.LANCZOS,
                )
                back_res = back.resize(
                    (int(back.width * target_h / back.height), target_h),
                    Image.Resampling.LANCZOS,
                )

                spacing = 24
                margin = 16
                comp_w = front_res.width + back_res.width + spacing + (margin * 2)
                comp_h = target_h + (margin * 2)

                comp = Image.new("RGB", (comp_w, comp_h), (248, 250, 252))
                comp.paste(front_res, (margin, margin), front_res)
                comp.paste(back_res, (margin + front_res.width + spacing, margin), back_res)

                buf = io.BytesIO()
                comp.save(buf, format="PNG", optimize=True)
                return buf.getvalue()

            buf = io.BytesIO()
            back.convert("RGB").save(buf, format="PNG", optimize=True)
            return buf.getvalue()

        except Exception as e:
            # Fallback to programmatic card if file loading encounters an issue
            pass

    # Programmatic fallback card
    width = 860
    height = 520
    card = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(card)
    draw.rectangle([(0, 0), (width, 84)], fill=(15, 23, 42))
    draw.rectangle([(0, 80), (width, 85)], fill=(16, 185, 129))
    draw.text((36, 18), "SWASTHYA SETU - PUBLIC HEALTH PLATFORM", fill=(241, 245, 249))
    draw.text((36, 44), "DIGITAL CITIZEN HEALTH IDENTITY", fill=(52, 211, 153))

    buf = io.BytesIO()
    card.save(buf, format="PNG")
    return buf.getvalue()
