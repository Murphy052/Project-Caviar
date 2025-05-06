from __future__ import annotations

from typing_extensions import Self

from src.abstract.singleton import SingletonMeta


class Settings(metaclass=SingletonMeta):
    VT_API_KEY: str

    def __init__(self):
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.VT_API_KEY = os.getenv("VT_API_KEY")


settings = Settings()
