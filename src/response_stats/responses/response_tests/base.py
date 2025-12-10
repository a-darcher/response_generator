# responses/response_tests/base.py
from abc import ABC, abstractmethod
from enum import Enum, auto

import numpy as np

from response_stats.responses.config import ResponseData

class TestKind(Enum):
    PARAMETRIC = auto()
    SURROGATE = auto()

class ResponseTest(ABC):
    kind: TestKind.PARAMETRIC
    @abstractmethod
    def compute_pvalues(self, data: ResponseData) -> np.ndarray:
        ...