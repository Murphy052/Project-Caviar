from __future__ import annotations

from pprint import pprint
import email
from email import policy
from email.message import EmailMessage

from src.external.phishsense import Phishsense1BModel
from src.analyzer import ArtifactsAnalyzer


def func():
    from email.iterators import _structure

    file1 = "src/mails/example.eml"
    file2 = "src/mails/multipart_example.eml"
    with open(file2, "rb") as f:
        msg: EmailMessage = email.message_from_binary_file(f, policy=policy.default)

    if not msg:
        exit(1)

    m = ArtifactsAnalyzer.from_email_message(msg)
    m.body_plain_text._analyze()

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
