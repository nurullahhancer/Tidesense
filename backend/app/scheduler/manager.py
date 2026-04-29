from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.scheduler import jobs


class SchedulerManager:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self._started_at: datetime | None = None
        self._status = "idle"
        self._configured = False

    def _configure_jobs(self) -> None:
        if self._configured:
            return
        self.scheduler.add_job(
            jobs.moon_update_job,
            IntervalTrigger(minutes=settings.moon_update_interval_minutes),
            id="moon_update",
            replace_existing=True,
        )
        self.scheduler.add_job(
            jobs.prediction_generation_job,
            IntervalTrigger(minutes=settings.prediction_interval_minutes),
            id="prediction_generation",
            replace_existing=True,
        )
        self.scheduler.add_job(
            jobs.alert_check_job,
            IntervalTrigger(minutes=settings.alert_check_interval_minutes),
            id="alert_check",
            replace_existing=True,
        )
        self.scheduler.add_job(
            jobs.external_fetch_job,
            IntervalTrigger(minutes=settings.external_fetch_interval_minutes),
            id="external_fetch",
            replace_existing=True,
        )
        self._configured = True

    def bootstrap(self) -> None:
        if not settings.scheduler_enabled:
            self._status = "disabled"
            return
        jobs.bootstrap_job()
        self._configure_jobs()
        if not self.scheduler.running:
            self.scheduler.start()
        self._started_at = datetime.now(UTC)
        self._status = "running"

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        if self._status == "running":
            self._status = "stopped"

    def snapshot(self) -> dict:
        return {
            "status": self._status,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "jobs": [
                {
                    "id": job.id,
                    "next_run_time": (
                        next_run_time.isoformat()
                        if (next_run_time := getattr(job, "next_run_time", None))
                        else None
                    ),
                }
                for job in self.scheduler.get_jobs()
            ],
            "configured_jobs": {
                "moon_update_minutes": settings.moon_update_interval_minutes,
                "prediction_generation_minutes": settings.prediction_interval_minutes,
                "alert_check_minutes": settings.alert_check_interval_minutes,
                "external_fetch_minutes": settings.external_fetch_interval_minutes,
            },
        }


scheduler_manager = SchedulerManager()
