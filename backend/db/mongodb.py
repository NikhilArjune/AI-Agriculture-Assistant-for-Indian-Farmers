import logging
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncMongoClient] = None
_db: Optional[AsyncDatabase] = None


async def connect_db() -> None:
    global _client, _db

    _ensure_local_mongo_available()

    # Import all Beanie document models
    from models.user import User
    from models.farmer_profile import FarmerProfile
    from models.farm import Farm
    from models.crop_advisory import CropAdvisory
    from models.disease_report import DiseaseReport
    from models.soil_advisory import SoilAdvisory
    from models.weather_alert import WeatherAlert
    from models.market_price import MarketPrice
    from models.scheme import GovernmentScheme
    from models.chat_history import ChatMessage as ChatHistory
    from models.uploaded_file import UploadedFile
    from models.notification import Notification
    from models.admin_user import AdminUser

    _client = AsyncMongoClient(settings.mongo_uri)
    _db = _client[settings.mongo_db_name]

    await init_beanie(
        database=_db,
        document_models=[
            User,
            FarmerProfile,
            Farm,
            CropAdvisory,
            DiseaseReport,
            SoilAdvisory,
            WeatherAlert,
            MarketPrice,
            GovernmentScheme,
            ChatHistory,
            UploadedFile,
            Notification,
            AdminUser,
        ],
    )

    logger.info("Connected to MongoDB: %s / %s", settings.mongo_uri, settings.mongo_db_name)


def _ensure_local_mongo_available() -> None:
    """Start a local dev MongoDB process on Windows when localhost is not running."""
    parsed = urlparse(settings.mongo_uri)
    host = parsed.hostname or ""
    port = parsed.port or 27017

    if settings.is_production or host not in {"localhost", "127.0.0.1", "::1"}:
        return
    if _is_port_open("127.0.0.1", port):
        return
    if sys.platform != "win32":
        return

    mongod = _find_mongod_exe()
    if mongod is None:
        logger.warning(
            "MongoDB is not running on localhost:%s and mongod.exe was not found. "
            "Start MongoDB from Compass/Services or install MongoDB Community Server.",
            port,
        )
        return

    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / ".local-mongo" / "data"
    log_dir = project_root / ".local-mongo" / "log"
    log_file = log_dir / "mongod.log"
    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.info("MongoDB is not running. Starting local mongod at %s", mongod)
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        [
            str(mongod),
            "--dbpath",
            str(data_dir),
            "--logpath",
            str(log_file),
            "--bind_ip",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
        close_fds=True,
    )

    deadline = time.time() + 20
    while time.time() < deadline:
        if _is_port_open("127.0.0.1", port):
            logger.info("Local MongoDB started on 127.0.0.1:%s", port)
            return
        time.sleep(0.5)

    logger.warning("Tried to start MongoDB, but port %s is still closed. Check %s", port, log_file)


def _is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def _find_mongod_exe() -> Optional[Path]:
    configured = os.getenv("MONGOD_PATH")
    if configured:
        path = Path(configured)
        if path.exists():
            return path

    candidates = []
    program_files = [os.getenv("ProgramFiles"), os.getenv("ProgramW6432")]
    for base in [Path(p) for p in program_files if p]:
        server_dir = base / "MongoDB" / "Server"
        if server_dir.exists():
            candidates.extend(server_dir.glob("*/bin/mongod.exe"))

    return sorted(candidates, reverse=True)[0] if candidates else None


async def disconnect_db() -> None:
    global _client
    if _client:
        await _client.close()
        logger.info("Disconnected from MongoDB.")


def get_db() -> AsyncDatabase:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db
