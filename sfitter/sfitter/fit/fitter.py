import os
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field

import torch
import numpy as np
from tqdm import tqdm

from ..likelihood.likelihood import Likelihood


@dataclass
class FitResults:
    """
    Data class that contains the results of a fit. All dictionaries have the parameter names
    or pairs of parameter names as keys.

    Args:
        parameters: list of the names of the likelihood parameters
        points: bin centers, shape (n_bins, )
        marginal_1d: 1d marginal histograms, shape (n_bins_1d, )
        marginal_1d_bins: bin boundaries for 1d marginal histograms, shape (n_bins_1d + 1, )
        marginal_2d: 2d marginal histograms, shape (n_bins_2d, n_bins_2d)
        marginal_2d_bins: bin boundaries for 2d marginal histograms, shape (n_bins_2d + 1, )
        profile_1d: 1d profile likelihoods, shape (n_points_1d, )
        profile_1d_points: points for 1d profile likelihoods, shape (n_points_1d, )
        profile_2d: 2d profile likelihoods, shape (n_points_2d, n_points_2d)
        profile_2d_points: points for 2d profile likelihoods, shape (n_points_2d, )
        marginal_effective_size: effective sample size used for marginalization
    """
    parameters: list[str]
    marginal_1d: dict[str, np.ndarray]
    marginal_1d_bins: dict[str, np.ndarray]
    marginal_2d: dict[str, np.ndarray]
    marginal_2d_bins: dict[str, np.ndarray]
    profile_1d: dict[tuple[str, str], np.ndarray]
    profile_1d_bins: dict[str, np.ndarray]
    profile_2d: dict[tuple[str, str], np.ndarray]
    profile_2d_bins: dict[str, np.ndarray]
    marginal_effective_size: float
    marginal_1d_points: dict[str, np.ndarray] = field(init=False)
    marginal_2d_points: dict[str, np.ndarray] = field(init=False)
    profile_1d_points: dict[str, np.ndarray] = field(init=False)
    profile_2d_points: dict[str, np.ndarray] = field(init=False)
    w_bins_lin: np.ndarray
    w_hist_lin: np.ndarray
    w_bins_log: np.ndarray
    w_hist_log: np.ndarray

    def __post_init__(self):
        def bins_to_points(bins):
            return {key: (value[:-1] + value[1:]) / 2 for key, value in bins.items()}
        self.marginal_1d_points = bins_to_points(self.marginal_1d_bins)
        self.marginal_2d_points = bins_to_points(self.marginal_2d_bins)
        self.profile_1d_points = bins_to_points(self.profile_1d_bins)
        self.profile_2d_points = bins_to_points(self.profile_2d_bins)

class Fitter(ABC):
    """
    Abstract base class for fitters.
    """

    state_dict_attrs: list[str] = []
    save_attrs: list[str] = []

    def __init__(
        self,
        params: dict,
        verbose: bool,
        device: torch.device,
        state_file: str,
        likelihood: Likelihood,
    ):
        """
        Fitter constructor that is the same for all subclasses such that fitters can be
        constructed automatically. It sets the params, verbose, device, state_file and
        likelihood attributes and then calls the initialize method for further initialization.

        Args:
            params: dictionary with the run parameters
            verbose: if True, display progress bars
            device: torch device
            state_file: file name to save/load the fitter state
            likelihood: likelihood object for which the fit is performed
        """
        self.params = params
        self.verbose = verbose
        self.device = device
        self.state_file = state_file
        self.likelihood = likelihood
        self.initialize()

    def initialize(self):
        """
        Can be overridden by subclasses if further initialization after the constructor is
        necessary.
        """
        pass

    def train(self):
        """
        Can be overridden by subclasses if a training step is needed before the fit starts.
        """
        pass

    @abstractmethod
    def fit(self) -> FitResults:
        """
        Function to be defined by subclasses. Runs marginalization and profiling and
        constructs FitResults object containing the results.

        Returns:
            Results of the fit
        """
        pass

    def progress(self, iterable: Iterable, **kwargs) -> Iterable:
        """
        Shows a progress bar if verbose flag is set

        Args:
            iterable: iterable object
            kwargs: keyword arguments passed on to tqdm if verbose
        Returns:
            Unchanged iterable if not verbose, otherwise wrapped by tqdm
        """
        if self.verbose:
            return tqdm(iterable, **kwargs)
        else:
            return iterable

    def print(self, text: str):
        """
        Chooses print function depending on verbosity setting

        Args:
            text: String to be printed
        """
        if self.verbose:
            tqdm.write(text)
        else:
            print(text, flush=True)

    def save(self):
        """
        Saves the state of the fitter, as specified by state_dict_attrs (attributes that have
        a stat dict) and save_attrs (attributes without a state dict). Does nothing if there
        are no attributes to be saved.
        """
        if len(self.state_dict_attrs) + len(self.save_attrs) == 0:
            return

        torch.save(
            {
                **{
                    attr: getattr(self, attr).state_dict()
                    for attr in self.state_dict_attrs
                },
                **{attr: getattr(self, attr) for attr in self.save_attrs},
            },
            self.state_file,
        )

    def load(self):
        """
        Loads the state of the fitter, as specified by state_dict_attrs (attributes that have
        a stat dict) and save_attrs (attributes without a state dict). Does nothing if there
        are no attributes to be loaded.
        """
        if len(self.state_dict_attrs) + len(self.save_attrs) == 0:
            return

        state_dicts = torch.load(self.state_file, map_location=self.device, weights_only=False)
        for attr in self.state_dict_attrs:
            try:
                getattr(self, attr).load_state_dict(state_dicts[attr])
            except AttributeError:
                pass
        for attr in self.save_attrs:
            try:
                setattr(self, attr, state_dicts[attr])
            except AttributeError:
                pass
