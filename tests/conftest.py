import os
import sys
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session")
async def client():
    """
    Асинхронный клиент для тестирования FastAPI приложения,
    использует ASGI-интерфейс, минуя HTTP.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

