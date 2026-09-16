import shutil
import warnings
from dataclasses import dataclass
from functools import wraps
from typing import Optional
import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import multivariate_normal
from scipy.signal import convolve
from scipy.ndimage import zoom
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

from ..fit.fitter import FitResults
from ..util.documenter import Documenter
from .confidence import confidence_interval

class Plots:
    """
    Class containing all the plotting methods to display the fit results.
    """

    @staticmethod
    def make_plots(doc: Documenter, params: dict, results: FitResults):
        """
        Creates a Plot instance and runs all the plotting methods.

        Args:
            doc: Documenter instance
            params: run parameters
            results: fit results
        """
        plots = Plots(params, results)
        plots.hist_weights(doc.add_file("hist_weights.pdf"))
        #plots.confidence(doc.add_file("confidence.pdf"))
        plots.hist_1d(doc.add_file("hist_1d.pdf"))
        plots.hist_2d(doc.add_file("hist_2d_marginalize.pdf"), source="marginalize")
        plots.hist_2d(doc.add_file("hist_2d_profile.pdf"), source="profile")
        plots.contour_2d(doc.add_file("contour_2d.pdf"))
        plots.triangle(doc.add_file("triangle.pdf"))

    def __init__(self, params: dict, results: FitResults):
        """
        Initializes Plot object and sets matplotlib settings.

        Args:
            params: run parameters
            results: fit results
        """

        self.params = params
        self.results = results

        plt.rc("font", family="serif", size=16)
        plt.rc("axes", titlesize="medium")
        # PATCHED: usetex only when a latex binary exists. Neither this container
        # nor the compute-node sandbox ships one, and matplotlib raises
        # "Failed to process string with tex because latex could not be found"
        # at the first text render -- which is inside make_plots, i.e. AFTER the
        # fit completes, discarding a finished result. Fall back to mathtext.
        _has_latex = shutil.which("latex") is not None
        if _has_latex:
            plt.rc("text.latex", preamble=r"\usepackage{amsmath}")
        plt.rc("text", usetex=_has_latex)
        self.colors = [f"C{i}" for i in range(10)]

    def confidence(self, file: str):
        """
        Computes and plots confidence intervals for profiled and marginal likelihood.

        Args:
            file: Output file name
        """
        fig, ax = plt.subplots(figsize=(6.,4.))
        x_range = np.arange(len(self.results.parameters))
        for j, (points, data) in enumerate([
            (self.results.marginal_1d_points, self.results.marginal_1d),
            (self.results.profile_1d_points, self.results.profile_1d)
        ]):
            best = [[], []]
            ci = [[], []]
            for parameter in self.results.parameters:
                for sigma in range(1, 3):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        x_best, x_low, x_high = confidence_interval(
                            points[parameter],
                            -2. * np.log(np.maximum(data[parameter], 1e-15)),
                            sigma=sigma,
                            method="same_y",
                            estimator="spline",
                        )
                    best[sigma-1].append(x_best)
                    ci[sigma-1].append([x_best - x_low, x_high - x_best])
            for i in range(2):
                ax.errorbar(
                    x_range + 0.2 * j - 0.1,
                    best[i],
                    yerr=np.array(ci[i]).T,
                    ls="none",
                    capsize=5.,
                    lw=2 - i,
                    color=self.colors[j],
                    label=["marginal", "profile"][j] if i == 1 else None,
                )
        ax.axhline(0, color="k", lw=1)
        ax.set_xticks(x_range)
        ax.set_xticklabels(self.results.parameters)
        ax.legend(frameon=False)
        plt.savefig(file, format="pdf", bbox_inches="tight")
        plt.close()

    def hist_weights(self, file: str):
        """
        Plots histogram of sampled weights

        Args:
            file: Output file name
        """
        with PdfPages(file) as pdf:
            fig, ax = plt.subplots(figsize=(4.5,4.25))
            ax.stairs(
                self.results.w_hist_lin / np.max(self.results.w_hist_lin),
                edges=self.results.w_bins_lin,
                color=self.colors[0],
            )
            ax.axvline(1, lw=1, color="grey")
            ax.set_xlabel("weight")
            ax.set_ylabel("normalized")
            plt.savefig(pdf, format="pdf", bbox_inches="tight")
            plt.close()

            fig, ax = plt.subplots(figsize=(4.5,4.25))
            ax.stairs(
                self.results.w_hist_log / np.max(self.results.w_hist_log),
                edges=self.results.w_bins_log,
                color=self.colors[0],
            )
            ax.axvline(1, lw=1, color="grey")
            ax.set_xlabel("weight")
            ax.set_ylabel("normalized")
            ax.set_xscale("log")
            ax.set_yscale("log")
            plt.savefig(pdf, format="pdf", bbox_inches="tight")
            plt.close()

    def hist_1d(self, file: str):
        """
        Plots 1D profiled and marginal likelihoods for all parameters.

        Args:
            file: Output file name
        """
        with PdfPages(file) as pdf:
            for parameter in self.results.parameters:
                fig, ax = plt.subplots(figsize=(4.5,4.25))
                marginal = self.results.marginal_1d[parameter]
                ax.plot(
                    self.results.marginal_1d_points[parameter],
                    marginal / np.max(marginal),
                    label="marginal",
                    color=self.colors[0],
                )
                #ax.stairs(
                #    marginal / np.max(marginal),
                #    edges=self.results.bins[parameter],
                #    label="marginal",
                #    color=self.colors[0],
                #)
                profile = self.results.profile_1d[parameter]
                ax.plot(
                    self.results.profile_1d_points[parameter],
                    profile / np.max(profile),
                    label="profile",
                    color=self.colors[1],
                )
                ax.legend(frameon=False)
                ax.set_xlabel(parameter)
                ax.set_ylabel("normalized")
                plt.savefig(pdf, format="pdf", bbox_inches="tight")
                plt.close()

    def hist_2d(self, file: str, source: str):
        """
        Plots 2D profiled and marginal likelihoods for all pairs of parameters.

        Args:
            file: Output file name
        """
        with PdfPages(file) as pdf:
            n_params = len(self.results.parameters)
            for i in range(n_params - 1):
                for j in range(i + 1, n_params):
                    x_param = self.results.parameters[i]
                    y_param = self.results.parameters[j]

                    fig, ax = plt.subplots(figsize=(4.5,4.25))
                    if source == "marginalize":
                        data = self.results.marginal_2d[(x_param, y_param)]
                        bins = self.results.marginal_2d_bins
                    elif source == "profile":
                        data = self.results.profile_2d[(x_param, y_param)]
                        bins = self.results.profile_2d_bins
                    grid_x, grid_y = np.meshgrid(bins[x_param], bins[y_param])
                    ax.pcolormesh(grid_x, grid_y, data.T, rasterized=True)
                    ax.set_xlabel(x_param)
                    ax.set_ylabel(y_param)
                    plt.savefig(pdf, format="pdf", bbox_inches="tight")
                    plt.close()

    def plot_contour(
        self,
        ax: mpl.axes.Axes,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        color: str,
        smooth: bool = False,
        upsampling: float | None = None
    ):
        """
        Make contour plot from the given x and y coordinates and function values. Optionally
        apply smoothing or interpolation.

        Args:
            ax: matplotlib axes
            x: x coordinates, shape (n_bins, )
            y: y coordinates, shape (n_bins, )
            z: function values, shape (n_bins, n_bins)
            color: matplotlib color string
            smooth: if True, apply kernel density estimation to smooth function
            upsampling: if not None, increase number of points by the given factor using
                interpolation
        """
        confidence = np.array([0.95450, 0.68269])
        hist = z.flatten()
        hist_idx = np.argsort(hist.flatten())[::-1]
        hist_sorted = hist[hist_idx]
        hist_cumsum = np.cumsum(hist_sorted)
        levels = hist_sorted[
            np.argmax(hist_cumsum[:,None] / hist_cumsum[-1] >= confidence[None,:], axis=0)
        ]

        if smooth:
            std_factor = 1.06 / self.results.marginal_effective_size**(1/5)
            cov = np.cov(np.stack(
                np.meshgrid(np.arange(len(x)), np.arange(len(y))), axis=0
            ).reshape(2,-1), aweights=hist) * std_factor**2
            kernel_size = int(8 * np.sqrt(np.max(np.diag(cov)))) // 2 * 2 + 1
            if kernel_size > 1:
                kernel_coords = np.stack(
                    np.meshgrid(np.arange(kernel_size), np.arange(kernel_size)), axis=2
                )
                kernel = multivariate_normal(
                    [kernel_size // 2, kernel_size // 2], cov
                ).pdf(kernel_coords)
                z = convolve(z, kernel / np.sum(kernel), "same")

        if upsampling is not None:
            z = zoom(z, upsampling)
            x = np.linspace(x[0], x[-1], z.shape[0])
            y = np.linspace(y[0], y[-1], z.shape[1])

        ax.contour(x, y, z.T, levels, colors=color, linestyles=["dashed", "solid"])

    def contour_2d(self, file: str):
        """
        Plots contours of profiled and marginal likelihoods for all pairs of parameters.

        Args:
            file: Output file name
        """
        with PdfPages(file) as pdf:
            n_params = len(self.results.parameters)
            for i in range(n_params - 1):
                for j in range(i + 1, n_params):
                    x_param = self.results.parameters[i]
                    y_param = self.results.parameters[j]

                    fig, ax = plt.subplots(figsize=(4.5,4.25))
                    self.plot_contour(
                        ax=ax,
                        x=self.results.marginal_2d_points[x_param],
                        y=self.results.marginal_2d_points[y_param],
                        z=self.results.marginal_2d[(x_param, y_param)],
                        color=self.colors[0],
                        #smooth=True,
                        upsampling=3.,
                    )
                    self.plot_contour(
                        ax=ax,
                        x=self.results.profile_2d_points[x_param],
                        y=self.results.profile_2d_points[y_param],
                        z=self.results.profile_2d[(x_param, y_param)],
                        color=self.colors[1],
                        upsampling=3.,
                    )
                    ax.set_xlabel(x_param)
                    ax.set_ylabel(y_param)
                    #ax.legend([
                    #    Line2D([0], [0], color=self.colors[0]),
                    #    Line2D([0], [0], color=self.colors[1]),
                    #], ["marginal", "profile"], frameon=False)
                    plt.savefig(pdf, format="pdf", bbox_inches="tight")
                    plt.close()

    def triangle(self, file: str):
        """
        Plots triangle with 1D and contour plots for all parameters/pairs of parameters.

        Args:
            file: Output file name
        """
        n_params = len(self.results.parameters)
        fig, axs = plt.subplots(n_params, n_params, figsize=(3 * n_params, 3 * n_params))
        for i in range(n_params - 1):
            for j in range(i + 1, n_params):
                x_param = self.results.parameters[i]
                y_param = self.results.parameters[j]

                axs[i][j].axis("off")
                if i == 0 and j == n_params - 1:
                    axs[i][j].legend([
                        Line2D([0], [0], color=self.colors[0]),
                        Line2D([0], [0], color=self.colors[1]),
                    ], ["marginal", "profile"], frameon=False)

                ax = axs[j][i]
                self.plot_contour(
                    ax=ax,
                    x=self.results.marginal_2d_points[x_param],
                    y=self.results.marginal_2d_points[y_param],
                    z=self.results.marginal_2d[(x_param, y_param)],
                    color=self.colors[0],
                    #smooth=True,
                    upsampling=3.,
                )
                self.plot_contour(
                    ax=ax,
                    x=self.results.profile_2d_points[x_param],
                    y=self.results.profile_2d_points[y_param],
                    z=self.results.profile_2d[(x_param, y_param)],
                    color=self.colors[1],
                    upsampling=3.,
                )
                if j == n_params - 1:
                    ax.set_xlabel(x_param)
                if i == 0:
                    ax.set_ylabel(y_param)

        for i in range(n_params):
            ax = axs[i][i]
            parameter = self.results.parameters[i]
            marginal = self.results.marginal_1d[parameter]
            #ax.stairs(
            #    marginal / np.max(marginal),
            #    edges=self.results.bins[parameter],
            #    color=self.colors[0],
            #)
            ax.plot(
                self.results.marginal_1d_points[parameter],
                marginal / np.max(marginal),
                color=self.colors[0],
            )
            profile = self.results.profile_1d[parameter]
            ax.plot(
                self.results.profile_1d_points[parameter],
                profile / np.max(profile),
                color=self.colors[1],
            )
            if i == n_params - 1:
                ax.set_xlabel(parameter)
        fig.tight_layout()
        plt.savefig(file, format="pdf", bbox_inches="tight")
        plt.close()
