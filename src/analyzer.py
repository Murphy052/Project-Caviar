from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional, List, Any, Self, Literal
from email.message import EmailMessage

from src.Artifacts import HTMLArtifact, FileArtifact, PlainTextArtifact
from src.Artifacts.headers_artifact import HeaderArtifact


@dataclass(kw_only=True)
class ArtifactsAnalyzer:
    header: HeaderArtifact

    # Body
    markup: Optional[HTMLArtifact] = None
    body_plain_text: Optional[PlainTextArtifact] = None

    # Files
    images: List[Any]
    media: List[Any]
    application: List[FileArtifact]

    @classmethod
    def from_email_message(
            cls,
            msg: EmailMessage,
    ) -> Self:
        if msg.defects:
            print("defects:", msg.defects)

        # HEADER PART
        header = HeaderArtifact.from_email_message(msg)

        body_plain_text = None
        if plain_part := msg.get_body("plain"):
            body_plain_text = PlainTextArtifact(plain_part.get_content())

        markup = None
        if html_part := msg.get_body("html"):
            markup = HTMLArtifact.from_mime_part(html_part)

        images, media, application = cls._email_message_walk(msg)

        return cls(
            header=header,
            markup=markup,
            body_plain_text=body_plain_text,
            images=images,
            media=media,
            application=application,
        )

    @staticmethod
    def _email_message_walk(part: EmailMessage):
        images = []
        media = []
        application = []

        for part in part.walk():
            main_type = part.get_content_maintype()
            match main_type:
                case "multipart":
                    # self.walk(part)
                    continue
                case "image":
                    images.append(part.get_payload())
                case "audio" | "video":
                    media.append(part.get_payload())
                case "application":
                    file = FileArtifact.from_email_part(part)
                    application.append(file)

        return images, media, application

    def analyse(self) -> Any: # TODO: implement aggregation function
        risk = 0
        risk += self.header.risk.value
        risk += self.markup.risk.value
        risk += self.body_plain_text.risk.value

        return risk

