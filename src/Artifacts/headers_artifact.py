from __future__ import annotations

from email.message import EmailMessage
from typing import Self, List, Union

from src.Artifacts import PlainTextArtifact
from src.Artifacts.artifact_base import Artifact, Risk


class HeaderArtifact(Artifact):
    sender: str
    received: List[str]
    reply_to: List[str]
    subject: PlainTextArtifact

    def __init__(
            self,
            sender: str,
            received: List[str],
            reply_to: List[str],
            subject: Union[PlainTextArtifact, str],
            *args,
            **kwargs,
    ):
        self.sender = sender
        self.received = received
        self.reply_to = reply_to

        if not isinstance(subject, PlainTextArtifact):
            subject = PlainTextArtifact(subject)

        self.subject = subject

    @classmethod
    def from_email_message(
            cls,
            msg: EmailMessage,
    ) -> Self:
        sender = msg["from"]
        received = msg.get_all("Received", [])
        reply_to = msg.get_all("Reply-To", failobj=msg.get_all("In-Reply-To", []))
        subject = PlainTextArtifact(msg["subject"])

        return cls(sender, received, reply_to, subject)

    def _analyze(self) -> Risk:
        ...

    def report(self) -> Risk:
        ...
