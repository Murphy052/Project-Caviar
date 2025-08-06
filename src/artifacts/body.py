from __future__ import annotations

import re
from email.message import EmailMessage
from typing import Optional

from bs4 import BeautifulSoup

from src.abstract.artifact_base import Artifact, Risk

from src.external.phishsense import get_phishsense_model

_url_pattern = re.compile(r"e\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:/[^\s<>)\"\']*)?")


class BodyArtifact(Artifact):
    text: str
    markup_text: Optional[str]
    _soup: BeautifulSoup

    _analys_stat: dict = None

    def __init__(self, text: str, markup: Optional[str]) -> None:
        # Raw text
        self.text = text

        # HTML Markup
        if not markup:
            self.markup_text = None
            return

        self._soup = BeautifulSoup(markup, features="html.parser")
        self.markup_text = self._soup.get_text(strip=True)

    @classmethod
    def from_email_message(cls, msg: EmailMessage) -> BodyArtifact:
        body_plain_text = None
        if plain_part := msg.get_body("plain"):
            body_plain_text = plain_part.get_content()

        markup = None
        if html_part := msg.get_body("html"):
            markup = html_part.get_content()

        return cls(body_plain_text, markup)

    def analyze(self):
        report = {"risks": {}}

        model = get_phishsense_model()
        is_phishing = model.predict(self.text) or model.predict(self.markup_text)

        if is_phishing:
            self.risk = Risk.High
            report["risks"]["text"] = (Risk.High, "Phishsense analys results")

        self._analys_stat = report

    def report(self) -> dict:
        if self._analys_stat is None:
            self.analyze()

        self._analys_stat.update({
            "text": self.text,
        })

        return self._analys_stat

    def get_urls(self) -> list[str]:
        return [a['href'] for a in self._soup.find_all('a', href=True)] + _url_pattern.findall(self.text)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(\n"
                f"\tRaw Text:\n{self.text}\n"
                f"\tMarkup:\n{self._soup.prettify()}\n"
                f")")
