from __future__ import annotations

from typing import TYPE_CHECKING, Self, Any

import vt

from src.abstract.artifact_base import Artifact, Risk
from src.external.vt_client import get_vt_client

if TYPE_CHECKING:
    from email.message import EmailMessage


class FileArtifact(Artifact):
    _name: str
    _extension: str
    _hash: str

    _extensions_blacklist: tuple[str, ...] = (
        "exe",
        "html",
        "vbs",
        "js",
        "iso",
        "bat",
        "ps",
        "ps1",
    )

    _analys_stat: Any = None

    def __init__(self, file_name: str, file: bytes) -> None:
        import hashlib

        self._name = file_name
        self._extension = self._name.split('.')[-1]
        self._hash = hashlib.sha256(file).hexdigest()

    @classmethod
    def from_email_part(cls, part: EmailMessage) -> Self:
        file = part.get_payload(decode=True)
        file_name = part.get_filename()  ## Also possible to get through magic bytes

        return cls(file_name, file)

    @classmethod
    def from_filename(cls, file_name: str) -> Self:
        with open(file_name, 'rb') as file:
            return cls(file_name, file.read())

    def _analyze(self):
        if self._extension in self._extensions_blacklist:
            self.risk = Risk.Medium

        with get_vt_client() as client:
            try:
                vt_file = client.get_object(f"/files/{self._hash}")
                self._analys_stat = vt_file.last_analysis_stats
            except vt.APIError as e:
                print(e)

    def report(self) -> str:
        if self.risk is None:
            self._analyze()

        return f"FILE:{self._name}\nHASH:{self._hash}\nRISK:{self._risk}\nVT_RESULT:{self._analys_stat}"
