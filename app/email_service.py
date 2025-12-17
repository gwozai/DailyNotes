"""
Async email service for DailyNotes.
Uses SMTP with aiosmtplib for async email sending.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails asynchronously via SMTP.

    Supports password reset and magic link emails with HTML and plain text versions.
    """

    def __init__(self, app=None):
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.smtp_use_tls = True
        self.from_email = None
        self.from_name = "DailyNotes"
        self.app_url = "http://localhost:8000"
        self.enabled = False

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the email service with app configuration."""
        self.smtp_host = app.config.get("SMTP_HOST")
        self.smtp_port = app.config.get("SMTP_PORT", 587)
        self.smtp_user = app.config.get("SMTP_USER")
        self.smtp_password = app.config.get("SMTP_PASSWORD")
        self.smtp_use_tls = app.config.get("SMTP_USE_TLS", True)
        self.from_email = app.config.get("SMTP_FROM_EMAIL") or self.smtp_user
        self.from_name = app.config.get("SMTP_FROM_NAME", "DailyNotes")
        self.app_url = app.config.get("APP_URL", "http://localhost:8000")
        self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password)

        if self.enabled:
            logger.info(
                f"Email service configured: host={self.smtp_host}, port={self.smtp_port}, "
                f"user={self.smtp_user}, from={self.from_email}, tls={self.smtp_use_tls}"
            )
        else:
            logger.warning(
                "Email service not configured. "
                "Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD to enable email features."
            )

    @property
    def is_enabled(self):
        """Check if email service is properly configured."""
        return self.enabled

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Send an email asynchronously.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML content of the email
            text_body: Plain text fallback (optional)

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email service not configured, skipping email send")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        logger.info(f"Sending email to {to_email}: {subject}")

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=self.smtp_use_tls,
            )
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_password_reset(self, to_email: str, token: str) -> bool:
        """
        Send password reset email.

        Args:
            to_email: Recipient email address
            token: Password reset token

        Returns:
            True if email was sent successfully
        """
        reset_url = f"{self.app_url}/auth/reset-password?token={token}"

        subject = "Reset Your DailyNotes Password"
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; padding: 40px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h1 style="color: #333; margin-top: 0; margin-bottom: 24px;">Reset Your Password</h1>
        <p style="color: #555; line-height: 1.6; margin-bottom: 24px;">
            You requested to reset your DailyNotes password. Click the button below to set a new password:
        </p>
        <p style="margin: 32px 0; text-align: center;">
            <a href="{reset_url}" style="background-color: #48c774; color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 16px;">
                Reset Password
            </a>
        </p>
        <p style="color: #888; font-size: 14px; line-height: 1.5; margin-bottom: 8px;">
            This link will expire in <strong>1 hour</strong>.
        </p>
        <p style="color: #888; font-size: 14px; line-height: 1.5;">
            If you didn't request this, you can safely ignore this email. Your password will remain unchanged.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 32px 0;">
        <p style="color: #aaa; font-size: 12px; line-height: 1.5; margin-bottom: 0;">
            If the button doesn't work, copy and paste this URL into your browser:<br>
            <a href="{reset_url}" style="color: #48c774; word-break: break-all;">{reset_url}</a>
        </p>
    </div>
</body>
</html>
"""
        text_body = f"""Reset Your Password

You requested to reset your DailyNotes password.
Visit this link to set a new password: {reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.
Your password will remain unchanged.
"""
        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_magic_link(self, to_email: str, token: str) -> bool:
        """
        Send magic link login email.

        Args:
            to_email: Recipient email address
            token: Magic link token

        Returns:
            True if email was sent successfully
        """
        login_url = f"{self.app_url}/auth/verify-magic-link?token={token}"

        subject = "Sign in to DailyNotes"
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; padding: 40px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h1 style="color: #333; margin-top: 0; margin-bottom: 24px;">Sign in to DailyNotes</h1>
        <p style="color: #555; line-height: 1.6; margin-bottom: 24px;">
            Click the button below to sign in to your account:
        </p>
        <p style="margin: 32px 0; text-align: center;">
            <a href="{login_url}" style="background-color: #3273dc; color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 16px;">
                Sign In
            </a>
        </p>
        <p style="color: #888; font-size: 14px; line-height: 1.5; margin-bottom: 8px;">
            This link will expire in <strong>15 minutes</strong>.
        </p>
        <p style="color: #888; font-size: 14px; line-height: 1.5;">
            If you didn't request this, you can safely ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 32px 0;">
        <p style="color: #aaa; font-size: 12px; line-height: 1.5; margin-bottom: 0;">
            If the button doesn't work, copy and paste this URL into your browser:<br>
            <a href="{login_url}" style="color: #3273dc; word-break: break-all;">{login_url}</a>
        </p>
    </div>
</body>
</html>
"""
        text_body = f"""Sign in to DailyNotes

Click this link to sign in to your account: {login_url}

This link will expire in 15 minutes.

If you didn't request this, you can safely ignore this email.
"""
        return await self.send_email(to_email, subject, html_body, text_body)


# Global email service instance - initialized with app in __init__.py
email_service = EmailService()
