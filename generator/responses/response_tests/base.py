# responses/response_tests/base.py
from abc import ABC, abstractmethod

import numpy as np

from ..config import ResponseData

class ResponseTest(ABC):
    @abstractmethod
    def compute_pvalues(self, data: ResponseData) -> np.ndarray:
        ...