from __future__ import print_function
from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import gridspec
import matlab.engine
import pickle
import copy

from bayes_opt import BayesianOptimization

def cmc_objective(thigh, shank):
    print("Starting Matlab step.")
    result = -eng.cmcObjective(np.asscalar(thigh), np.asscalar(shank)) # Be sure to test whether you can just pass this directly below, i.e. don't need to define cmc_objective.
    print("This worked.")
    return result


def unique_rows(a):
    """
    A functions to trim repeated rows that may appear when optimizing.
    This is necessary to avoid the sklearn GP object from breaking

    :param a: array to trim repeated rows from

    :return: mask of unique rows
    """

    # Sort array and kep track of where things should go back to
    order = np.lexsort(a.T)
    reorder = np.argsort(order)

    a = a[order]
    diff = np.diff(a, axis=0)
    ui = np.ones(len(a), 'bool')
    ui[1:] = (diff != 0).any(axis=1)

    return ui[reorder]


def posterior(bo, X):
    ur = unique_rows(bo.X)
    bo.gp.fit(bo.X[ur], bo.Y[ur])
    mu, sigma2 = bo.gp.predict(X, return_std=True)
    return mu, np.sqrt(sigma2), bo.util.utility(X, bo.gp, bo.Y.max())


if __name__ == "__main__":

    # Start the MATLAB engine.
    eng = matlab.engine.start_matlab()

    # Load the saved BO object.
    bo = pickle.load(open("bo_save.p", "rb"))

    x = np.linspace(0, 10, 300)
    y = np.linspace(0.5, 11.5, 300)
    X, Y = np.meshgrid(x, y)
    x = X.ravel()
    y = Y.ravel()
    X = np.vstack([x, y]).T[:, [1, 0]]

    # Removed failed values.
    successful_values = [val for val in bo.Y if val != -1000.0]
    min_value = min(successful_values)
    for index, item in enumerate(bo.Y):
        if item == -1000.0:
            bo.Y[index] = min_value

    for i in range(2, len(bo.X)):

        co = copy.deepcopy(bo)
        co.X = co.X[0:i]
        co.Y = co.Y[0:i]

        mu, s, ut = posterior(co, X)

        fig, ax = plt.subplots(2, 2, figsize=(14, 10))
        gridsize = 150

        # fig.suptitle('Bayesian Optimization in Action', fontdict={'size':30})

        # GP regression output
        ax[0][0].set_title('Gausian Process Predicted Mean', fontdict={'size': 15})
        im00 = ax[0][0].hexbin(x, y, C=mu, gridsize=gridsize, cmap=cm.jet, bins=None)
        ax[0][0].axis([x.min(), x.max(), y.min(), y.max()])
        ax[0][0].plot(co.X[:, 1], co.X[:, 0], 'D', markersize=4, color='k', label='Observations')

        ax[1][0].set_title('Gausian Process Variance', fontdict={'size': 15})
        im01 = ax[1][0].hexbin(x, y, C=s, gridsize=gridsize, cmap=cm.jet, bins=None)
        ax[1][0].axis([x.min(), x.max(), y.min(), y.max()])

        ax[1][1].set_title('Acquisition Function', fontdict={'size': 15})
        im11 = ax[1][1].hexbin(x, y, C=ut, gridsize=gridsize, cmap=cm.jet, bins=None)

        np.where(ut.reshape((300, 300)) == ut.max())[0]
        np.where(ut.reshape((300, 300)) == ut.max())[1]

        ax[1][1].plot([np.where(ut.reshape((300, 300)) == ut.max())[1] / 50.,
                       np.where(ut.reshape((300, 300)) == ut.max())[1] / 50.],
                      [0, 11.5],
                      'k-', lw=2, color='k')

        ax[1][1].plot([0, 11.5],
                      [np.where(ut.reshape((300, 300)) == ut.max())[0] / 50.,
                       np.where(ut.reshape((300, 300)) == ut.max())[0] / 50.],
                      'k-', lw=2, color='k')

        ax[1][1].axis([x.min(), x.max(), y.min(), y.max()])

        do = copy.deepcopy(bo)
        for index, item in enumerate(do.Y):
            do.Y[index] = 100 * (do.Y[index] - min_value) / min_value * (-1)
        do.X = do.X[0:i]
        do.Y = do.Y[0:i]

        mu, s, ut = posterior(do, X)

        ax[0][1].set_title('Average Power Reduction as % Compared to Worst Case', fontdict={'size': 15})
        im10 = ax[0][1].hexbin(x, y, C=mu, gridsize=gridsize, cmap=cm.jet, bins=None)
        ax[0][1].axis([x.min(), x.max(), y.min(), y.max()])
        ax[0][1].plot(do.X[:, 1], do.X[:, 0], 'D', markersize=4, color='k')

        for im, axis in zip([im00, im10, im01, im11], ax.flatten()):
            cb = fig.colorbar(im, ax=axis)
            # cb.set_label('Value')

        plt.tight_layout()

        # Save or show figure?
        fig.savefig('gif/do_eg_' + str(i) + '.png')