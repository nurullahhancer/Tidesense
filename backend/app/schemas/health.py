from pydantic import BaseModel


class HealthComponent(BaseModel):
    status: str
    detail: str | None = None


class HealthResponse(BaseModel):
    project: str
    timestamp: str
    environment: str
    database: HealthComponent
    websocket: dict
    scheduler: dict
    ml_module: dict
    external_provider: dict
    counts: dict
