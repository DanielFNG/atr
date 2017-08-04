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
    acq.set_ylim((0, np.max(utility) + 0.5))
    acq.set_ylabel('Utility', fontdict={'size': 20})
    acq.set_xlabel('x', fontdict={'size': 20})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)


def prompt_function(values):
    """
    Method to prompt user for measurement of the objective function given values for the dependant variables.

    :param values:
        The 'next guesses' for the link attachment positions which maximise the objective function, given as a
        dictionary of (coordinate, value) pairs.

    :return:
        The value of the objective function - handled separately - which is input by the user. For example, mean or
        total EMG.
    """
    print(values.keys())
    for coordinate in values.keys():
        print("Set the ", coordinate, " attachment position to: ", values[coordinate], sep="")
    return input("Please input the resultant measured value: ")


def main(inputs, measurements, iterations=10, trade_off=5, acquisition='ucb', plots=True):
    """
    Method to carry out BO experiment for XoR2 exoskeleton.

    :param inputs:
        Dependant variables and their ranges.
    :param measurements:
        Initial measurements required to start the optimisation.
    :param iterations:
        Number of iterations to carry out.
    :param trade_off:
        Trade-off between exploitation and exploration.
    :param acquisition:
        Function to use as acquisition function.
    :param plots:
        If true, create a sequence of plots as the optimisation unfolds. Currently supports only 1D data.

    :return:
        The BayesianOptimization object after the experiment has been completed.
    """
    # Create BayesianOptimization object using a prompt_function for user-in-the-loop optimisation.
    bo = BayesianOptimization(prompt_function, inputs)

    # Initialise the optimisation with the two known values of the objective function.
    bo.initialize(measurements)

    # Perform Bayesian optimisation with the given iterations, acquisition function and trade off between exploitation
    # and exploration.
    if plots:
        # Create array of 10,000 x values linearly spaced in the range of the dependent variable.
        x = np.linspace(inputs.values()[0][0], inputs.values()[0][1], 10000).reshape(-1, 1)
        for i in range(iterations):
            bo.maximize(init_points=0, n_iter=1, acq=acquisition, kappa=trade_off)
            plot_gp_blind(bo, x)
    else:
        bo.maximize(init_points=0, n_iter=iterations, acq=acquisition, kappa=trade_off)

    return bo


# Execution script.
if __name__ == "__main__":

    # Inputs variables and their ranges. Currently assumes coupling of XoR2 thigh attachment positions (i.e. makes
    # the assumption that the best solution will have position(left_attachment) = position(right_attachment). Shank
    # attachment positions are fixed. Ranges measured manually.
    variables = {'thigh': (0, 0.13)}

    # Two known measurements of the objective function, formatted as shown. Any two measurements will do, but it seemed
    # natural to choose the end points. The 'target' is a keyword and should not be changed.
    measured_points = {'target': [0, 0], 'thigh': [0, 0.13]}

    # Begin Bayesian Optimisation process.
    bo_result = main(variables, measured_points)
