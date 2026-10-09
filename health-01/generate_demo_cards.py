import os
import qrcode
from PIL import Image, ImageDraw

cards = [
    ("SS-TEST-001", "Meera Joshi", "+919876543210", "Flu / Hypertension"),
    ("SS-TEST-002", "Arjun Sharma", "+919876543211", "Viral Fever / Diabetes"),
    ("SS-TEST-003", "Priya Sen", "+919876543212", "Dengue / Dehydration"),
]

output_dir = os.path.join(os.path.dirname(__file__), "demo_qr_cards")
os.makedirs(output_dir, exist_ok=True)

desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop", "demo_qr_cards")
os.makedirs(desktop_dir, exist_ok=True)

for card_id, name, phone, condition in cards:
    # 1. Generate Pure Full-Screen QR code with huge contrast (easiest for webcams to read)
    qr_big = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=18,
        border=4
    )
    qr_big.add_data(card_id)
    qr_big.make(fit=True)
    pure_img = qr_big.make_image(fill_color="black", back_color="white").convert("RGB")
    
    pure_name = f"{card_id}_BIG_QR_FOR_WEBCAM.png"
    pure_img.save(os.path.join(output_dir, pure_name))
    pure_img.save(os.path.join(desktop_dir, pure_name))

    # 2. Generate Patient Card format
    qr = qrcode.QRCode(box_size=10, border=3)
    qr.add_data(card_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0f172a", back_color="white").convert("RGB")
    
    w, h = 480, 560
    card = Image.new("RGB", (w, h), color="#f8fafc")
    draw = ImageDraw.Draw(card)
    
    # Header banner
    draw.rectangle([(0, 0), (w, 85)], fill="#0284c7")
    draw.text((25, 20), "SWASTHYA SETU", fill="white")
    draw.text((25, 48), "Pune Municipal Digital Health Card", fill="#e0f2fe")
    
    # Paste QR in center
    qr_w, qr_h = qr_img.size
    card.paste(qr_img, ((w - qr_w) // 2, 105))
    
    # Card Details Footer box
    draw.rectangle([(20, 420), (w - 20, 540)], fill="white", outline="#cbd5e1")
    draw.text((35, 432), f"Card ID : {card_id}", fill="#0f172a")
    draw.text((35, 458), f"Name    : {name}", fill="#334155")
    draw.text((35, 484), f"Phone   : {phone}", fill="#334155")
    draw.text((35, 510), f"Record  : {condition}", fill="#64748b")
    
    fname = f"{card_id}_{name.replace(' ', '_')}.png"
    card.save(os.path.join(output_dir, fname))
    card.save(os.path.join(desktop_dir, fname))
    print(f"Generated {card_id} -> {pure_name} and {fname}")
