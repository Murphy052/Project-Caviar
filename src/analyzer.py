from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Any, Self
from email.message import EmailMessage

from src.artifacts import HTMLArtifact, FileArtifact, BodyArtifact, HeaderArtifact


@dataclass(kw_only=True)
class ArtifactsAnalyzer:
    header: HeaderArtifact

    # Body
    markup: Optional[HTMLArtifact] = None
    body_plain_text: Optional[BodyArtifact] = None

    # Web

    # Files
    images: List[Any]
    media: List[Any]
    application: List[FileArtifact]

    _report: List = field(default_factory=dict)

    @classmethod
    def from_email_message(
            cls,
            msg: EmailMessage,
    ) -> Self:
        if msg.defects:
            print("defects:", msg.defects)

        # HEADER PART
        header = HeaderArtifact.from_email_message(msg)

        # BODY PART
        body_plain_text = None
        urls = []
        if plain_part := msg.get_body("plain"):
            body_plain_text = BodyArtifact(plain_part.get_content())
            urls = body_plain_text.get_urls()

        markup = None
        if html_part := msg.get_body("html"):
            markup = HTMLArtifact.from_mime_part(html_part)
            urls.extend(markup.get_urls())

        # FILES
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
        report = {}
        risk = 0

        if self.markup:
            report.update({"Markup": self.markup.report()})
            risk += self.markup.risk.value
        if self.body_plain_text:
            report.update({"Plain Body": self.body_plain_text.report()})
            risk += self.body_plain_text.risk.value

        if len(self.application) >0:
            files_risk = 0
            files_reports = []
            for file_artifact in self.application:
                files_reports.append(file_artifact.report())
                files_risk += file_artifact.risk.value
            risk += files_risk/len(self.application)
            report.update({"Files": files_reports})

        report.update({"Headers": self.header.report()})
        risk += self.header.risk.value

        self._report = report

        return risk

    def get_report(self) -> List[dict]:
        return self._report
