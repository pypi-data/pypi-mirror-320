"""Rhys M. Adams 24.11.07"""
import numpy as np
from scipy.interpolate import LinearNDInterpolator, Akima1DInterpolator
from scipy.sparse import csr_matrix,csc_matrix, diags
from sklearn.neighbors import BallTree
from sksparse.cholmod import cholesky, CholmodNotPositiveDefiniteError
from smoothDE.estimator_predictor import estimator_predictor
from smoothDE.integrate_dphidt import integrate_dphidt
from smoothDE.optimize_phi import optimize_phi
from smoothDE.find_tf import find_tf

class density_fitter(estimator_predictor):
    """Fit a density estimate.

    Args:
        estimator_predictor (_type_): inherit from predictor class
    """
    def __init__(self, box=None, dpow=2, n_ts=500, ts=None,
        tf_from_alpha0=1, nodes=None, edges=None,
        laplace_points=None, LNDI=None, max_val=100, enforce_pos_def=True,
        log_prior_coef=None, log_prior=None):
        """Initialize parameters for fitting densities

        Args:
            box (list of ints, optional): Bounding box to fit points in.
            Defaults to None.
            dpow (int, optional): Derivative used for smoothing penalty. 
            Defaults to 2.
            n_ts (int, optional): Number of smoothing penalties to sample. 
            Defaults to 500.
            ts (_type_, optional): Related to smoothing penalties to sample;
            l ~ e^-t. Defaults to None.
            tf_from_alpha0 (float, optional): Sampling stops when 
            |density * number - tf_from_alpha0| == 0
            Defaults to 1.

            These 3 parameters can be safely ignored unless you want to consider 
            unusual density geometries.
            nodes (numpy array, optional): how much each laplace point is weighted. 
            Defaults to None.
            edges (list of 2-tuples, optional): How each laplace point is connected to 
            each other. Defaults to None.
            laplace_points (numpy array, optional): Coordinate of all points to consider. 
            Defaults to None.
            
            LNDI (sklearn interpolator, optional): Interpolator to guess densities. 
            Defaults to None.
            max_val (int, optional): Clip phi=-log probability to this number. Defaults to 100.
            enforce_pos_def (bool, optional): For high smoothing penalties, the smoothing 
            penalty matrix 
            can be numerically mistaken to by not positive definite. This alters the starting 
            smoothing penalty so this doesn't happen.  Defaults to True.
            log_prior_coef (float optional) - multiply the log prior of t by this constant. If
            none, defaults to (n-alpha) / n. 0 makes a uniform prior, 1 makes
            it a powerlaw prior.
            log_prior (lambda optional) - the log prior of t. If none, defaults to 
            lambda t: dpow * t / 2
        """

        super().__init__(box, max_val, LNDI)
        self.dpow = dpow
        self.n_ts = n_ts
        self.ts = ts
        self.tf_from_alpha0 = tf_from_alpha0
        self.enforce_pos_def = enforce_pos_def
        self.edges = edges
        self.nodes = nodes

        self._set_laplace(laplace_points)
        self._set_edges(self.edges)
        self.L = self.laplace_points.max(axis=0) - self.laplace_points.min(axis=0)
        if nodes is None:
            nodes = np.array(len(self.laplace_points) * [(np.prod(self.L) / len(self.laplace_points))])

        self.ndim = self.laplace_points.shape[1]
        self.V = np.sum(self.nodes)

        self.mapper = BallTree(self.laplace_points, leaf_size=2)
        self._make_deltas()
        self.ts = ts
        self.log_prior_coef = log_prior_coef
        if log_prior is None:
            self.log_prior = lambda t: self.dpow * t / 2


    def _make_full_laplace(self, dims):
        """create a edges connection points

        Args:
            dims (list): number of gridpoints for each dimension

        Returns:
            _type_: _description_
        """
        rows = []
        cols = []
        grids = [list(range(dim)) for dim in dims]
        make_gridpoints = lambda x:np.vstack([g.ravel() for g in np.meshgrid(*x, indexing='ij')])
        def make_edges(axes, pop_list, ):
            for axis, elem in zip(axes, pop_list):
                grids[axis].pop(elem)

            gridpoints = make_gridpoints(grids)

            for axis, elem in zip(axes[::-1], pop_list[::-1]):
                if elem==0:
                    grids[axis] = [elem] + grids[axis]

                elif elem!=0:
                    grids[axis] = grids[axis] + [elem]
            return np.ravel_multi_index(gridpoints, dims=dims)

        for ii in range(len(dims)):
            cols.append(make_edges([ii], [0],))
            rows.append(make_edges([ii], [dims[ii]-1],))

        rows = np.hstack(rows)
        cols = np.hstack(cols)
        edges = np.array([rows, cols])
        return edges


    def _set_laplace(self, laplace_points):
        """Sets laplace_points if user wants to manually define them. Otherwise 
        they are constructed.

        Args:
            laplace_points (None or numpy array): Sampling coordinates where to 
            infer densities.
        """
        if laplace_points is None:
            for b in self.box:
                if len(b)<3:
                    b.append(16) #default 16 gridpoints per dimension
            bins = [np.linspace(*b) for b in self.box]
            dims = [b[2] for b in self.box]
            laplace_points = np.vstack([x.ravel() for x in np.meshgrid(*bins, indexing='ij')]).T
            self.edges = self._make_full_laplace(dims)
            self.nodes = np.array([np.prod(dims) / len(laplace_points)] * len(laplace_points))
        laplace_points = (laplace_points - self.center) / self.scale # 23.12.29
        self.laplace_points = laplace_points

    def _set_edges(self, edges):
        """Set edges if user wants to manually set them.

        Args:
            edges (list of 2 tuples): edge of laplace points to connect together
            for derivative calculation.
        """
        if edges is None:
            #connect nearby points
            kdt = BallTree(self.laplace_points, leaf_size=2, metric='euclidean')
            inds = kdt.query(self.laplace_points,
                k=np.min([self.dpow*10,len(self.laplace_points)]),
                return_distance=False)
            edges = set()
            for ind1 in range(len(inds)):
                p0 = self.laplace_points[ind1]
                ind2_candidates = []
                vector_signs = set()
                for ind2 in inds[ind1]:
                    if ind1!=ind2:
                        vector = self.laplace_points[ind2] - p0
                        vector_sign = tuple(np.sign(vector))
                        if not(vector_sign in vector_signs) and not(0 in vector_sign):
                            vector_signs.update({vector_sign})
                            ind2_candidates.append(ind2)
                for ind2 in ind2_candidates:
                    edge = tuple(sorted([ind1, ind2]))
                    edges.update(set([edge]))
            self.edges = np.array(list(edges)).T

    def export_graph(self):
        """Exports all of the elements of the laplce

        Returns:
            numpy array, list of 2-tuples, numpy array: Weight of each point,Which coordinates connect,Coordinates
            
        """
        return self.nodes, self.edges, self.laplace_points

    def _points2histogram(self, points):
        """Calculate histogram from data points

        Args:
            points (numpy array): data

        Returns:
            numpy array: empirical density of data
        """
        _, ind = self.mapper.query(points, k=1)
        histR = np.bincount(ind.ravel(),
                weights=np.ones(len(ind)),
                minlength=len(self.nodes))
        return histR

    def _integrate_dphidt(self, phi1, ts, pR, n_samples, no_delta_penalty):
        """Calculate ideal phis for each smoothing penalty.

        Args:
            phi1 (numpy array): density guess for highest smoothing penalty.
            ts (np.array): t~-np.log(l), exponential function of smoothing penalty.
            pR (numpy array): empirical density of points.
            n_samples (int): number of data points.
            no_delta_penalty (numpy array or None): Don't apply smoothing penalty to this alteration of phi

        Returns:
            ts (numpy array): function of smoothing penalties actually sampled
            phis (numpy array): best field found corresponding to ts
            dets (numpy array): determinants of Hessians for each t sampled. 
        """
        records = integrate_dphidt(phi1,
                    ts,
                    pR,
                    self.nodes,
                    self.csc_delta,
                    n_samples,
                    no_delta_penalty)
        ts = np.sort(list(records.keys()))
        #self.Qs = np.array([self.records[t][0] for t in self.ts])
        dets = np.array([records[t][1] for t in ts])
        phis = np.array([records[t][2] for t in ts])
        return ts, phis, dets

    def _optimize_phi1(self, phi0, t, pR, n_samples, no_delta_penalty):
        """Newton's method for finding phi

        Args:
            phi0 (numpy array):starting guess of optimal phi
            t (float): function of smoothing penalty.
            pR (numpy array): empirical density of data points
            n_samples (int): number of data points.
            no_delta_penalty (numpy array or None): Add to phi but don't apply smoothing penalty to these values.

        Returns:
            numpy array: estimate of phi.
        """
        if not self.LNDI is None:
            phi0 = np.clip(np.nan_to_num(self.LNDI(self.laplace_points), nan=self.max_val),
                a_min=None, a_max=self.max_val)

        beta = np.exp(-t)
        phi1 = optimize_phi(np.zeros(len(phi0)), beta, self.nodes, pR, self.csc_delta, n_samples, no_delta_penalty)
        phi1 -= (phi1.min() + 50)
        Q = np.exp(-phi1 - phi0)
        Z = (Q * self.nodes).sum()
        phi1 += np.log(Z) - 50
        self.LNDI = self._make_interpolator(phi1.ravel())
        return phi1


    def _make_deltas(self):
        """Create a matrix, Delta, so that phi.dot(Delta.dot(phi)) represents a smoothing penalty
        Diagonals are also created that can approximate D for very small smoothing penalties
        """
        values = np.sum((self.laplace_points[self.edges[0]]-self.laplace_points[self.edges[1]])**2, axis=1)**0.5
        delta = csr_matrix((-1. / values, self.edges), shape=(len(self.nodes),len(self.nodes)))

        delta += delta.T
        delta = delta.multiply(self.nodes)
        delta = delta.T
        vals = np.array(-delta.sum(axis=1)).ravel()
        diag_inds = np.arange(len(vals))

        self.delta = (delta + csr_matrix((vals, (diag_inds, diag_inds))))**self.dpow * diags(self.nodes)
        self.csc_delta = csc_matrix(self.delta )
        self.diagonals = self.csc_delta.diagonal(0)

    def _generate_ts(self, n_ts, R, n_samples, phi0):
        """make ampling points to optimize phi

        Args:
            n_ts (int): number of sampling points to make
            pR (numpy array): empirical density
            n_samples (int): number of samples collected
            phi0 (numpy array): starting phi0. Used to find where numerical issues predict a non positive definite Hessian matrix.
        """
        eff_dimensions = 2.0 * self.dpow - self.ndim
        max_D = self.csc_delta.max()
        t_i = - eff_dimensions * np.mean(np.log(self.L))
        t_f =   np.log(n_samples) + np.log(self.V) - eff_dimensions * np.sum(np.log(self.L) - np.log(len(self.nodes) /self.ndim))
        t_f = find_tf(R,
                      self.tf_from_alpha0,
                      self.diagonals,
                      n_samples,
                      mu=R,
                      neg_t0=t_f, 
                      V=self.nodes * n_samples)
        if self.enforce_pos_def:
            Q = np.exp(-phi0) * self.nodes + 1e-16
            Q /= Q.sum()
            for t_i in np.linspace(t_i, t_f, 100):
                A = self.csc_delta + (n_samples * np.exp(t_i)) * diags(Q)
                try:
                    factor = cholesky(A/max_D)
                    min_det = factor.slogdet()
                    if np.isfinite(min_det[1]):
                        break
                except CholmodNotPositiveDefiniteError:
                    pass
        #if self.tf_from_alpha0:

        self.ts = np.linspace(t_i, t_f, n_ts)

    def _max_ent_phi0(self, offset_fun):
        """find starting phi0 value for infinite smoothing penalty

        Args:
            offset_fun (lambda): starting phi0 guess for strong smoothing penalty

        Returns:
            numpy array: starting phi0
            numpy array or None: function of starting phi0
        """
        if offset_fun is None:
            phi0 = np.zeros(len(self.laplace_points))
            no_delta_penalty = None
        else:
            phi0 = offset_fun(self.laplace_points * self.scale + self.center)
            no_delta_penalty = np.array(phi0.copy())
        return phi0, no_delta_penalty

    def fit(self, points, phi0_fun=None):
        """fit density to empirical points

        Args:
            points (numpy array): data points to train model
            phi0_fun (_lambda, optional): phi0 function not 
            subject to smoothing penalty. Defaults to None.

        Returns:
            dict: key statistics during fit. ts <- sample points, phis <- optimal solutions, dets <- determinats of the Hessian of the solution, objs <- action of the solution, occams <- relative goodness of each solution, best_ind <- which solution has the highest occam score

        """
        if len(points.shape) == 1:
            points = np.array([points]).T
        points = (points - self.center) / self.scale # 23.12.29
        n_samples = len(points)
        pR = self._points2histogram(points)
        phi0, no_delta_penalty = self._max_ent_phi0(phi0_fun)
        if self.ts is None:
            self._generate_ts(self.n_ts, pR, n_samples, phi0)

        phi1 = self._optimize_phi1(phi0, self.ts[0], pR, n_samples, no_delta_penalty)
        ####################################################
        ts, phis, dets = self._integrate_dphidt(phi1, self.ts, pR, n_samples, no_delta_penalty)
        objs = np.array([self._obj(phi, t, pR, n_samples, no_delta_penalty)
                         for phi, t in zip(phis, ts)])
        if self.log_prior_coef is None:
            prior_coef = (n_samples - self.dpow) / (n_samples)
            occams = -objs  - dets / 2 + prior_coef * self.log_prior(ts)
        else:
            occams = -objs  - dets / 2 + self.log_prior_coef * self.log_prior(ts)
        ####################################################
        best_t_ind = np.nanargmax(occams)
        if no_delta_penalty is None:
            self.LNDI = self._make_interpolator(phis[best_t_ind].ravel())
        else:
            self.LNDI = self._make_interpolator(phis[best_t_ind].ravel() + no_delta_penalty.ravel())
        records = {'ts':ts, 'phis':phis, 'dets':dets,
                   'objs':objs,'occams':occams, 'best_ind':best_t_ind}
        return records

    def _make_interpolator(self, phis):
        """make interpolator used for prediction

        Args:
            phis (numpy array): the best solution

        Returns:
            interpolator: predicts phi given a coordinate
        """
        denom = self.V / np.prod([b[1]-b[0] for b in self.box])
        phis = phis + np.log(np.sum(np.exp(-phis) * self.nodes / denom ))
        if self.ndim ==1:
            out = Akima1DInterpolator(self.laplace_points.flatten(), phis.ravel())
        else:
            out = LinearNDInterpolator(self.laplace_points, phis.ravel())
        return out

    def _obj(self, phi, t, pR, n_samples, no_delta_penalty):
        """objective function/action of phi

        Args:
            phi (numpy array): value to evaluate
            t (float): a functino of smoothing penalty
            pR (numpy array): empirical density
            n_samples (int): number of samples
            no_delta_penalty (numpy array or None): 
            part of phi not subject to smoothing penalty

        Returns:
            float: action/objective values
        """
        beta = np.exp(-t)
        if no_delta_penalty is None:
            Q = np.exp(-phi)
        else:
            Q = np.exp(-phi - no_delta_penalty)
        Z = (Q * self.nodes).sum()
        myf = np.nansum(pR*(phi + np.log(Z)))
        phi = np.clip(phi, a_min=-1e10, a_max=1e10)
        d_penalty = 0.5 * (phi).T.dot(self.delta.dot(phi))
        return myf  + d_penalty * beta

    def export_predictor(self):
        """export a class capable of predictions, but not fitting.
        Much more memory efficient.

        Returns:
            estimator_predictor: predicts fit solution without all of 
            the variables and memory
        """
        return estimator_predictor(box=self.box,
                                   max_val=self.max_val,
                                   LNDI=self.LNDI)
