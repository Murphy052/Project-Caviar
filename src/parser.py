from __future__ import annotations

import re
from dataclasses import dataclass
from pprint import pprint
from typing import Optional, List, Any
import email
from email import policy
from email.message import EmailMessage

from src.Artifacts import HTMLArtifact, FileArtifact, PlainTextArtifact


@dataclass(kw_only=True)
class ArtifactsParser:
    # Header
    sender: Any
    received: List[str]
    reply_to: List[str]
    subject: Optional[PlainTextArtifact] = None

    # Body
    markup: Optional[HTMLArtifact] = None
    body_plain_text: Optional[PlainTextArtifact] = None

    # Files
    images: List[Any]
    media: List[Any]
    application: List[FileArtifact]

    def __init__(self, msg: EmailMessage) -> None:
        if msg.defects:
            print("defects:", msg.defects)

        # HEADER PART
        self.sender = msg["from"]
        self.received = msg.get_all("Received", [])
        self.reply_to = msg.get_all("Reply-To", failobj=msg.get_all("In-Reply-To", []))
        self.subject = PlainTextArtifact(msg["subject"])

        if plain_part := msg.get_body("plain"):
            self.body_plain_text = PlainTextArtifact(plain_part.get_content())

        if html_part := msg.get_body("html"):
            self.markup = HTMLArtifact.from_mime_part(html_part)

        self.images = []
        self.media = []
        self.application = []

        # BODY
        self.walk(msg)


    def walk(self, part: EmailMessage):
        for part in part.walk():
            main_type = part.get_content_maintype()
            match main_type:
                case "multipart":
                    # self.walk(part)
                    continue
                case "image":
                    self.images.append(part.get_payload())
                case "audio" | "video":
                    self.media.append(part.get_payload())
                case "application":
                    file = FileArtifact.from_email_part(part)
                    self.application.append(file)


def func():
    from email.iterators import _structure

    file1 = "src/mails/example.eml"
    file2 = "src/mails/multipart_example.eml"
    with open(file2, "rb") as f:
        msg: EmailMessage = email.message_from_binary_file(f, policy=policy.default)

    if not msg:
        exit(1)

    m = ArtifactsParser(msg)

    pprint(m)
    # pprint(m.received)
    pprint(msg)
    _structure(msg)

    print(msg.keys())

    for part in msg.iter_parts():
        print(part.get_content_type())

    # print(m.application)
    # print(m.body)
    # for obj in msg.walk():
    #     print(c_type := obj.get_content_type())
