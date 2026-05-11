from pydantic import BaseModel

class ReportPreferenceRead(BaseModel):
    weekly_reports_enabled: bool
    selected_port_ids: list[int]

class ReportPreferenceUpdate(BaseModel):
    weekly_reports_enabled: bool | None = None
    selected_port_ids: list[int] | None = None
