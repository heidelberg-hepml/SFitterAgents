import numpy as np
from typing import Callable, Optional
from scipy.interpolate import interp1d
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import erf


def fit_likelihood_poly(
    alphas: np.ndarray,
    likelihood: np.ndarray,
    likelihood_err: Optional[np.ndarray],
    xmin: float,
    xmax: float,
    deg: int = 4
) -> tuple[np.ndarray, np.ndarray, Callable[[np.ndarray], np.ndarray]]:
    """
    Fits a polynomial to the given likelihood points.

    Args:
        alphas: theory parameters, shape (n_points, )
        likelihood: value of the neg-log-likelihood, shape (n_points, )
        likelihood_err: error of the neg-log-likelihood, shape (n_points, ) or None
        xmin: smallest alpha to consider for the fit
        xmax: largest alpha to consider for the fit
        deg: degree of the polynomial
    Returns:
        Grid points in alpha, shape (n_grid, )
        Normalized neg-log-likelihood, shape (n_grid, )
        Fit function for normalized neg-log-likelihood
    """
    amask = (alphas >= xmin) & (alphas <= xmax)
    alphas, likelihood = alphas[amask], likelihood[amask]
    if likelihood_err is None:
        w = None
    else:
        w = 1/likelihood_err[amask]**2
    coeffs = np.polyfit(alphas, likelihood, deg, w=w)
    x = np.linspace(xmin, xmax, 1000)
    f = np.poly1d(coeffs)
    y = f(x)
    ymin = np.min(y)
    return x, y - ymin, lambda a: f(a) - ymin


def interp_likelihood_spline(
    alphas: np.ndarray, likelihood: np.ndarray
) -> tuple[np.ndarray, np.ndarray, Callable[[np.ndarray], np.ndarray]]:
    """
    Interpolates between the given likelihood points.

    Args:
        alphas: theory parameters, shape (n_points, )
        likelihood: value of the neg-log-likelihood, shape (n_points, )
    Returns:
        Grid points in alpha, shape (n_grid, )
        Normalized neg-log-likelihood, shape (n_grid, )
        Interpolated function for normalized neg-log-likelihood
    """
    f = interp1d(alphas, likelihood, kind="cubic")
    x = np.linspace(np.min(alphas), np.max(alphas), 1000)
    y = f(x)
    ymin = np.min(y)
    return x, y - ymin, lambda a: f(a) - ymin


def confidence_interval(
    alphas: np.ndarray,
    likelihood: np.ndarray,
    likelihood_err: Optional[np.ndarray] = None,
    sigma: float = 1,
    method: str = "intersect",
    estimator: str = "spline",
    x_low: Optional[float] = None,
    x_high: Optional[float] = None,
    **kwargs
) -> tuple[float, float, float]:
    """
    Interpolates between the given likelihood points.

    Args:
        alphas: theory parameters, shape (n_points, )
        likelihood: value of the neg-log-likelihood, shape (n_points, )
        likelihood_err: error of the neg-log-likelihood, shape (n_points, ) or None
        sigma: which sigma interval to compute
        method: method to compute the CI, options "intersect", "same_y", "from_point"
        estimator: method for fit/interpolation, options "spline", "poly"
        x_low: smallest alpha to consider for confidence intervals
        x_high: largest alpha to consider for confidence intervals
    Returns:
        Alpha with minimal likelihood
        Lower end of the confidence interval
        Upper end of the confidence interval
    """
    if x_low is None:
        x_low = np.min(alphas)
    if x_high is None:
        x_high = np.max(alphas)
    if estimator == "spline":
        x, y, f = interp_likelihood_spline(alphas, likelihood)
    elif estimator == "poly":
        x, y, f = fit_likelihood_poly(
            alphas, likelihood, likelihood_err, x_low, x_high, **kwargs
        )
    else:
        raise ValueError("Unknown estimator type")

    min_x = x[y == 0.][0]

    if method == "intersect":
        xc_low, xc_high = intersect_likelihood(f, sigma, x_low, x_high, min_x)
    else:
        ff = lambda a: np.exp(-f(a)/2)
        confidence = erf(sigma / np.sqrt(2))
        if method == "same_y":
            xc_low, xc_high = integ_same_y(ff, confidence, x_low, x_high)
        elif method == "from_point":
            xc_low, xc_high = integ_from_point(ff, confidence, x_low, x_high, min_x)
        else:
            raise ValueError("Unknown method")
    if xc_low is None:
        xc_low = min_x
    if xc_high is None:
        xc_high = min_x
    return min_x, xc_low, xc_high


def integ_same_y(
    f: Callable[[np.ndarray], np.ndarray],
    target_conf: float,
    x_min: float,
    x_max: float,
    steps: int = 10,
    resolution: int = 100,
) -> tuple[Optional[float], Optional[float]]:
    """
    Find two points with the same y value such that the integrated likelihood between these
    points matches target_conf.

    Args:
        f: likelihood function
        target_conf: confidence level
        x_min: smallest alpha to consider for CI
        x_max: largest alpha to consider for CI
        steps: maximum number of steps to find CI
        resolution: resolution for initial guess of intersection
    Returns:
        Lower end of CI or None if not converged
        Upper end of CI or None if not converged
    """
    int_total = quad(f, x_min, x_max)[0]
    y_min, y_max = 0, 1
    for i in range(steps):
        y = (y_max + y_min) / 2
        x = np.linspace(x_min, x_max, resolution)
        fxy = f(x) - y
        diff = np.diff(np.sign(fxy))
        try:
            idx_pos = np.where(diff == 2)[0][0]
            idx_neg = np.where(diff == -2)[0][-1]
        except IndexError:
            return None, None
        x_pos = brentq(lambda x: f(x) - y, x[idx_pos], x[idx_pos+1])
        x_neg = brentq(lambda x: f(x) - y, x[idx_neg], x[idx_neg+1])
        conf = quad(f, x_pos, x_neg)[0]
        if conf/int_total < target_conf:
            y_max = y
        else:
            y_min = y
    return x_pos, x_neg


def integ_from_point(
    f: Callable[[np.ndarray], np.ndarray],
    target_conf: float,
    x_min: float,
    x_max: float,
    x_center: float,
) -> tuple[Optional[float], Optional[float]]:
    """
    Start with central points and integrate likelihood in both directions so that the
    integrals on both sides match target_conf/2

    Args:
        f: likelihood function
        target_conf: confidence level
        x_min: smallest alpha to consider for CI
        x_max: largest alpha to consider for CI
        x_center: central point to start the integration from
    Returns:
        Lower end of CI or None if not converged
        Upper end of CI or None if not converged
    """
    int_low_total = quad(f, x_min, x_center)[0]
    int_high_total = quad(f, x_center, x_max)[0]
    low_conf_diff = lambda x_low: quad(f, x_low, x_center)[0] / int_low_total - target_conf
    high_conf_diff = lambda x_high: quad(f, x_center, x_high)[0] / int_high_total - target_conf
    try:
        x_low = brentq(low_conf_diff, x_min, x_center, xtol=1e-3)
    except ValueError:
        x_low = None
    try:
        x_high = brentq(high_conf_diff, x_center, x_max, xtol=1e-3)
    except ValueError:
        x_high = None
    return x_low, x_high


def intersect_likelihood(
    f: Callable[[np.ndarray], np.ndarray],
    sigma: float,
    x_min: float,
    x_max: float,
    x_center: float,
) -> tuple[float, float]:
    """
    Start with central points and find intersection of log-likelihood with sigma^2

    Args:
        f: log-likelihood function
        sigma: confidence sigma
        x_min: smallest alpha to consider for CI
        x_max: largest alpha to consider for CI
        x_center: central point of CI
    Returns:
        Lower end of CI or None if not converged
        Upper end of CI or None if not converged
    """
    y = sigma**2
    try:
        x_low = brentq(lambda x: f(x)-y, x_min, x_center)
    except ValueError:
        x_low = None
    try:
        x_high = brentq(lambda x: f(x)-y, x_center, x_max)
    except ValueError:
        x_high = None
    return x_low, x_high
