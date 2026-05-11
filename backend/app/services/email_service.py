import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def send_email(subject: str, recipient: str, body_html: str) -> bool:
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not configured, skipping email to %s", recipient)
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_from
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        logger.info("Email sent successfully to %s", recipient)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", recipient, exc)
        return False


def send_critical_alert_email(recipient_email: str, station_name: str, water_level: float, severity: str) -> bool:
    subject = f"KRİTİK UYARI: {station_name} İstasyonunda Yüksek Su Seviyesi"
    
    body = f"""
    <html>
        <body>
            <h2 style="color: #dc2626;">TideSense Kritik Durum Bildirimi</h2>
            <p>Sayın kullanıcımız,</p>
            <p><strong>{station_name}</strong> istasyonunda kritik su seviyesi tespit edilmiştir.</p>
            <table border="0" cellpadding="5">
                <tr>
                    <td><strong>İstasyon:</strong></td>
                    <td>{station_name}</td>
                </tr>
                <tr>
                    <td><strong>Su Seviyesi:</strong></td>
                    <td><span style="color: #dc2626; font-weight: bold;">{water_level:.1f} cm</span></td>
                </tr>
                <tr>
                    <td><strong>Risk Seviyesi:</strong></td>
                    <td>{severity}</td>
                </tr>
            </table>
            <p>Lütfen gerekli önlemleri alınız ve <a href="{settings.frontend_origin}">TideSense Paneli</a> üzerinden durumu takip ediniz.</p>
            <hr>
            <p style="font-size: 0.8rem; color: #666;">
                Bu e-posta, TideSense sistemindeki tercihlerinize istinaden gönderilmiştir. 
                Bildirim ayarlarınızı panel üzerinden değiştirebilirsiniz.
            </p>
        </body>
    </html>
    """
    return send_email(subject, recipient_email, body)
