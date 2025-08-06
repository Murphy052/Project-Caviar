from __future__ import annotations

from abc import abstractmethod, ABC
from enum import Enum
from typing import Protocol, Optional


class Risk(Enum):
    Low = 0
    Medium = 1
    High = 2


class ArtifactRisk(ABC):
    _risk: Risk = Risk.Low

    @property
    def risk(self) -> Risk:
        return self._risk

    @risk.setter
    def risk(self, risk: Risk) -> None:
        if self._risk.value < risk.value:
            self._risk = risk


class Artifact(ArtifactRisk, ABC):
    @abstractmethod
    def analyze(self):
        ...

    @abstractmethod
    def report(self) -> dict:
        ...