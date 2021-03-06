from __future__ import print_function
from __future__ import division

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib import gridspec

from bayes_opt import BayesianOptimization


# This function is a simple parabola with maximum at (5,5).
def test_objective(x, y):
    return -((x-5)**2 + (y-5)**2)


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
    mu, sigma2 = bo.gp.predict(X, eval_MSE=True)
    return mu, np.sqrt(sigma2), bo.util.utility(X, bo.gp, bo.Y.max())


def plot_2d(name=None):

    mu, s, ut = posterior(bo, X)

    fig, ax = plt.subplots(2, 2, figsize=(14, 10))
    gridsize=150

    # fig.suptitle('Bayesian Optimization in Action', fontdict={'size':30})

    # GP regression output
    ax[0][0].set_title('Gausian Process Predicted Mean', fontdict={'size':15})
    im00 = ax[0][0].hexbin(x, y, C=mu, gridsize=gridsize, cmap=cm.jet, bins=None, vmin=-0.9, vmax=2.1)
    ax[0][0].axis([x.min(), x.max(), y.min(), y.max()])
    ax[0][0].plot(bo.X[:, 1], bo.X[:, 0], 'D', markersize=4, color='k', label='Observations')

    ax[0][1].set_title('Target Function', fontdict={'size':15})
    im10 = ax[0][1].hexbin(x, y, C=z, gridsize=gridsize, cmap=cm.jet, bins=None, vmin=-0.9, vmax=2.1)
    ax[0][1].axis([x.min(), x.max(), y.min(), y.max()])
    ax[0][1].plot(bo.X[:, 1], bo.X[:, 0], 'D', markersize=4, color='k')


    ax[1][0].set_title('Gausian Process Variance', fontdict={'size':15})
    im01 = ax[1][0].hexbin(x, y, C=s, gridsize=gridsize, cmap=cm.jet, bins=None, vmin=0, vmax=1)
    ax[1][0].axis([x.min(), x.max(), y.min(), y.max()])

    ax[1][1].set_title('Acquisition Function', fontdict={'size':15})
    im11 = ax[1][1].hexbin(x, y, C=ut, gridsize=gridsize, cmap=cm.jet, bins=None, vmin=0, vmax=8)

    np.where(ut.reshape((300, 300)) == ut.max())[0]
    np.where(ut.reshape((300, 300)) == ut.max())[1]

    ax[1][1].plot([np.where(ut.reshape((300, 300)) == ut.max())[1]/50.,
                   np.where(ut.reshape((300, 300)) == ut.max())[1]/50.],
                  [0, 6],
                  'k-', lw=2, color='k')

    ax[1][1].plot([0, 6],
                  [np.where(ut.reshape((300, 300)) == ut.max())[0]/50.,
                   np.where(ut.reshape((300, 300)) == ut.max())[0]/50.],
                  'k-', lw=2, color='k')

    ax[1][1].axis([x.min(), x.max(), y.min(), y.max()])

    for im, axis in zip([im00, im10, im01, im11], ax.flatten()):
        cb = fig.colorbar(im, ax=axis)
        # cb.set_label('Value')

    if name is None:
        name = '_'

    plt.tight_layout()

    # Save or show figure?
    # fig.savefig('bo_eg_' + name + '.png')
    plt.show()
    plt.close(fig)


if __name__ == "__main__":

    # Set input parameters and initialise BO.
    description = 'testing2D'
    [min_thigh, max_thigh, thigh_label] = [0.0, 10.0, 'thigh']
    [min_shank, max_shank, shank_label] = [0.5, 11.5, 'shank']
    [x_thigh, x_shank] = [np.linspace(min_thigh, max_thigh, 10000).reshape(-1, 1),
                          np.linspace(min_shank, max_shank, 10000).reshape(-1, 1)]
    bo = BayesianOptimization(
        test_objective, {thigh_label: (min_thigh, max_thigh), shank_label: (min_shank, max_shank)})

    # For plotting.
    x = y = np.linspace(0, 6, 300)
    X, Y = np.meshgrid(x, y)
    x = X.ravel()
    y = Y.ravel()
    X = np.vstack([x, y]).T[:, [1, 0]]
    z = test_objective(x, y)
    fig, axis = plt.subplots(1, 1, figsize=(14, 10))
    gridsize = 150

    im = axis.hexbin(x, y, C=z, gridsize=gridsize, cmap=cm.jet, bins=None, vmin=-0.9, vmax=2.1)
    axis.axis([x.min(), x.max(), y.min(), y.max()])

    cb = fig.colorbar(im, )
    cb.set_label('Value')

    trade_off = 5
    max_iter = 30
    bo.maximize(init_points=2, n_iter=0, acq='ucb', kappa=trade_off)
    plot_2d("{:03}".format(len(bo.X)))
    plt.ioff()
    for n_iterations in range(2, max_iter):
        bo.maximize(init_points=0, n_iter=1, kappa=trade_off)
        plot_2d("{:03}".format(len(bo.X)))
