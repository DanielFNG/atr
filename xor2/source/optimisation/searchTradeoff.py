from __future__ import print_function
from __future__ import division

import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from matplotlib import gridspec

from bayes_opt import BayesianOptimization


def posterior(bo, x):
    """
    Method to aid in visualisation. See visualization.ipynb in external/BayesianOptimization/examples.

    :param bo:
        The Bayesian Optimization object.
    :param x:
        The array to use for the x dimension.

    :return:
        Mean and variance values along x based on the current belief of the objective function.
    """
    bo.gp.fit(bo.X, bo.Y)
    mu, sigma = bo.gp.predict(x, return_std=True)
    return mu, sigma


def plot_gp(bo, x, y):
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('{} Steps'.format(len(bo.X)), fontsize = 30)

    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    axis = plt.subplot(gs[0])
    acq = plt.subplot(gs[1])

    mu, sigma = posterior(bo, x)
    axis.plot(x, y, linewidth=3, label='Target')
    axis.plot(bo.X.flatten(), bo.Y, 'D', markersize=8, label=u'Observations', color='r')
    axis.plot(x, mu, '--', color='k', label='Prediction')

    axis.fill(np.concatenate([x, x[::-1]]),
              np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
              alpha=.6, fc='c', ec='None', label='95% confidence interval')

    fontsize = 30

    axis.set_xlim((x[0], x[-1]))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size': fontsize})
    axis.set_xlabel('x', fontdict={'size': fontsize})
    plt.rc('xtick', labelsize=8)
    plt.rc('ytick', labelsize=8)

    utility = bo.util.utility(x, bo.gp, 0)
    acq.plot(x, utility, label='Utility Function', color='purple')
    acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15,
             label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
    acq.set_xlim((x[0], x[-1]))
    acq.set_ylim((0, np.max(utility) + 0.5))
    acq.set_ylabel('Utility', fontdict={'size': fontsize})
    acq.set_xlabel('x', fontdict={'size': fontsize})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0., prop={'size': 40})
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0., prop={'size': 40})


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
        diff_x.append(abs(x.item(np.argmax(mu)) - known_max_x))
        diff_y.append(abs(np.max(mu) - known_max_y))

    return diff_x, diff_y


def main():
    # Implementation details.
    max_iter = 15
    repetitions = 10
    kappas = np.linspace(0.0, 10.0, 101)  # Change tradeoff parameter from 0.0 to 10.0 by 0.1.

    # Practical measurements.
    min_thigh = 0.0
    max_thigh = 10.0
    min_shank = 0.5
    max_shank = 11.5

    # The appropriate domain.
    x_thigh = np.linspace(min_thigh, max_thigh, 10000).reshape(-1, 1)
    x_shank = np.linspace(min_shank, max_shank, 10000).reshape(-1, 1)

    # Create tables for the thigh and shank functions, used for finding their maxima and maxlocs. Note that we take
    # the negative of the function result because we are interested in minimising!
    y_thigh = []
    for element in x_thigh:
        y_thigh.append(-thigh_total(element))
    y_shank = []
    for element in x_shank:
        y_shank.append(-shank_total(element))

    # Create structures (lists, to hold lists) which will store the overall results.
    thigh_results_x_mean = []
    thigh_results_x_std = []
    thigh_results_y_mean = []
    thigh_results_y_std = []
    shank_results_x_mean = []
    shank_results_x_std = []
    shank_results_y_mean = []
    shank_results_y_std = []

    # For each value of the tradeoff parameter (kappa)...
    for kappa in kappas:
        rep_thigh_x = []
        rep_thigh_y = []
        rep_shank_x = []
        rep_shank_y = []
        for repetition in range(repetitions):
            # Create BayesianOptimization object for the thigh_total and shank_total functions. Note that we take the
            # negative of these functions since we are minimizing rather than maximizing.
            bo_thigh = BayesianOptimization(lambda x: -thigh_total(x), {'x': (min_thigh, max_thigh)})
            bo_shank = BayesianOptimization(lambda x: -shank_total(x), {'x': (min_shank, max_shank)})

            # Optimise and record.
            diff_x_thigh, diff_y_thigh = optimise_and_record(
                bo_thigh, x_thigh, np.max(y_thigh), x_thigh.item(y_thigh.index(max(y_thigh))), max_iter, kappa)
            diff_x_shank, diff_y_shank = optimise_and_record(
                bo_shank, x_shank, np.max(y_shank), x_shank.item(y_shank.index(max(y_shank))), max_iter, kappa)

            rep_thigh_x.append(diff_x_thigh)
            rep_thigh_y.append(diff_y_thigh)
            rep_shank_x.append(diff_x_shank)
            rep_shank_y.append(diff_y_shank)

        # Transpose the rep lists, so that each individual list corresponds to the same value of max_iter.
        rep_thigh_x = list(map(list, zip(*rep_thigh_x)))
        rep_thigh_y = list(map(list, zip(*rep_thigh_y)))
        rep_shank_x = list(map(list, zip(*rep_shank_x)))
        rep_shank_y = list(map(list, zip(*rep_shank_y)))

        # For each kappa save a list of the mean and the variance of the repetition list for each case.
        thigh_results_x_mean.append([np.mean(element_list) for element_list in rep_thigh_x])
        thigh_results_x_std.append([np.std(element_list) for element_list in rep_thigh_x])
        thigh_results_y_mean.append([np.mean(element_list) for element_list in rep_thigh_y])
        thigh_results_y_std.append([np.std(element_list) for element_list in rep_thigh_y])
        shank_results_x_mean.append([np.mean(element_list) for element_list in rep_shank_x])
        shank_results_x_std.append([np.std(element_list) for element_list in rep_shank_x])
        shank_results_y_mean.append([np.mean(element_list) for element_list in rep_shank_y])
        shank_results_y_std.append([np.std(element_list) for element_list in rep_shank_y])

    # Save the results for use in matlab. For reference: the result is a matrix, the columns of which index the
    # iteration of the BO process (column 1 = iteration 1, column 2 = iteration 2, etc) and the rows of which
    # index kappa (row 1 = first value of kappa, etc...)
    sio.savemat('tradeoff_results.mat', {'thigh_x_mean': thigh_results_x_mean, 'thigh_x_std': thigh_results_x_std,
                                         'thigh_y_mean': thigh_results_y_mean, 'thigh_y_std': thigh_results_y_std,
                                         'shank_x_mean': shank_results_x_mean, 'shank_x_std': shank_results_x_std,
                                         'shank_y_mean': shank_results_y_mean, 'shank_y_std': shank_results_y_std})

    return (thigh_results_x_mean, thigh_results_x_std, thigh_results_y_mean, thigh_results_y_std,  shank_results_x_mean,
            shank_results_x_std, shank_results_y_mean, shank_results_y_std)


if __name__ == "__main__":
    #thigh_x_mean, thigh_x_std, thigh_y_mean, thigh_y_std, shank_x_mean, shank_x_std, shank_y_mean, shank_y_std = main()

    min_thigh = 0.0
    max_thigh = 10.0
    description = 'thigh-report'
    x_thigh = np.linspace(min_thigh, max_thigh, 10000).reshape(-1, 1)
    y_thigh = []
    for element in x_thigh:
        y_thigh.append(thigh_total(element)*-1)
    bo_thigh = BayesianOptimization(lambda x: -thigh_total(x), {'x': (min_thigh, max_thigh)})
    tradeoff = 8.5
    max_iter = 8
    bo_thigh.maximize(init_points=2, n_iter=0, acq='ucb', kappa=tradeoff)
    for n_iterations in range(2, max_iter):
        bo_thigh.maximize(init_points=0, n_iter=1, kappa=tradeoff)
        plot_gp(bo_thigh, x_thigh, y_thigh)
        plt.show()
        plt.savefig(description + str(n_iterations) + '.png', orientation='landscape', bbox_inches='tight')
