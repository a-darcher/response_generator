import sys
sys.path.append("/home/al/Documents/code/generate_responses/generator")

from abc import ABC, abstractmethod

import numpy as np

from responses.config import ResponseData


class ResponseTest(ABC):
    @abstractmethod
    def compute_pvalues(self, data: ResponseData) -> np.ndarray:
        ...