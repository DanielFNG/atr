from __future__ import print_function
from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

from bayes_opt import BayesianOptimization


def posterior(bo, x, xmin=0.0, xmax=10.3):
    """
    Method to aid in visualisation. See visualization.ipynb in external/BayesianOptimization/examples.

    :param bo:
        The Bayesian Optimization object.
    :param x:
        The array to use for the x dimension.

    :return:
        Mean and variance values along x based on the current belief of the objective function.
    """
    xmin, xmax = 0.0, 10.3
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

    axis.set_xlim((-2, 10))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size': 20})
    axis.set_xlabel('x', fontdict={'size': 20})

    utility = bo.util.utility(x, bo.gp, 0)
    acq.plot(x, utility, label='Utility Function', color='purple')
    acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15,
             label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
    acq.set_xlim((-2, 10))
    acq.set_ylim((0, np.max(utility) + 0.5))
    acq.set_ylabel('Utility', fontdict={'size': 20})
    acq.set_xlabel('x', fontdict={'size': 20})

    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)

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

    # Tell it to explore correctly.
    bo.explore(measurements)

    # Initialise the optimisation with the two known values of the objective function.
    #bo.maximize(init_points=2, n_iter=0, acq='ucb', kappa=5)

    # Create array of 10,000 x values linearly spaced in the range of the dependent variable.
    x = np.linspace(inputs.values()[0][0], inputs.values()[0][1], 10000).reshape(-1, 1)

    # Perform Bayesian optimisation with the given iterations, acquisition function and trade off between exploitation
    # and exploration.
    if plots:
        for i in range(iterations):
            bo.maximize(init_points=1, n_iter=0, acq=acquisition, kappa=trade_off)
            plot_gp_blind(bo, x)
    else:
        bo.maximize(init_points=iterations, n_iter=0, acq=acquisition, kappa=trade_off)
        plot_gp_blind(bo,x)

    return bo, x


# Execution script.
if __name__ == "__main__":

    # Inputs variables and their ranges. Currently assumes coupling of XoR2 thigh attachment positions (i.e. makes
    # the assumption that the best solution will have position(left_attachment) = position(right_attachment). Shank
    # attachment positions are fixed. Ranges measured manually.
    #variables = {'thigh': (0, 10.3)}

    # Two known measurements of the objective function, formatted as shown. Any two measurements will do, but it seemed
    # natural to choose the end points. The 'target' is a keyword and should not be changed.
    #measured_points = {'target': [405.10, 428.24], 'thigh': [0, 10.3]}
    #measured_points = {'thigh': [0, 10.3]}

    # Begin Bayesian Optimisation process.
    #bo_result = main(variables, measured_points, iterations=5) # Not much exploration here.
    #bo_result, domain = main(variables, measured_points, iterations=4, trade_off=5, plots=False)
    # With trade_off=7 we have more exploration than exploitation.

    # Notes: the 'plots' keyword was intended to switch on/off plotting after each step. However, doing this gets weird
    # results where after the first step the prediction stops being updated, and the 'best guesses' hardly vary at all
    # from one stage to the next. I've not figured out why this is yet, but instead I'm going to keep plots=False.
    # I can still easily get a graph at the end, and as long as I keep the returned bo_result I can later modify the
    # plot_gp_blind function to allow plotting at multiple stages during the process.

    # Plot the final result.
    #plot_gp_blind(bo_result, domain)

    bo = BayesianOptimization(prompt_function, {'x': (0, 10.3)})
    x = np.linspace(0, 10.3, 10000).reshape(-1, 1)
    bo.explore({'x': [0,10.3]})
    bo.maximize(init_points=2, n_iter=0, acq='ucb', kappa=5)#, normalize_y=True)
    plot_gp_blind(bo,x)
    bo.maximize(init_points=0, n_iter=1, acq='ucb', kappa=5)
    plot_gp_blind(bo,x)