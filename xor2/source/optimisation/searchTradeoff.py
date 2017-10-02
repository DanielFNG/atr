from __future__ import print_function
from __future__ import division

import numpy as np

from bayes_opt import BayesianOptimization


def thigh_total(x):
    return (0.002901443099453 * x ** 7 + (-0.108582947697938) * x ** 6 + 1.590490343582480 * x ** 5 + (
        -11.418714610996563) * x ** 4
            + 40.776324462043448 * x ** 3 + (-62.991806316373179) * x ** 2 + 21.796071382477542 * x + (
        5.772354116295380))/3


def shank_total(x):
    return (0.003316535284540 * x ** 7 + (-0.141420929190400) * x ** 6 + 2.413719719139595 * x ** 5 + (
        -20.950320407359662) * x ** 4
            + 96.859771488963474 * x ** 3 + (-2.275093222070007e+02) * x ** 2 + 2.316303649040210e+02 * x +
            (-70.885259395894977))/5


def optimise_and_record(bo, x, known_max_y, known_max_x, max_iter, tradeoff):
    """
    Method for carrying out Bayesian Optimisation to max_iter iterations for a given trade-off value, while recording
    the difference between the predicted max and true max at each step of the Bayesian Optimisation process. The
    parameter max_iter should be > 2 since 2 points are needed to initialise the BO.

    :param bo: The Bayesian Optimisation object to be optimised.
    :param x: The domain of the bo.
    :param known_max_y: The known maximum of the function, for training purposes.
    :param known_max_x: The known loca of the maximum of the function, for training purposes.
    :param max_iter: The number of iterations to be performed + recorded.
    :param tradeoff: The value of the exploitation-exploration tradeoff parameter.
    :return: diff_x, diff_y: recording the error in the maximum location along the x and y axes, respectively.
    """
    # Throw an error if max_iter isn't big enough.
    if max_iter <= 2:
        raise ValueError('max_iter must be greater than 2')

    # Create two empty lists to store the results.
    diff_x = []
    diff_y = []

    # Initialise the bo using 2 points.
    bo.maximize(init_points=2, n_iter=0, acq='ucb', kappa=tradeoff)

    # Maximize up to max_iter times, storing info after each iteration.
    for n_iterations in range(2, max_iter):
        bo.maximize(init_points=0, n_iter=1, kappa=tradeoff)
        mu = bo.gp.predict(x, return_std=False)
        diff_x.append(abs(np.argmax(mu) - known_max_x))
        diff_y.append(abs(np.max(mu) - known_max_y))

    return diff_x, diff_y


def main():
    # Implementation details.
    max_iter = 3
    kappas = np.linspace(0.0, 10.0, 101)  # Change tradeoff parameter from 0.0 to 10.0 by 0.1.

    # Practical measurements.
    min_thigh = 0.0
    max_thigh = 10.0
    min_shank = 0.5
    max_shank = 11.5

    # The appropriate domain.
    x_thigh = np.linspace(min_thigh, max_thigh, 10000).reshape(-1, 1)
    x_shank = np.linspace(min_shank, max_shank, 10000).reshape(-1, 1)

    # Create tables for the thigh and shank functions, used for finding their maxima and maxlocs.
    y_thigh = []
    for element in x_thigh:
        y_thigh.append(thigh_total(element))
    y_shank = []
    for element in x_shank:
        y_shank.append(shank_total(element))

    # Create structures (lists, to hold lists) which will store the overall results.
    thigh_results_bo = []
    thigh_results_x = []
    thigh_results_y = []
    shank_results_bo = []
    shank_results_x = []
    shank_results_y = []

    # For each value of the tradeoff parameter (kappa)...
    # for kappa in kappas:
    for kappa in [0.1, 0.5, 0.9]:
        # Create BayesianOptimization object for the thigh_total and shank_total functions.
        bo_thigh = BayesianOptimization(thigh_total, {'x': (min_thigh, max_thigh)})
        bo_shank = BayesianOptimization(shank_total, {'x': (min_shank, max_shank)})

        # Optimise and record.
        diff_x_thigh, diff_y_thigh = optimise_and_record(
            bo_thigh, x_thigh, max(y_thigh), y_thigh.index(max(y_thigh)), max_iter, kappa)
        diff_x_shank, diff_y_shank = optimise_and_record(
            bo_shank, x_shank, max(y_shank), y_shank.index(max(y_shank)), max_iter, kappa)
        thigh_results_bo.append(bo_thigh)
        thigh_results_x.append(diff_x_thigh)
        thigh_results_y.append(diff_y_thigh)
        shank_results_bo.append(bo_shank)
        shank_results_x.append(diff_x_shank)
        shank_results_y.append(diff_y_shank)

    return thigh_results_bo, thigh_results_x, thigh_results_y, shank_results_bo, shank_results_x, shank_results_y


if __name__ == "__main__":
    thigh_bo, thigh_x, thigh_y, shank_bo, shank_x, shank_y = main()
