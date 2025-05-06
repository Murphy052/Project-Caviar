from __future__ import annotations

from typing import TYPE_CHECKING, Self

from bs4 import BeautifulSoup

from src.abstract.artifact_base import Artifact, Risk

if TYPE_CHECKING:
    from email.message import MIMEPart


class HTMLArtifact(Artifact):
    _raw_html: str
    _soup: BeautifulSoup

    def __init__(self, raw_html: str) -> None:
        self._raw_html = raw_html
        self._soup = BeautifulSoup(self._raw_html, features="html.parser")

    @classmethod
    def from_mime_part(cls, part: MIMEPart) -> Self:
        raw_html = part.get_content()
        return cls(raw_html)

    def _analyze(self) -> Risk:
        ...

    def report(self) -> str:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._soup.prettify()})"
