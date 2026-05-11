from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User, UserReportPreference, Port
from app.schemas.report import ReportPreferenceRead, ReportPreferenceUpdate

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/preferences", response_model=ReportPreferenceRead)
def get_report_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kullanıcının rapor tercihlerini getirir.
    """
    selected_port_ids = db.scalars(
        select(UserReportPreference.port_id).where(UserReportPreference.user_id == current_user.id)
    ).all()
    
    return ReportPreferenceRead(
        weekly_reports_enabled=current_user.weekly_reports_enabled,
        selected_port_ids=list(selected_port_ids)
    )

@router.put("/preferences", response_model=ReportPreferenceRead)
def update_report_preferences(
    payload: ReportPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kullanıcının rapor tercihlerini günceller.
    """
    if payload.weekly_reports_enabled is not None:
        current_user.weekly_reports_enabled = payload.weekly_reports_enabled
        db.add(current_user)
    
    if payload.selected_port_ids is not None:
        # Mevcutları sil
        db.execute(delete(UserReportPreference).where(UserReportPreference.user_id == current_user.id))
        
        # Yenileri ekle
        for port_id in payload.selected_port_ids:
            # Portun varlığını kontrol et
            port = db.get(Port, port_id)
            if port:
                pref = UserReportPreference(user_id=current_user.id, port_id=port_id)
                db.add(pref)
    
    db.commit()
    db.refresh(current_user)
    
    selected_port_ids = db.scalars(
        select(UserReportPreference.port_id).where(UserReportPreference.user_id == current_user.id)
    ).all()
    
    return ReportPreferenceRead(
        weekly_reports_enabled=current_user.weekly_reports_enabled,
        selected_port_ids=list(selected_port_ids)
    )
