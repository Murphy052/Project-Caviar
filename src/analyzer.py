from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Any, Self
from email.message import EmailMessage

from src.artifacts import FileArtifact, BodyArtifact, HeaderArtifact


@dataclass(kw_only=True)
class ArtifactsAnalyzer:
    header: HeaderArtifact
    body: Optional[BodyArtifact] = None
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

        header = HeaderArtifact.from_email_message(msg)
        body = BodyArtifact.from_email_message(msg)
        #urls = body.get_urls()

        # FILES
        images, media, application = cls._email_message_walk(msg)

        return cls(
            header=header,
            body=body,
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

        if self.body:
            report.update({"Body": self.body.report()})
            risk += self.body.risk.value

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
