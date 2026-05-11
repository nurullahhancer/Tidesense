from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models import User
from app.services.email_service import send_email

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackCreate(BaseModel):
    subject: str = Field(..., min_length=3, max_length=128)
    message: str = Field(..., min_length=10, max_length=2000)

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcıdan gelen öneri ve şikayetleri alır ve tidesense.alert@gmail.com adresine e-posta gönderir.
    """
    subject = f"TideSense Geri Bildirim: {payload.subject}"
    body = f"""
    <html>
        <body>
            <h2>Yeni Geri Bildirim Alındı</h2>
            <p><strong>Gönderen Kullanıcı:</strong> {current_user.username} ({current_user.email or "E-posta belirtilmemiş"})</p>
            <p><strong>Konu:</strong> {payload.subject}</p>
            <hr>
            <p style="white-space: pre-wrap;">{payload.message}</p>
            <hr>
            <p style="font-size: 0.8rem; color: #666;">Bu mesaj TideSense sistemi üzerinden otomatik olarak gönderilmiştir.</p>
        </body>
    </html>
    """
    
    # tidesense.alert@gmail.com adresine gönder
    send_email(
        subject=subject,
        recipient="tidesense.alert@gmail.com",
        body_html=body
    )
    
    return {"message": "Geri bildiriminiz başarıyla iletildi. Teşekkür ederiz."}
