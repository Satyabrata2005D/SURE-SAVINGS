"""
SURE SAVINGS: Institutional Email OTP Authentication Service
Sends cryptographic 6-digit verification codes using Gmail SMTP.
Gracefully handles network-restricted development environments.
"""

import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("sure_savings.email")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "SURE SAVINGS")


class EmailService:
    """
    Delivers secure authentication codes via Gmail SMTP.
    """

    @classmethod
    def send_otp(cls, to_email: str, otp_code: str) -> Tuple[bool, Optional[str]]:
        """
        Sends a 6-digit OTP code to the recipient email.
        Returns (success: bool, error_message: Optional[str]).
        """
        load_dotenv(override=True)
        smtp_user = os.getenv("SMTP_USER", "").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_from_name = os.getenv("SMTP_FROM_NAME", "SURE SAVINGS").strip()

        if not smtp_user or not smtp_password:
            logger.warning("SMTP credentials not configured. Skipping live email transmission.")
            return False, "SMTP credentials missing in .env"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{otp_code} is your SURE SAVINGS verification code"
        msg["From"] = f'"{smtp_from_name}" <{smtp_user}>'
        msg["To"] = to_email

        # Plaintext Fallback
        text_content = (
            f"Your SURE SAVINGS verification code is: {otp_code}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you did not request this code, please ignore this email.\n\n"
            f"SURE SAVINGS — Build a financial buffer before life tests it."
        )

        # High-End Branded HTML Email
        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SURE SAVINGS Verification Code</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F7F6F2; color: #111827;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F7F6F2; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="100%" max-width="520" border="0" cellspacing="0" cellpadding="0" style="max-width: 520px; background-color: #FFFFFF; border-radius: 24px; border: 1px solid #EDEAE3; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.04);">
          
          <!-- Header -->
          <tr>
            <td style="padding: 32px 36px 20px; border-bottom: 1px solid #F3F1EC;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="display: inline-block; width: 32px; height: 32px; line-height: 32px; background-color: #111827; color: #FFFFFF; font-weight: 800; font-size: 16px; text-align: center; border-radius: 8px; vertical-align: middle;">S</div>
                    <span style="font-weight: 800; font-size: 16px; letter-spacing: -0.5px; color: #111827; margin-left: 10px; vertical-align: middle;">SURE SAVINGS</span>
                  </td>
                  <td align="right">
                    <span style="font-size: 11px; font-weight: 700; color: #FF5B45; text-transform: uppercase; letter-spacing: 0.5px;">Verification</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 36px 36px 28px;">
              <h1 style="margin: 0 0 12px; font-size: 22px; font-weight: 800; color: #111827; letter-spacing: -0.5px;">Confirm your email address</h1>
              <p style="margin: 0 0 28px; font-size: 14px; line-height: 1.5; color: #4B5563;">
                Use the verification code below to access your private SURE SAVINGS financial workspace:
              </p>

              <!-- OTP Code Display Card -->
              <div style="background-color: #F7F6F2; border: 1px solid #E5E1D8; border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 28px;">
                <span style="font-family: 'Courier New', Courier, monospace; font-size: 38px; font-weight: 800; letter-spacing: 8px; color: #111827; display: inline-block;">
                  {otp_code}
                </span>
                <div style="margin-top: 8px; font-size: 12px; font-weight: 600; color: #6B7280;">
                  Valid for 10 minutes • Single use only
                </div>
              </div>

              <!-- Security Notice -->
              <p style="margin: 0 0 8px; font-size: 12px; line-height: 1.5; color: #6B7280;">
                🔒 If you did not request this verification code, you can safely ignore this email. Someone may have mistyped their email address.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 36px 28px; background-color: #FAF9F6; border-top: 1px solid #F3F1EC; text-align: center;">
              <p style="margin: 0 0 4px; font-size: 11px; font-weight: 600; color: #9CA3AF;">
                SURE SAVINGS • Build a financial buffer before life tests it.
              </p>
              <p style="margin: 0; font-size: 11px; color: #9CA3AF;">
                Automated Income Intelligence &amp; Multi-Tenant Resilience Platform
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Attempt port 587 STARTTLS with quick timeout
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=3) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                logger.info(f"Successfully sent OTP to {to_email} via SMTP 587")
                return True, None
        except Exception as err587:
            logger.warning(f"SMTP 587 failed ({err587}). Attempting SMTP 465 SSL...")
            # Attempt port 465 SSL fallback with quick timeout
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_host, 465, context=context, timeout=3) as server:
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                    logger.info(f"Successfully sent OTP to {to_email} via SMTP 465")
                    return True, None
            except Exception as err465:
                logger.error(f"SMTP live delivery timed out/failed on both ports (587: {err587}, 465: {err465}).")
                return False, f"Outbound SMTP network blocked: {err587}"
