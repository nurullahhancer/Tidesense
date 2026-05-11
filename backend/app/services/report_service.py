from datetime import UTC, datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User, UserReportPreference, Port, Station, SensorReading
from app.services.email_service import send_email

def generate_weekly_report_data(db: Session, user: User) -> list[dict]:
    """
    Kullanıcının seçtiği limanlar için son 1 haftanın günlük özet verilerini hesaplar.
    """
    selected_ports = db.scalars(
        select(Port).join(UserReportPreference).where(UserReportPreference.user_id == user.id)
    ).all()
    
    if not selected_ports:
        return []
    
    end_at = datetime.now(UTC)
    start_at = (end_at - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    report_data = []
    
    for port in selected_ports:
        # Port altındaki tüm istasyonları al
        stations = db.scalars(select(Station).where(Station.port_id == port.id)).all()
        station_ids = [s.id for s in stations]
        
        if not station_ids:
            continue
            
        # Günlük bazda aggregate et
        # Not: PostgreSQL date_trunc veya casting kullanacağız
        query = (
            select(
                func.date(SensorReading.recorded_at).label("day"),
                func.min(SensorReading.water_level_cm).label("min_val"),
                func.max(SensorReading.water_level_cm).label("max_val"),
                func.avg(SensorReading.water_level_cm).label("avg_val")
            )
            .where(
                SensorReading.station_id.in_(station_ids),
                SensorReading.recorded_at >= start_at,
                SensorReading.recorded_at < end_at
            )
            .group_by(func.date(SensorReading.recorded_at))
            .order_by(func.date(SensorReading.recorded_at).asc())
        )
        
        days = db.execute(query).all()
        
        if days:
            report_data.append({
                "port_name": port.name,
                "city": port.city,
                "days": [
                    {
                        "date": d.day.isoformat() if hasattr(d.day, "isoformat") else str(d.day),
                        "min": float(d.min_val),
                        "max": float(d.max_val),
                        "avg": float(d.avg_val)
                    } for d in days
                ]
            })
            
    return report_data

def send_weekly_reports(db: Session):
    """
    Rapor ayarı açık olan tüm kullanıcılara haftalık özet e-postası gönderir.
    """
    users = db.scalars(select(User).where(User.weekly_reports_enabled == True)).all()
    
    for user in users:
        if not user.email:
            continue
            
        data = generate_weekly_report_data(db, user)
        if not data:
            continue
            
        subject = "TideSense Haftalık Su Seviyesi Raporu"
        
        # Basit bir HTML template oluştur
        html_content = f"""
        <html>
            <body style="font-family: sans-serif; color: #333;">
                <h2 style="color: #2563eb;">Haftalık Özet Raporu</h2>
                <p>Merhaba <strong>{user.username}</strong>,</p>
                <p>Seçtiğiniz limanlar için son 1 haftalık su seviyesi özetleri aşağıdadır:</p>
        """
        
        for port_report in data:
            html_content += f"""
                <div style="margin-top: 24px; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px;">
                    <h3 style="margin-top: 0;">{port_report['port_name']} ({port_report['city']})</h3>
                    <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; border-color: #e5e7eb;">
                        <tr style="background-color: #f9fafb;">
                            <th>Tarih</th>
                            <th>En Düşük (cm)</th>
                            <th>Ortalama (cm)</th>
                            <th>En Yüksek (cm)</th>
                        </tr>
            """
            for day in port_report['days']:
                html_content += f"""
                        <tr>
                            <td>{day['date']}</td>
                            <td style="text-align: center;">{day['min']:.1f}</td>
                            <td style="text-align: center;">{day['avg']:.1f}</td>
                            <td style="text-align: center;">{day['max']:.1f}</td>
                        </tr>
                """
            html_content += "</table></div>"
            
        html_content += f"""
                <p style="margin-top: 30px; font-size: 0.9rem; color: #666;">
                    Bu rapor otomatik olarak gönderilmiştir. Rapor ayarlarınızı 
                    <a href="{settings.frontend_origin}/reports">TideSense Paneli</a> üzerinden değiştirebilirsiniz.
                </p>
                <hr>
                <p style="font-size: 0.8rem; color: #999;">Gönderen: tidesense.alert@gmail.com</p>
            </body>
        </html>
        """
        
        send_email(subject, user.email, html_content)
