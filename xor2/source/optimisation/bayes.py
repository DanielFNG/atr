from __future__ import print_function
from __future__ import division

import numpy as np
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
    fig.suptitle('Gaussian Process and Utility Function After {} Steps'.format(len(bo.X)), fontdict={'size': 30})

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

    axis.set_xlim((x[0], x[-1]))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size': 20})
    axis.set_xlabel('x', fontdict={'size': 20})

    utility = bo.util.utility(x, bo.gp, 0)
    acq.plot(x, utility, label='Utility Function', color='purple')
    acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15,
             label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
    acq.set_xlim((x[0], x[-1]))
    acq.set_ylim((0, np.max(utility) + 0.5))
    acq.set_ylabel('Utility', fontdict={'size': 20})
    acq.set_xlabel('x', fontdict={'size': 20})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)


def plot_gp_blind(bo, x):
    """
    Method to aid in visualisation. See visualization.ipynb in external/BayesianOptimization/examples. This
    implementation differs in that it assumed we are going in 'blind' i.e. we don't know what the function we are trying
    to optimise for is, so we can't plot it. This is for a 1D function only.

    :param bo:
        The BayesianOptimization object currently being worked with.
    :param x:
        The array to use for the x dimension in the plots, calculated from the range of the dependent variable.
    :return:
        Nothing.
    """
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Gaussian Process and Utility Function After {} Steps'.format(len(bo.X)), fontdict={'size': 30})

    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    axis = plt.subplot(gs[0])
    acq = plt.subplot(gs[1])

    mu, sigma = posterior(bo, x)
    axis.plot(bo.X.flatten(), bo.Y, 'D', markersize=8, label=u'Observations', color='r')
    axis.plot(x, mu, '--', color='k', label='Prediction')

    axis.fill(np.concatenate([x, x[::-1]]),
              np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
              alpha=.6, fc='c', ec='None', label='95% confidence interval')

    axis.set_xlim((x[0], x[-1]))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size': 20})
    axis.set_xlabel('x', fontdict={'size': 20})

    utility = bo.util.utility(x, bo.gp, 0)
    acq.plot(x, utility, label='Utility Function', color='purple')
    acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15,
             label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
    acq.set_xlim((x[0], x[-1]))
    acq.set_ylim((np.min(utility) - 0.1, np.max(utility) + 0.1))
    acq.set_ylabel('Utility', fontdict={'size': 20})
    acq.set_xlabel('x', fontdict={'size': 20})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)


def plot_gp_blind_no_acq(bo, x):
    """
        Method to aid in visualisation. Works as plot_gp_blind but with no plot for the acquisition function.

        :param bo:
            The BayesianOptimization object currently being worked with.
        :param x:
            The array to use for the x dimension in the plots, calculated from the range of the dependent variable.
        :return:
            Nothing.
        """
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Gaussian Process and Utility Function After {} Steps'.format(len(bo.X)), fontdict={'size': 30})

    gs = gridspec.GridSpec(1, 1, height_ratios=[3])
    axis = plt.subplot(gs[0])

    mu, sigma = posterior(bo, x)
    axis.plot(bo.X.flatten(), bo.Y, 'D', markersize=8, label=u'Observations', color='r')
    axis.plot(x, mu, '--', color='k', label='Prediction')

    axis.fill(np.concatenate([x, x[::-1]]),
              np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
              alpha=.6, fc='c', ec='None', label='95% confidence interval')

    axis.set_xlim((x[0], x[-1]))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size': 20})
    axis.set_xlabel('x', fontdict={'size': 20})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)


def results_thigh(**kwargs):
    results = [47.42, 54.20, 43.61, 31.06, 89.39, 60.51, 56.38, 54.97, 59.91, 54.37, 50.90, 50.93, 88.30, 57.10,
               95.76, 56.24, 71.65, 58.19, 53.15, 50.78, 49.87]

    for key, value in kwargs.items():
        value = int(2 * value)
        return results[value] / 10 * -1  # see prompt_function


def results_shank(**kwargs):
    results = [21.79, 9.27, 10.95, 11.21, 18.42, 16.38, 16.49, 12.84, 11.22, 39.02, 34.90, 7.44]

    for key, value in kwargs.items():
        value = int(value - 0.5)
        return results[value] / 10 * -1  # see prompt_function


def prompt_function(**kwargs):
    """
    Method to prompt user for measurement of the objective function given values for the dependant variables.

    :param kwargs:
        The 'next guesses' for the link attachment positions which maximise the objective function, given as a
        dictionary of (coordinate, value) pairs.

    :return:
        The value of the objective function - handled separately - which is input by the user. For example, mean or
        total EMG.
    """
    for key, value in kwargs.items():
        print("Set the ", key, " attachment position to: ", value, sep="")
    return input(
        "Please input the resultant measured value: ") / 500 * -1  # * -1 to get the minimum, /500 to get in range


def step(bo, x, desc, num):
    bo.maximize(init_points=0, n_iter=1, acq='ucb', kappa=5)
    plot_gp_blind(bo, x)
    plt.savefig(desc + str(num) + '.png', orientation='landscape', bbox_inches='tight')


# The function definitions below are the polynomial fits to the data for the thigh and shank objective functions.
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


def main():
    # BayesianOptimization object for the thigh_total function.
    bo = BayesianOptimization(shank_total, {'x': (0.5, 11.5)})

    # The appropriate domain.
    x = np.linspace(0.5, 11.5, 10000).reshape(-1, 1)

    y = []
    for element in x:
        y.append(thigh_total(element))

    # Choose to get to within 1% accuracy, and limit to 50 iterations.
    d = 1
    max_iter = 20

    return optimise_to_tolerance(bo, x, max(y), d, max_iter)


def optimise_to_tolerance(bo, x, known_max, d, max_iter):
    """
    Method to carry out Bayesian Optimisation until the maximum of the function is found to within d%, with confidence
    of 95%. For example, if the true maximum is y we should find that:
        proposed_max in [y-d,y+d] and mean + 1.96 * sigma  < proposed_max for all x
    where mean and sigma are the mean and variance of the GP prediction for the function f. This function is intended
    for training purposes, so it is assumed we know the function f, or at least it's maximum.

    :param bo: The Bayesian Optimisation object to be optimised.
    :param x: The domain of the bo.
    :param known_max: The known maximum of the function, for training purposes.
    :param d: A measure of the accuracy we're looking for. See description.
    :param max_iter: A cutoff point to prevent getting caught in local minima.
    :return: n_iterations: the number of iterations it took to find the maximum
    """
    # Initialise the bo using 2 points.
    bo.maximize(init_points=2, n_iter=0, acq='ucb', kappa=9)

    # Maximise up to max_iter times.
    for n_iterations in range(2, max_iter + 1):
        bo.maximize(init_points=0, n_iter=1, kappa=9)
        # Check stopping criterion.
        bo.gp.fit(bo.X, bo.Y)
        mu, sigma = bo.gp.predict(x, return_std=True)
        # Get the points for which mean + variance is larger than the known maximum minus d.
        meanvar = [v for v in range(len(x)) if mu[v] + 1.9600 * sigma[v] > known_max - d]
        # From the points in meanvar, isolate those whose mean is not within d of the known maximum.
        meanonly = [v for v in meanvar if abs(known_max - mu[v]) > d]
        if len(meanvar) > 0 and len(meanonly) == 0:
            break
    # Couldn't find the maximum in the requested number of iterations.
    if n_iterations == max_iter:
        return bo, -1

    # Found the maximum in small enough iterations; return n_iterations.
    return bo, n_iterations


def optimise_and_record(bo, x, known_max, max_iter):
    """

    :param bo: The Bayesian Optimisation object to be optimised.
    :param x: The domain of the bo.
    :param known_max: The known maximum of the function, for training purposes.
    :param max_iter: The number of iterations to be performed + recorded.
    :return: diff_x, diff_y: recording the error in the maximum location along the x and y axes, respectively.
    """


# Execution script.
if __name__ == "__main__":
    bo, iterations = main()
    x = np.linspace(0, 10.0, 10000).reshape(-1,1)
    y = shank_total(x)
    plot_gp(bo, x, y)
    # plot_gp_blind_no_acq(bo,x)
    # description = 'span_thigh'
    # description = 'span_shank'
    # iterations = 10

    # bo = BayesianOptimization(prompt_function, {'x': (0, 10.0)})
    # bo = BayesianOptimization(results_thigh, {'x': (0, 10.0)})
    # bo = BayesianOptimization(results_shank, {'x': (0.5, 11.5)})

    # x = np.linspace(0, 10.0, 10000).reshape(-1, 1)
    # x = np.linspace(0.5, 11.5, 10000).reshape(-1, 1)

    # Initialise with 2 random points, and plot, then save.
    # bo.maximize(init_points=2, n_iter=0, acq='ucb', kappa=5)
    # plot_gp_blind(bo, x)
    # plt.savefig(description + '0' + '.png', orientation='landscape', bbox_inches='tight')

    # Loop through the remaining iterations, plotting and saving.
    # for i in range(iterations + 1):
    #     step(bo, x, description, i + 1)

    # Explore end points.
    # bo.explore({'x': [0, 10]})

    # Explore all measured points - thigh.
    # bo.explore(
    #     {'x': [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]})

    # Explore all measured points - shank.
    # bo.explore({'x': [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]})

    # Explore with extremely high points removed.
    # bo.explore(
    #     {'x': [0, 0.5, 1.0, 1.5, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.5, 7.5, 8.5, 9.0, 9.5, 10.0]})

    # Explore with all extreme points removed.
    # bo.explore({'x': [0, 0.5, 2.5, 3.0, 4.0, 4.5, 5.0, 6.5, 8.5, 9.0, 9.5, 10.0]})

    # bo.maximize(init_points=0, n_iter=0, acq='ucb', kappa=5)
    # plot_gp_blind(bo, x)
    # plot_gp_blind_no_acq(bo, x)
    # plt.show()
    # plt.savefig(description + '.png', orientation='landscape', bbox_inches='tight')

    # After this use step(bo, x) to step through the process from the iPython window.
