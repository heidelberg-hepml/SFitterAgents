from abc import ABC, abstractmethod

import torch


class Likelihood(ABC):
    @abstractmethod
    def __init__(self, params: dict, device: torch.device):
        pass

    @property
    @abstractmethod
    def dims_parameter(self) -> int:
        pass

    @property
    @abstractmethod
    def dims_nuisance(self) -> int:
        pass

    @property
    def dims_total(self) -> int:
        return self.dims_parameter + self.dims_nuisance

    @property
    @abstractmethod
    def parameter_names(self) -> list[str]:
        pass

    @abstractmethod
    def log_likelihood(self, x: torch.Tensor) -> torch.Tensor:
        pass

    @abstractmethod
    def log_prior(self, x: torch.Tensor) -> torch.Tensor:
        pass
