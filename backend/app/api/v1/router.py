from fastapi import APIRouter

from app.api.v1.endpoints import (
    alerts,
    auth,
    cameras,
    health,
    moon,
    predictions,
    readings,
    sensors,
    stations,
    users,
)

router = APIRouter()
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(stations.router)
router.include_router(sensors.router)
router.include_router(readings.router)
router.include_router(moon.router)
router.include_router(predictions.router)
router.include_router(alerts.router)
router.include_router(cameras.router)
