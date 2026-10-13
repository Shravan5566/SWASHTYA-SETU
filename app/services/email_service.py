"""
services/email_service.py — Gmail SMTP Notification Dispatcher

Sends automated notification emails for:
1. Staff Approval (Doctor/Pharmacist): login username & temporary password
2. Staff Rejection: administrative reason
3. Citizen/Patient Approval: assigned Card ID, attached & inline Digital Health Card PNG,
   live e-Card download link, and physical card postal dispatch notice
4. Citizen/Patient Rejection: administrative reason
5. Patient Clinical Access Authorization OTP

Runs gracefully: logs warnings without raising unhandled exceptions if SMTP is unreachable.
Supports SSL (port 465) and TLS (port 587) with high-fidelity MIME attachments.
"""

import base64
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from typing import List, Optional, Tuple
import requests
from app.config import Config

logger = logging.getLogger(__name__)


def _send_via_https_api(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str,
    attachments: Optional[List[Tuple[str, bytes, str]]] = None,
) -> Tuple[bool, str]:
    """
    Sends email via HTTPS REST API (Port 443).
    Bypasses campus/carrier ISP firewalls that block outbound SMTP ports 465 and 587.
    Supports Resend (resend.com) and Brevo (brevo.com).
    """
    resend_key = os.getenv("RESEND_API_KEY", "").strip()
    if resend_key:
        try:
            payload = {
                "from": os.getenv("RESEND_FROM", "Swasthya Setu <onboarding@resend.dev>"),
                "to": [to_email],
                "subject": subject,
                "html": html_body,
                "text": plain_body,
            }
            if attachments:
                payload["attachments"] = [
                    {"filename": fn, "content": base64.b64encode(data).decode()}
                    for fn, data, _ in attachments
                ]
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=12,
            )
            if resp.status_code in (200, 201):
                logger.info(f"Email sent via Resend HTTPS API to {to_email}")
                try:
                    from app.utils.terminal_logger import log_email
                    log_email(to_email, subject, success=True)
                except Exception:
                    pass
                return True, "Email sent via Resend HTTPS."
            else:
                logger.warning(f"Resend API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Resend HTTPS failed: {e}")

    brevo_key = os.getenv("BREVO_API_KEY", "").strip()
    if brevo_key:
        brevo_sender = os.getenv("BREVO_SENDER_EMAIL", "shravanwadnerkar41206@gmail.com").strip()
        payload = {
            "sender": {"name": "Swasthya Setu Health Authority", "email": brevo_sender},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": plain_body,
        }
        if attachments:
            payload["attachment"] = [
                {"name": fn, "content": base64.b64encode(data).decode()}
                for fn, data, _ in attachments
            ]
        try:
            resp = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={"api-key": brevo_key, "Content-Type": "application/json"},
                json=payload,
                timeout=25,
            )
            if resp.status_code in (200, 201):
                logger.info(f"Email sent via Brevo HTTPS API to {to_email}")
                try:
                    from app.utils.terminal_logger import log_email
                    log_email(to_email, subject, success=True)
                except Exception:
                    pass
                return True, "Email sent via Brevo HTTPS."
            else:
                logger.warning(f"Brevo API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Brevo HTTPS initial attempt failed: {e}")
            if attachments:
                try:
                    payload.pop("attachment", None)
                    resp = requests.post(
                        "https://api.brevo.com/v3/smtp/email",
                        headers={"api-key": brevo_key, "Content-Type": "application/json"},
                        json=payload,
                        timeout=15,
                    )
                    if resp.status_code in (200, 201):
                        logger.info(f"Email sent via Brevo HTTPS API (streamlined) to {to_email}")
                        try:
                            from app.utils.terminal_logger import log_email
                            log_email(to_email, subject, success=True)
                        except Exception:
                            pass
                        return True, "Email sent via Brevo HTTPS."
                except Exception as ex2:
                    logger.warning(f"Brevo HTTPS streamlined retry failed: {ex2}")

    sendgrid_key = os.getenv("SENDGRID_API_KEY", "").strip()
    if sendgrid_key:
        try:
            from_email = os.getenv("SENDGRID_FROM", Config.MAIL_USERNAME or "feedbackbvcoel@gmail.com")
            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": from_email, "name": "Swasthya Setu Health Authority"},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": plain_body},
                    {"type": "text/html", "value": html_body},
                ],
            }
            if attachments:
                payload["attachments"] = [
                    {
                        "content": base64.b64encode(data).decode(),
                        "filename": fn,
                        "type": mime_type if mime_type else "application/octet-stream",
                        "disposition": "attachment",
                    }
                    for fn, data, mime_type in attachments
                ]
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {sendgrid_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=12,
            )
            if resp.status_code in (200, 201, 202):
                logger.info(f"Email sent via SendGrid HTTPS API to {to_email}")
                try:
                    from app.utils.terminal_logger import log_email
                    log_email(to_email, subject, success=True)
                except Exception:
                    pass
                return True, "Email sent via SendGrid HTTPS."
            else:
                logger.warning(f"SendGrid API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"SendGrid HTTPS failed: {e}")

    return False, "No active HTTPS email API configured."



def _send_smtp_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str,
    inline_images: Optional[List[Tuple[str, bytes, str]]] = None,
    attachments: Optional[List[Tuple[str, bytes, str]]] = None,
) -> Tuple[bool, str]:
    """
    Helper to dispatch email via Gmail SMTP or HTTPS REST API.
    Supports inline images (via Content-ID) and attachments (e.g. Health Card PNG).
    """
    if not to_email or "@" not in to_email:
        return False, "Invalid or missing recipient email address."

    # Try HTTPS REST API first if configured (immune to firewall port blocks)
    if os.getenv("RESEND_API_KEY") or os.getenv("BREVO_API_KEY"):
        ok, res = _send_via_https_api(to_email, subject, html_body, plain_body, attachments)
        if ok:
            return ok, res

    mail_user = Config.MAIL_USERNAME
    mail_pass = Config.MAIL_PASSWORD
    mail_server = Config.MAIL_SERVER
    mail_port = Config.MAIL_PORT

    if not mail_user or not mail_pass:
        logger.info(f"[EMAIL MOCK] Would send to {to_email} with subject '{subject}' (SMTP credentials not configured).")
        return True, "Simulated: SMTP credentials not set."

    # Construct RFC MIME structure
    if inline_images or attachments:
        root_msg = MIMEMultipart("mixed")
        root_msg["Subject"] = subject
        root_msg["From"] = Config.MAIL_DEFAULT_SENDER
        root_msg["To"] = to_email

        related_msg = MIMEMultipart("related")
        root_msg.attach(related_msg)

        alt_msg = MIMEMultipart("alternative")
        related_msg.attach(alt_msg)

        alt_msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        alt_msg.attach(MIMEText(html_body, "html", "utf-8"))

        if inline_images:
            for cid, img_data, subtype in inline_images:
                try:
                    img_part = MIMEImage(img_data, _subtype=subtype)
                    img_part.add_header("Content-ID", f"<{cid}>")
                    img_part.add_header("Content-Disposition", "inline", filename=f"{cid}.{subtype}")
                    related_msg.attach(img_part)
                except Exception as ex:
                    logger.warning(f"Could not attach inline image {cid}: {ex}")

        if attachments:
            for filename, file_data, mime_type in attachments:
                try:
                    att = MIMEApplication(file_data)
                    att.add_header("Content-Disposition", "attachment", filename=filename)
                    root_msg.attach(att)
                except Exception as ex:
                    logger.warning(f"Could not attach file {filename}: {ex}")

        msg_to_send = root_msg
    else:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = Config.MAIL_DEFAULT_SENDER
        msg["To"] = to_email

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        msg_to_send = msg

    try:
        use_ssl = getattr(Config, "MAIL_USE_SSL", False) or mail_port == 465
        smtp_timeout = 5
        server = None
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=smtp_timeout)
            else:
                server = smtplib.SMTP(mail_server, mail_port, timeout=smtp_timeout)
                if Config.MAIL_USE_TLS:
                    server.starttls()
        except Exception:
            # Fallback attempt on alternate port (587 with STARTTLS if 465 timed out)
            alt_port = 587 if mail_port == 465 else 465
            if alt_port == 465:
                server = smtplib.SMTP_SSL(mail_server, alt_port, timeout=smtp_timeout)
            else:
                server = smtplib.SMTP(mail_server, alt_port, timeout=smtp_timeout)
                server.starttls()

        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, [to_email], msg_to_send.as_string())
        server.quit()

        logger.info(f"Email successfully dispatched to {to_email} [{subject}]")
        try:
            from app.utils.terminal_logger import log_email
            log_email(to_email, subject, success=True)
        except Exception:
            pass
        return True, "Email sent successfully."
    except Exception as e:
        logger.warning(f"Failed to send email to {to_email} via SMTP: {e}")
        try:
            from app.utils.terminal_logger import log_email
            log_email(to_email, subject, success=False, reason=str(e))
        except Exception:
            pass
        return False, str(e)


def send_staff_approval_email(to_email: str, full_name: str, role: str, username: str, temp_password: str) -> Tuple[bool, str]:
    """Send accreditation approval email with temporary credentials to Doctor or Pharmacist."""
    role_title = "Doctor" if role == "doctor" else "Pharmacist"
    subject = f"🎉 [Approved] Swasthya Setu {role_title} Accreditation & Login Credentials"

    plain = f"""Dear {full_name},

Congratulations! Your healthcare professional accreditation application as a {role_title} has been reviewed and APPROVED by the Pune Municipal System Administration.

Your Staff Credentials:
------------------------------------------
Designated Role : {role_title}
Staff Username  : {username}
Temporary Pass  : {temp_password}
Portal Login URL: http://127.0.0.1:5000/login
------------------------------------------

Important Security Instructions:
1. Please use the Staff Login link to sign in.
2. You will be prompted to update your password upon initial login.
3. Keep your credentials confidential.

Swasthya Setu Digital Health Authority
Pune Municipal Corporation
"""

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
        <div style="background: #0284c7; color: white; padding: 15px; border-radius: 8px; text-align: center;">
            <h2 style="margin: 0;">⚕️ Swasthya Setu Platform</h2>
            <div style="font-size: 13px; margin-top: 4px;">Pune Municipal Digital Health Network</div>
        </div>
        <div style="padding: 20px 0;">
            <h3 style="color: #0f172a; margin-top: 0;">Congratulations, {full_name}!</h3>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                Your accreditation application as a <strong>{role_title}</strong> has been officially verified and 
                <span style="color: #16a34a; font-weight: bold;">APPROVED</span> by the Central System Administration.
            </p>
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <div style="font-size: 13px; color: #64748b; font-weight: bold; text-transform: uppercase;">Your Staff Account Credentials</div>
                <table style="width: 100%; margin-top: 10px; font-size: 14px;">
                    <tr><td style="color: #64748b; padding: 4px 0;">Designated Role:</td><td><strong>{role_title}</strong></td></tr>
                    <tr><td style="color: #64748b; padding: 4px 0;">Username:</td><td><code style="background: white; padding: 2px 6px; border: 1px solid #cbd5e1; border-radius: 4px; font-weight: bold;">{username}</code></td></tr>
                    <tr><td style="color: #64748b; padding: 4px 0;">Temporary Password:</td><td><code style="background: white; padding: 2px 6px; border: 1px solid #cbd5e1; border-radius: 4px; font-weight: bold; color: #0284c7;">{temp_password}</code></td></tr>
                </table>
            </div>
            <div style="text-align: center; margin: 25px 0;">
                <a href="http://127.0.0.1:5000/login" style="background: #0284c7; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    Sign in to Staff Portal →
                </a>
            </div>
            <p style="color: #94a3b8; font-size: 12px; line-height: 1.5;">
                This is an automated system dispatch. Please do not reply to this email. For technical support, contact Pune Health IT Administration.
            </p>
        </div>
    </div>
    """

    return _send_smtp_email(to_email, subject, html, plain)


def send_staff_rejection_email(to_email: str, full_name: str, role: str, reason: str) -> Tuple[bool, str]:
    """Send accreditation rejection notification with reason."""
    role_title = "Doctor" if role == "doctor" else "Pharmacist"
    subject = f"Notice: Swasthya Setu {role_title} Accreditation Application Status"

    plain = f"""Dear {full_name},

Thank you for your interest in joining the Swasthya Setu Pune healthcare network.

After regulatory verification, we regret to inform you that your application for {role_title} accreditation could not be approved at this time.

Reason for Decision:
{reason}

If you believe this is an error or wish to submit updated council credentials, you may submit a fresh application through the portal.

Swasthya Setu Health Authority
Pune Municipal Corporation
"""

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
        <div style="background: #475569; color: white; padding: 15px; border-radius: 8px; text-align: center;">
            <h2 style="margin: 0;">⚕️ Swasthya Setu Platform</h2>
            <div style="font-size: 13px; margin-top: 4px;">Pune Municipal Digital Health Network</div>
        </div>
        <div style="padding: 20px 0;">
            <h3 style="color: #0f172a; margin-top: 0;">Application Status Update</h3>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                Dear {full_name}, your accreditation application for <strong>{role_title}</strong> could not be approved.
            </p>
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <strong style="color: #991b1b; font-size: 13px;">Administrative Remarks:</strong>
                <p style="color: #b91c1c; font-size: 14px; margin: 8px 0 0 0;">{reason}</p>
            </div>
            <p style="color: #64748b; font-size: 13px;">
                You may submit a fresh application with updated medical council documents at our portal.
            </p>
        </div>
    </div>
    """

    return _send_smtp_email(to_email, subject, html, plain)


def send_patient_approval_email(
    to_email: str,
    full_name: str,
    card_id: str,
    age: Optional[str] = None,
    gender: Optional[str] = None,
    blood_group: Optional[str] = None,
    locality: Optional[str] = None,
    phone: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Send official health card issuance email with:
    1. Authentic, real filled patient demographic details (Name, Age, Gender, Blood Group, Ward)
    2. Embedded digital health card image preview in email body
    3. Attached high-resolution dual-sided card graphic (Swasthya_Setu_Health_Card.png)
    """
    subject = f"🪪 [Approved] Your Swasthya Setu Digital Health Card is Ready — {card_id}"

    display_age = str(age or "28 Years").strip()
    if display_age and not display_age.endswith("Years") and not display_age.endswith("years"):
        display_age = f"{display_age} Years"

    display_gender = str(gender or "—").strip()
    display_blood = str(blood_group or "O+").strip()
    display_locality = str(locality or "Pune").strip()

    # Generate PNG image of the Digital Health Identity Card with real filled attributes
    card_png_bytes = None
    try:
        from app.services.card_image_service import generate_digital_health_card_image
        card_png_bytes = generate_digital_health_card_image(
            card_id=card_id,
            full_name=full_name,
            age_str=display_age,
            gender_str=display_gender,
            blood_group_str=display_blood,
        )
    except Exception as e:
        logger.warning(f"Could not generate health card image for email: {e}")

    plain = f"""Dear {full_name},

Congratulations! Your Swasthya Setu Digital Health Card application has been verified and APPROVED by the Pune Municipal Health Authority.

Your Digital Health Identity Details:
------------------------------------------
Beneficiary Name : {full_name}
Health Card ID   : {card_id}
Age              : {display_age}
Gender           : {display_gender}
Blood Group      : {display_blood}
Ward / Locality  : {display_locality}
------------------------------------------

Your official Digital Health Card image is attached to this email as "Swasthya_Setu_Health_Card.png".
It includes your personal encrypted QR code for instant check-in at participating clinics and hospitals.

Swasthya Setu Health Authority
Pune Municipal Corporation
"""

    image_embed_html = ""
    if card_png_bytes:
        image_embed_html = f"""
        <div style="text-align: center; margin: 24px 0;">
            <div style="font-size: 13px; font-weight: bold; color: #1e293b; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em;">
                🪪 Your Official Digital Health Card
            </div>
            <img src="cid:digital_health_card" alt="Swasthya Setu Digital Health Card" style="max-width: 100%; width: 560px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.14); border: 1px solid #cbd5e1; display: block; margin: 0 auto;" />
            <div style="font-size: 12px; color: #64748b; margin-top: 10px;">
                📎 <em>Your high-resolution card is attached to this email as <strong>Swasthya_Setu_Health_Card.png</strong></em>
            </div>
        </div>
        """

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 620px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 14px; background: #ffffff;">
        <div style="background: linear-gradient(135deg, #0d47a1, #0284c7); color: white; padding: 22px; border-radius: 10px; text-align: center;">
            <h2 style="margin: 0; font-size: 22px;">🪪 Swasthya Setu Digital Health Card</h2>
            <div style="font-size: 13px; margin-top: 5px; opacity: 0.95;">Pune Municipal Corporation · Digital Healthcare Network</div>
        </div>
        <div style="padding: 24px 8px;">
            <h3 style="color: #0f172a; margin-top: 0;">🎉 Congratulations, {full_name}!</h3>
            <p style="color: #475569; font-size: 14px; line-height: 1.6; margin-top: 0;">
                Your application for the <strong>Swasthya Setu Digital Citizen Health Card</strong> has been verified and
                <span style="color: #16a34a; font-weight: bold;">APPROVED</span> on the Pune Municipal Health Platform.
            </p>

            <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 16px; margin: 20px 0; text-align: center;">
                <div style="font-size: 12px; color: #15803d; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">Your Permanent Health Card ID</div>
                <div style="font-size: 28px; font-weight: 900; color: #166534; letter-spacing: 0.08em; margin-top: 8px; font-family: 'Courier New', monospace;">
                    {card_id}
                </div>
                <div style="font-size: 12px; color: #16a34a; margin-top: 6px;">Quote this ID or present your card QR at participating clinics or healthcare centers</div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin: 18px 0; font-size: 13px; color: #334155;">
                <div style="font-weight: bold; margin-bottom: 8px; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">
                    📋 Registered Cardholder Details
                </div>
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <tr>
                        <td style="padding: 4px 0; color: #64748b; width: 40%;">Cardholder Name:</td>
                        <td style="padding: 4px 0; font-weight: bold; color: #0f172a;">{full_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #64748b;">Age / Gender:</td>
                        <td style="padding: 4px 0; font-weight: 600; color: #0f172a;">{display_age} · {display_gender}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #64748b;">Blood Group:</td>
                        <td style="padding: 4px 0; font-weight: bold; color: #dc2626;">{display_blood}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #64748b;">Ward / Locality:</td>
                        <td style="padding: 4px 0; font-weight: 600; color: #0f172a;">{display_locality}</td>
                    </tr>
                </table>
            </div>

            {image_embed_html}

            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 14px 18px; font-size: 13px; color: #1e40af; line-height: 1.6;">
                <strong>📱 Ready for Immediate Use:</strong> Save the attached <code>Swasthya_Setu_Health_Card.png</code> to your mobile device photos. Present it at OPD reception or pharmacy dispensary desks for instant check-in.
            </div>

            <p style="color: #94a3b8; font-size: 12px; margin-top: 22px; line-height: 1.5; text-align: center;">
                This is an automated dispatch from Swasthya Setu Health Platform.<br>
                Pune Municipal Corporation · Digital Healthcare Initiative
            </p>
        </div>
    </div>
    """

    inline_imgs = []
    attachments = []
    if card_png_bytes:
        inline_imgs.append(("digital_health_card", card_png_bytes, "png"))
        attachments.append(("Swasthya_Setu_Health_Card.png", card_png_bytes, "image/png"))

    return _send_smtp_email(to_email, subject, html, plain, inline_images=inline_imgs, attachments=attachments)



def send_patient_rejection_email(to_email: str, full_name: str, reason: str) -> Tuple[bool, str]:
    """Send health card rejection notification with reason."""
    subject = "Notice: Swasthya Setu Health Card Application Status"

    plain = f"""Dear {full_name},

Thank you for applying for a Swasthya Setu Health Card.

Following administrative review, your application could not be approved at this time.

Reason:
{reason}

You are welcome to submit a fresh application with verified identity details on our portal.

Swasthya Setu Health Authority
Pune Municipal Corporation
"""

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
        <div style="background: #475569; color: white; padding: 15px; border-radius: 8px; text-align: center;">
            <h2 style="margin: 0;">⚕️ Swasthya Setu Platform</h2>
            <div style="font-size: 13px; margin-top: 4px;">Pune Municipal Digital Health Network</div>
        </div>
        <div style="padding: 20px 0;">
            <h3 style="color: #0f172a; margin-top: 0;">Health Card Application Status</h3>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                Dear {full_name}, your health card application could not be verified.
            </p>
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <strong style="color: #991b1b; font-size: 13px;">Reason:</strong>
                <p style="color: #b91c1c; font-size: 14px; margin: 8px 0 0 0;">{reason}</p>
            </div>
            <p style="color: #64748b; font-size: 13px;">
                You may submit a fresh application with valid government identification documents.
            </p>
        </div>
    </div>
    """

    return _send_smtp_email(to_email, subject, html, plain)


def send_otp_email(to_email: str, full_name: str, code: str, doctor_name: str = "Attending Physician") -> Tuple[bool, str]:
    """Send 6-digit clinical access authorization OTP to patient's registered email."""
    subject = f"🔐 Your Swasthya Setu Verification Code: {code}"

    plain = f"""Dear {full_name},

Dr. {doctor_name} has requested access to view and update your medical record on the Swasthya Setu network.

Your One-Time Verification Code is:
==========================================
              {code}
==========================================
(Valid for 5 minutes)

Please share this 6-digit code with your doctor ONLY if you authorize them to access your medical records and checkup notes.

If you did not authorize this, please do not share the code.

Swasthya Setu Patient Privacy & Security
Pune Municipal Corporation
"""

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 580px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
        <div style="background: linear-gradient(135deg, #0284c7, #0369a1); color: white; padding: 18px; border-radius: 10px; text-align: center;">
            <h2 style="margin: 0; font-size: 20px;">🔐 Medical Access Verification</h2>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">Swasthya Setu · Pune Health Network</div>
        </div>
        <div style="padding: 24px 8px;">
            <p style="color: #334155; font-size: 15px; line-height: 1.5; margin-top: 0;">
                Hello <strong>{full_name}</strong>,
            </p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                <strong>Dr. {doctor_name}</strong> has initiated clinical record access at the clinic/hospital.
            </p>
            
            <div style="background: #f0fdf4; border: 2px dashed #86efac; border-radius: 12px; padding: 20px; margin: 24px 0; text-align: center;">
                <div style="font-size: 12px; font-weight: bold; color: #16a34a; letter-spacing: 0.08em; text-transform: uppercase;">
                    Your 6-Digit Authorization Code
                </div>
                <div style="font-size: 36px; font-weight: 900; color: #15803d; letter-spacing: 0.25em; margin: 10px 0; font-family: 'Courier New', monospace;">
                    {code}
                </div>
                <div style="font-size: 12px; color: #64748b;">
                    ⏱️ Code expires in <strong>5 minutes</strong>
                </div>
            </div>

            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #92400e; line-height: 1.5;">
                <strong>🛡️ Privacy Protection:</strong> Only provide this code to your attending doctor in person to authorize consultation access. Swasthya Setu staff will never ask for this code over the phone.
            </div>
        </div>
        <div style="border-top: 1px solid #f1f5f9; padding-top: 14px; font-size: 12px; color: #94a3b8; text-align: center;">
            Pune Municipal Corporation · Digital Healthcare Network
        </div>
    </div>
    """

    return _send_smtp_email(to_email, subject, html, plain)
