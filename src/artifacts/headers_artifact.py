from __future__ import annotations

import re
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from typing import Self, List

from src.abstract.artifact_base import Artifact
from src.external.phishsense import Phishsense1BModel


class HeaderArtifact(Artifact):
    sender: str
    received: List[str]
    reply_to: List[str]
    subject: str

    _analys_stat: dict = None

    def __init__(
            self,
            sender: str,
            received: List[str],
            reply_to: List[str],
            subject: str,
            *args,
            **kwargs,
    ):
        self.sender = sender
        self.received = received
        self.reply_to = reply_to
        self.subject = subject

    @classmethod
    def from_email_message(
            cls,
            msg: EmailMessage,
    ) -> Self:
        sender = msg["from"]
        received = msg.get_all("Received", [])
        reply_to = msg.get_all("Reply-To", failobj=msg.get_all("In-Reply-To", []))
        subject = msg["subject"]

        return cls(sender, received, reply_to, subject)

    def analyze(self) -> None:
        report = {"risks": {}}
        risk = 0

        if Phishsense1BModel().predict(self.subject):
            risk += 2
            report["risks"]["subject"] = "Phishsense1B: Malicious"

        hops = self.trace_route()
        report.update({
            "hops": hops,
            "delays": self.analyze_delays(hops),
        })

        self._analys_stat = report


    def report(self) -> dict:
        if self._analys_stat is None:
            self.analyze()

        self._analys_stat.update({
            "sender": self.sender,
            "received": self.received,
            "reply_to": self.reply_to,
            "subject": self.subject,
        })

        return self._analys_stat

    def trace_route(self):
        received_headers = self.received
        hops = []

        for rec in received_headers:
            # Extract 'from' and 'by' parts using regex
            from_match = re.search(r'from\s+(\S+)', rec, re.IGNORECASE)
            by_match = re.search(r'by\s+(\S+)', rec, re.IGNORECASE)
            from_host = from_match.group(1) if from_match else None
            by_host = by_match.group(1) if by_match else None

            # Extract the last IP address in brackets, if present
            ips = re.findall(r'\[([0-9\.]+)\]', rec)
            ip = ips[-1] if ips else None

            # Extract date after the last semicolon and parse to datetime
            parts = rec.rsplit(';', 1)
            date_str = parts[-1].strip() if len(parts) > 1 else ''
            try:
                dt = parsedate_to_datetime(date_str)
            except (TypeError, ValueError):
                dt = None

            hops.append({
                'from': from_host,
                'by': by_host,
                'ip': ip,
                'raw_date': date_str,
                'datetime': dt
            })

        # Sort hops by datetime (earliest first)
        hops = sorted([h for h in hops if h['datetime']], key=lambda h: h['datetime'])
        return hops

    @staticmethod
    def analyze_delays(hops):
        """
        Calculate time differences between consecutive hops.
        Returns a list of delays in seconds between hop[i] and hop[i+1].
        """
        delays = []
        for i in range(1, len(hops)):
            t_prev = hops[i - 1]['datetime']
            t_curr = hops[i]['datetime']
            if t_prev and t_curr:
                diff_sec = (t_curr - t_prev).total_seconds()
                delays.append(diff_sec)
        return delays