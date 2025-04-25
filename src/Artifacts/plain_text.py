from __future__ import annotations

import re

from src.Artifacts.artifact_base import Artifact, Risk


_url_pattern = re.compile(r"e\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:/[^\s<>)\"\']*)?")


class PlainTextArtifact(Artifact):
    _text: str
    _urls: list[str]

    def __init__(self, text: str):
        self._text = text
        self.urls = _url_pattern.findall(text)

    def _analyze(self) -> Risk:
        # TODO: Make call to model
        ...

    def report(self) -> str:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._text})"
