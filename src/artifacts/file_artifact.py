from __future__ import annotations

from typing import TYPE_CHECKING, Self

import vt

from src.abstract.artifact_base import Artifact, Risk
from src.external.vt_client import get_vt_client

if TYPE_CHECKING:
    from email.message import EmailMessage


class FileArtifact(Artifact):
    file_name: str
    file_extension: str
    file_hash: str

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

    _analys_stat: dict = None

    def __init__(self, file_name: str, file: bytes) -> None:
        import hashlib

        self.file_name = file_name
        self.file_extension = self.file_name.split('.')[-1]
        self.file_hash = hashlib.sha256(file).hexdigest()

    @classmethod
    def from_email_part(cls, part: EmailMessage) -> Self:
        file = part.get_payload(decode=True)
        file_name = part.get_filename()  ## Also possible to get through magic bytes

        return cls(file_name, file)

    @classmethod
    def from_filename(cls, file_name: str) -> Self:
        with open(file_name, 'rb') as file:
            return cls(file_name, file.read())

    def analyze(self):
        stat = {"risks": {}}

        if self.file_extension in self._extensions_blacklist:
            self.risk = Risk.Medium
            stat["risks"]["file_extension"] = (Risk.Medium, "Blacklisted")

        with get_vt_client() as client:
            try:
                vt_file = client.get_object(f"/files/{self.file_hash}")
                self._analys_stat = vt_file.last_analysis_stats
            except vt.APIError as e:
                print(e)

        self._analys_stat = stat

    def report(self) -> dict:
        if self._analys_stat is None:
            self.analyze()

        self._analys_stat.update({
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "file_hash": self.file_hash,
        })

        return self._analys_stat
