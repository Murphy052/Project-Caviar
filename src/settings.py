from __future__ import annotations

from typing_extensions import Self


class Settings:
    VT_API_KEY: str

    __instance: Self | None = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.VT_API_KEY = os.getenv("VT_API_KEY")


settings = Settings()
