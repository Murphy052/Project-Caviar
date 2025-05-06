from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from vt import Client as VTClient

from src.settings import settings


@contextmanager
def get_vt_client() -> Generator[VTClient, None, None]:
    vt_client = VTClient(settings.VT_API_KEY)

    yield vt_client

    vt_client.close()
