from app.scheduler.manager import scheduler_manager
from app.workers.mqtt_consumer import run_worker

if __name__ == "__main__":
    scheduler_manager.bootstrap()
    run_worker()
