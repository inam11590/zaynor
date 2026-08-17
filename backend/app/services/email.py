"""Email service — sends transactional emails via SMTP or logs to console."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger("zaynor.email")


def _build_order_confirmation_html(
    customer_name: str,
    order_id: int,
    items: List[Dict[str, Any]],
    total: float,
    notes: Optional[str] = None,
) -> str:
    """Build an HTML email body for order confirmation."""
    item_rows = ""
    for item in items:
        item_rows += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{item['product_name']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;">{item['quantity']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;">Rs. {item['unit_price']:,.0f}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;">Rs. {item['quantity'] * item['unit_price']:,.0f}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;">
            <div style="background:#1a1a1a;padding:20px;text-align:center;">
                <h1 style="color:#c9a84c;margin:0;font-size:24px;">ZAYNOR</h1>
            </div>
            <div style="padding:30px;">
                <h2 style="color:#1a1a1a;">Order Confirmation</h2>
                <p style="color:#666;">Hi {customer_name}, thank you for your order!</p>
                <p style="color:#666;">Order <strong>#{order_id}</strong> has been received and is being processed.</p>

                <table style="width:100%;border-collapse:collapse;margin:20px 0;">
                    <thead>
                        <tr style="background:#f9f9f9;">
                            <th style="padding:8px 12px;text-align:left;">Product</th>
                            <th style="padding:8px 12px;text-align:center;">Qty</th>
                            <th style="padding:8px 12px;text-align:right;">Price</th>
                            <th style="padding:8px 12px;text-align:right;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>{item_rows}</tbody>
                    <tfoot>
                        <tr>
                            <td colspan="3" style="padding:12px;text-align:right;font-weight:bold;border-top:2px solid #1a1a1a;">Total</td>
                            <td style="padding:12px;text-align:right;font-weight:bold;border-top:2px solid #1a1a1a;">Rs. {total:,.0f}</td>
                        </tr>
                    </tfoot>
                </table>

                <p style="color:#666;">We will contact you on WhatsApp to confirm delivery details.</p>
                {f'<p style="color:#999;font-size:13px;"><strong>Note:</strong> {notes}</p>' if notes else ''}
            </div>
            <div style="background:#f9f9f9;padding:15px;text-align:center;">
                <p style="color:#999;font-size:12px;margin:0;">This is an automated email from ZAYNOR.</p>
            </div>
        </div>
    </body>
    </html>"""


def _build_admin_notification_html(
    customer_name: str,
    customer_email: str,
    order_id: int,
    items: List[Dict[str, Any]],
    total: float,
    notes: Optional[str] = None,
) -> str:
    """Build an HTML email body for admin new-order notification."""
    item_rows = ""
    for item in items:
        item_rows += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{item['product_name']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;">{item['quantity']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;">Rs. {item['quantity'] * item['unit_price']:,.0f}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;">
            <div style="background:#c9a84c;padding:20px;text-align:center;">
                <h1 style="color:#fff;margin:0;font-size:20px;">New Order Received</h1>
            </div>
            <div style="padding:30px;">
                <p style="color:#1a1a1a;font-size:16px;">A new order has been placed on ZAYNOR.</p>
                <table style="width:100%;margin:15px 0;">
                    <tr><td style="color:#999;padding:4px 0;">Order ID</td><td style="font-weight:bold;">#{order_id}</td></tr>
                    <tr><td style="color:#999;padding:4px 0;">Customer</td><td>{customer_name}</td></tr>
                    <tr><td style="color:#999;padding:4px 0;">Email</td><td>{customer_email}</td></tr>
                </table>

                <table style="width:100%;border-collapse:collapse;margin:20px 0;">
                    <thead>
                        <tr style="background:#f9f9f9;">
                            <th style="padding:8px 12px;text-align:left;">Product</th>
                            <th style="padding:8px 12px;text-align:center;">Qty</th>
                            <th style="padding:8px 12px;text-align:right;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>{item_rows}</tbody>
                    <tfoot>
                        <tr>
                            <td colspan="2" style="padding:12px;text-align:right;font-weight:bold;border-top:2px solid #1a1a1a;">Total</td>
                            <td style="padding:12px;text-align:right;font-weight:bold;border-top:2px solid #1a1a1a;">Rs. {total:,.0f}</td>
                        </tr>
                    </tfoot>
                </table>

                {f'<p style="color:#666;"><strong>Customer note:</strong> {notes}</p>' if notes else ''}
            </div>
        </div>
    </body>
    </html>"""


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email. Returns True if sent successfully.

    In development (SMTP_ENABLED=false), logs the email to the console.
    In production, sends via the configured SMTP server.
    """
    if not settings.SMTP_ENABLED:
        logger.info(
            "[EMAIL DISABLED] Would send to=%s subject=%s",
            to_email,
            subject,
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())

        logger.info("Email sent to=%s subject=%s", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to=%s error=%s", to_email, exc)
        return False


def send_order_confirmation(customer_name: str, customer_email: str, order_id: int,
                            items: List[Dict[str, Any]], total: float,
                            notes: Optional[str] = None) -> bool:
    """Send order confirmation email to the customer."""
    html = _build_order_confirmation_html(customer_name, order_id, items, total, notes)
    return send_email(customer_email, f"ZAYNOR — Order #{order_id} Confirmed", html)


def send_admin_new_order(customer_name: str, customer_email: str, order_id: int,
                         items: List[Dict[str, Any]], total: float,
                         notes: Optional[str] = None) -> bool:
    """Notify the admin about a new order."""
    html = _build_admin_notification_html(customer_name, customer_email, order_id, items, total, notes)
    return send_email(settings.ADMIN_EMAIL, f"ZAYNOR — New Order #{order_id}", html)
