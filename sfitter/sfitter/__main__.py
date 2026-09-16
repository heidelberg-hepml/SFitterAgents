import argparse
import pickle
import os

import torch

from .util.documenter import Documenter
from .fit.fitter import Fitter
from .fit.smc_fitter import SMCFitter
from .fit.craft import CraftFitter
from .fit.flow_fitter import FlowFitter
from .eval.plots import Plots
from .likelihood.likelihood import Likelihood
from .likelihood.toy import ToyLikelihood
from .likelihood.toys2d import SpiralLikelihood, FivePointLikelihood
from .likelihood.full_likelihood import ProfileLikelihood

def main():
    """
    Main function of SFitter. Defines the command line arguments and then calls the
    suitable function based on the arguments.
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    train_parser = subparsers.add_parser("run")
    train_parser.add_argument("paramcard")
    train_parser.add_argument("--verbose", action="store_true")
    train_parser.set_defaults(func=run_new)

    plot_parser = subparsers.add_parser("fit")
    plot_parser.add_argument("run_name")
    plot_parser.add_argument("--verbose", action="store_true")
    plot_parser.set_defaults(func=lambda args: run_existing(args, fit=True))

    plot_parser = subparsers.add_parser("plot")
    plot_parser.add_argument("run_name")
    plot_parser.add_argument("--verbose", action="store_true")
    plot_parser.set_defaults(func=lambda args: run_existing(args, fit=False))

    args = parser.parse_args()
    args.func(args)


def init_run(doc: Documenter, params: dict, verbose: bool) -> tuple[Fitter, Likelihood]:
    """
    Common initialization function for the different SFitter sub-commands. Given run
    parameters, it initialized a Fitter and Likelihood object.

    Args:
        doc: Documenter instance
        params: dict with run settings
        verbose: verbosity setting
    Returns:
        fitter: Fitter instance
        likelihood: Likelihood instance
    """

    print("Welcome to SFitter :D")

    use_cuda = torch.cuda.is_available()
    print("Using device " + ("GPU" if use_cuda else "CPU"))
    device = torch.device("cuda:0" if use_cuda else "cpu")

    if params.get("precision", "single") == "double":
        torch.set_default_dtype(torch.float64)

    print("Building likelihood")
    likelihood_class = {
        "toy": ToyLikelihood,
        "spiral": SpiralLikelihood,
        "five_point": FivePointLikelihood,
        "profile": ProfileLikelihood,
    }[params["likelihood"]]
    likelihood = likelihood_class(params, device)

    print("Building fitter")
    model_file = doc.get_file("model.pth", False)
    fitter_class = {
        "smc": SMCFitter,
        "craft": CraftFitter,
        "flow": FlowFitter,
    }[params["fitter"]]
    fitter = fitter_class(params, verbose, device, model_file, likelihood)
    return fitter, likelihood


def run_new(args: argparse.Namespace):
    """
    Starts a new run from the paramcard passed as a command line argument.

    Args:
        args: command line arguments returned by the ArgumentParser
    """

    doc, params = Documenter.from_param_file(args.paramcard)
    fitter, likelihood = init_run(doc, params, args.verbose)
    fitter.train()
    fitter.save()
    results = fitter.fit()
    with open(doc.add_file("results.pkl"), "wb") as f:
        pickle.dump(results, f)
    print("Running evaluation")
    Plots.make_plots(doc, params, results)
    print("Have a nice day!")


def run_existing(args: argparse.Namespace, fit: bool):
    """
    Repeats parts of an existing run. The run name is passed as a command line argument.

    Args:
        args: command line arguments returned by the ArgumentParser
        fit: if True, repeat the fit, otherwise only the training
    """

    doc, params = Documenter.from_saved_run(args.run_name)
    fitter, likelihood = init_run(doc, params, args.verbose)
    fitter.load()
    if fit:
        print("Running fit")
        results = fitter.fit()
        with open(doc.add_file("results.pkl"), "wb") as f:
            pickle.dump(results, f)
    else:
        print("Loading fit results")
        with open(doc.get_file("results.pkl"), "rb") as f:
            results = pickle.load(f)
    print("Running evaluation")
    Plots.make_plots(doc, params, results)
    print("Have a nice day!")


if __name__ == "__main__":
    main()
