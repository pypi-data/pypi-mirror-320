"""Rhys M. Adams 24.11.07"""
import multiprocessing
import itertools
import numpy as np
from joblib import Parallel, delayed
from smoothDE.estimator import density_fitter
from smoothDE.maxent import multivariate_maxent
from smoothDE.interpolator_transformer import interpolator_transformer

def apply_density_fitter(X, y, category, N, dpow, maxent):
    """Function for running density fitter, allows for parallelization.

    Args:
        X (numpy array): Numpy array features to fit.
        y (numpy array): Numpy array of classes corresponding to X
        category (set): set of classes to fit
        N (list of ints): list of gridsizes
        dpow (list of ints): derivative to use for assessing smoothing penalty
        maxent (bool): Start from higher order maximum entropy density estimate?

    Returns:
        density_fitter: fit density estimator
    """
    scales = [[np.nanmin(X[:,ind]) - np.nanstd(X[:,ind]),
               np.nanmax(X[:,ind]) + np.nanstd(X[:,ind]), N]
        for ind in range(X.shape[1])]
    points = X[y == category]
    usethis = np.all(np.isfinite(points), axis=1)
    if any(scale[0]==scale[1] for scale in scales) or (np.sum(usethis) == 0):
        dr2 = None
    else:
        dr2 = density_fitter(scales, dpow=dpow, max_val=1000)
        if maxent:
            regr = multivariate_maxent(dpow-1)
            regr.fit(points[usethis])
            phi0_fun = lambda x:-regr.predict(x)
        else:
            phi0_fun=None

        dr2.fit(points[usethis], phi0_fun=phi0_fun)
        dr2 = dr2.export_predictor()
    return dr2

class MakeSubfields(interpolator_transformer):
    """Fit sub-fields model

    Args:
        interpolator_transformer: inherits predictions from this class
    """
    def __init__(self, dpows, Ns, n_threads=1, paired=False, categories=None, maxent=False):
        """Set up basic fitting parameters

        Args:
            dpows (list of ints): derivative values for density fitter
            Ns (list of ints): grid sizes for density fitter
            n_threads (int, optional): Number of parrallel threads to use. Defaults to 1.
            paired (value of class, optional): When calculating sub-fields, 
            always subtract this class. Defaults to False.
            categories (set, optional): list of possible classifiers. Defaults to None.
            maxent (bool, optional): _description_. Defaults to False.
        """
        super().__init__(Ns,
            drs={},
            paired=paired,
            categories=categories)
        self.dpows = dpows
        if n_threads <= -1:
            n_threads = multiprocessing.cpu_count() - n_threads + 1

        self.n_threads = n_threads
        self.maxent = maxent

    def fit(self, X, y):
        """Fit sub-field model

        Args:
            X (numpy array): Features to fit, transform
            y (numpy array): Classifier response
        """
        orders = np.arange(len(self.Ns)) + 1
        make_inds = lambda order:[x
            for x in itertools.combinations_with_replacement(np.arange(X.shape[1]), order)
            if len(set(x))==order]
        categories = set(y)
        assert (self.paired is None) or (self.paired in categories), "If paired option is specified, must be in response"
        self.categories = sorted(list(categories))
        pre_inds = [tuple(sorted(list(ind)))
            for ind in itertools.chain(*[make_inds(ii) for ii in orders])]
        category_list = list(itertools.chain(*[len(pre_inds) * [cat] for cat in categories]))
        inds = pre_inds * len(categories)
        Ns = [self.Ns[len(ind) - 1] for ind in inds]
        dpows = [self.dpows[len(ind) - 1] for ind in inds]
        if self.n_threads == 1:
            temp = [apply_density_fitter(X[:, ind], y, category, N, dpow, self.maxent) for
                category, ind, N, dpow in zip(category_list, inds, Ns, dpows)]
        else:
            temp = Parallel(n_jobs=self.n_threads)(
                delayed(apply_density_fitter)(X[:, ind], y, category, N, dpow, self.maxent) for
                category, ind, N, dpow in zip(category_list, inds, Ns, dpows))
        self.drs = {(category, ind):v for
            category, ind, v in zip(category_list, inds, temp) if not v is None}
        #self.__class__ = interpolator_transformer

    def fit_transform(self, X, y):
        """Fit Transform useful for sklearn.

        Args:
            X (numpy array): Features to fit
            y (numpy array): class of features

        Returns:
            numpy array: sub-fields
        """
        self.fit(X, y)
        return self.transform(X)
