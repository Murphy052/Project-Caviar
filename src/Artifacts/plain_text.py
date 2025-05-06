from __future__ import annotations

import re
from typing import TYPE_CHECKING

from src.Artifacts.artifact_base import Artifact, Risk

from src.external.phishsense import get_phishsense_model

_url_pattern = re.compile(r"e\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:/[^\s<>)\"\']*)?")


class PlainTextArtifact(Artifact):
    _text: str
    _urls: list[str]

    def __init__(self, text: str) -> None:
        self._text = text
        self.urls = _url_pattern.findall(text)

    def _analyze(self) -> Risk:
        model = get_phishsense_model()
        result = model.predict(self._text)
        print(f"DEBUG:{result}")
        if "TRUE" in result:
            return Risk.High

        return Risk.Low

    def report(self) -> str:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._text})"
