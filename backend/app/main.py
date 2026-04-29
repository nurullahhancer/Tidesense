import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.init_db import create_database_schema
from app.scheduler.manager import scheduler_manager
from app.websocket.manager import connection_manager
from app.websocket.routes import router as websocket_router

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(
        "Bootstrapping %s in %s mode",
        settings.project_name,
        settings.environment,
    )
    connection_manager.attach_loop(asyncio.get_running_loop())
    create_database_schema()
    
    # Bootstrap işlemini arka planda başlat (API'yi bloklamaz)
    asyncio.create_task(asyncio.to_thread(scheduler_manager.bootstrap))
    
    yield
    scheduler_manager.shutdown()
    logger.info("TideSense API shutdown completed")


app = FastAPI(
    title=settings.project_name,
    description=(
        "Ay konumu, sensör verileri, alarm üretimi ve makine öğrenmesi tabanlı "
        "gelgit tahminlerini tek serviste birleştiren TideSense backend API'si."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mount
static_path = Path(__file__).parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

app.include_router(api_router)
app.include_router(websocket_router)


@app.get("/", tags=["system"])
def read_root() -> dict[str, str]:
    return {
        "project": settings.project_name,
        "status": "running",
        "environment": settings.environment,
        "timestamp": datetime.now(UTC).isoformat(),
    }
