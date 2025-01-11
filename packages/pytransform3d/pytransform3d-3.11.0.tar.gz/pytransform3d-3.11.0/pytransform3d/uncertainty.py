"""Operations related to uncertain transformations.

See :doc:`user_guide/uncertainty` for more information.
"""
import numpy as np

from ._geometry import unit_sphere_surface_grid
from .batch_rotations import (axis_angles_from_matrices,
                              matrices_from_compact_axis_angles)
from .trajectories import (concat_many_to_one,
                           exponential_coordinates_from_transforms,
                           transforms_from_exponential_coordinates)
from .transformations import (
    adjoint_from_transform, concat, exponential_coordinates_from_transform,
    invert_transform, left_jacobian_SE3_inv, transform_from,
    transform_from_exponential_coordinates)


def estimate_gaussian_rotation_matrix_from_samples(samples):
    """Estimate Gaussian distribution over rotations from samples.

    Computes the Fréchet mean of the samples and the covariance in tangent
    space (exponential coordinates of rotation / rotation vectors) using an
    unbiased estimator as outlines by Eade [1]_.

    Parameters
    ----------
    samples : array-like, shape (n_samples, 3, 3)
        Sampled rotations represented by rotation matrices.

    Returns
    -------
    mean : array, shape (3, 3)
        Mean of the Gaussian distribution as rotation matrix.

    cov : array, shape (3, 3)
        Covariance of the Gaussian distribution in exponential coordinates.

    See Also
    --------
    frechet_mean
        Algorithm used to compute the mean of the Gaussian.

    References
    ----------
    .. [1] Eade, E. (2017). Lie Groups for 2D and 3D Transformations.
       https://ethaneade.com/lie.pdf
    """
    def compact_axis_angles_from_matrices(Rs):
        A = axis_angles_from_matrices(Rs)
        return A[:, :3] * A[:, 3, np.newaxis]

    mean, mean_diffs = frechet_mean(
        samples=samples,
        mean0=samples[0],
        exp=matrices_from_compact_axis_angles,
        log=compact_axis_angles_from_matrices,
        inv=lambda R: R.T,
        concat_one_to_one=lambda R1, R2: np.dot(R2, R1),
        concat_many_to_one=concat_many_to_one,
        n_iter=20
    )

    cov = np.cov(mean_diffs, rowvar=False, bias=True)
    return mean, cov


def estimate_gaussian_transform_from_samples(samples):
    """Estimate Gaussian distribution over transformations from samples.

    Computes the Fréchet mean of the samples and the covariance in tangent
    space (exponential coordinates of transformation) using an unbiased
    estimator as outlines by Eade [1]_.

    Parameters
    ----------
    samples : array-like, shape (n_samples, 4, 4)
        Sampled transformations represented by homogeneous matrices.

    Returns
    -------
    mean : array, shape (4, 4)
        Mean as homogeneous transformation matrix.

    cov : array, shape (6, 6)
        Covariance of distribution in exponential coordinate space.

    See Also
    --------
    frechet_mean
        Algorithm used to compute the mean of the Gaussian.

    References
    ----------
    .. [1] Eade, E. (2017). Lie Groups for 2D and 3D Transformations.
       https://ethaneade.com/lie.pdf
    """
    mean, mean_diffs = frechet_mean(
        samples=samples,
        mean0=samples[0],
        exp=transforms_from_exponential_coordinates,
        log=exponential_coordinates_from_transforms,
        inv=invert_transform,
        concat_one_to_one=concat,
        concat_many_to_one=concat_many_to_one,
        n_iter=20
    )

    cov = np.cov(mean_diffs, rowvar=False, bias=True)
    return mean, cov


def frechet_mean(
        samples, mean0, exp, log, inv, concat_one_to_one, concat_many_to_one,
        n_iter=20):
    r"""Compute the Fréchet mean of samples on a smooth Riemannian manifold.

    The mean is computed with an iterative optimization algorithm [1]_ [2]_:

    1. For a set of samples :math:`\{x_1, \ldots, x_n\}`, we initialize
       the estimated mean :math:`\bar{x}_0`, e.g., as :math:`x_1`.
    2. For a fixed number of steps :math:`K`, in each iteration :math:`k` we
       improve the estimation of the mean by

       a. Computing the distance of each sample to the current estimate of the
          mean in tangent space with
          :math:`d_{i,k} \leftarrow \log (x_i \cdot \bar{x}_k^{-1})`.
       b. Updating the estimate of the mean with
          :math:`\bar{x}_{k+1} \leftarrow
          \exp(\frac{1}{N}\sum_i d_{i,k}) \cdot \bar{x}_k`.

    3. Return :math:`\bar{x}_K`.

    Parameters
    ----------
    samples : array-like, shape (n_samples, ...)
        Samples on a smooth Riemannian manifold.

    mean0 : array-like, shape (...)
        Initial guess for the mean on the manifold.

    exp : callable
        Exponential map from the tangent space to the manifold.

    log : callable
        Logarithmic map from the manifold to the tangent space.

    inv : callable
        Computes the inverse of an element on the manifold.

    concat_one_to_one : callable
        Concatenates elements on the manifold.

    concat_many_to_one : callable
        Concatenates multiple elements on the manifold to one element on the
        manifold.

    n_iter : int, optional (default: 20)
        Number of iterations of the optimization algorithm.

    Returns
    -------
    mean : array, shape (...)
        Fréchet mean on the manifold.

    mean_diffs : array, shape (n_samples, n_tangent_space_components)
        Differences between the mean and the samples in the tangent space.
        These can be used to compute the covariance. They are returned to
        avoid recomputing them.

    See Also
    --------
    estimate_gaussian_rotation_matrix_from_samples
        Uses the Frechet mean to compute the mean of a Gaussian distribution
        over rotations.

    estimate_gaussian_transform_from_samples
        Uses the Frechet mean to compute the mean of a Gaussian distribution
        over transformations.

    References
    ----------
    .. [1] Fréchet, M. (1948). Les éléments aléatoires de nature quelconque
       dans un espace distancié. Annales de l’Institut Henri Poincaré, 10(3),
       215–310.

    .. [2] Pennec, X. (2006). Intrinsic Statistics on Riemannian Manifolds:
       Basic Tools for Geometric Measurements. J Math Imaging Vis 25, 127-154.
       https://doi.org/10.1007/s10851-006-6228-4
    """
    assert len(samples) > 0
    samples = np.asarray(samples)
    mean = np.copy(mean0)
    for _ in range(n_iter):
        mean_diffs = log(concat_many_to_one(samples, inv(mean)))
        avg_mean_diff = np.mean(mean_diffs, axis=0)
        mean = concat_one_to_one(mean, exp(avg_mean_diff))
    return mean, mean_diffs


def invert_uncertain_transform(mean, cov):
    r"""Invert uncertain transform.

    For the mean :math:`\boldsymbol{T}_{BA}`, the inverse is simply
    :math:`\boldsymbol{T}_{BA}^{-1} = \boldsymbol{T}_{AB}`.

    For the covariance, we need the adjoint of the inverse transformation
    :math:`\left[Ad_{\boldsymbol{T}_{BA}^{-1}}\right]`:

    .. math::

        \boldsymbol{\Sigma}_{\boldsymbol{T}_{AB}}
        =
        \left[Ad_{\boldsymbol{T}_{BA}^{-1}}\right]
        \boldsymbol{\Sigma}_{\boldsymbol{T}_{BA}}
        \left[Ad_{\boldsymbol{T}_{BA}^{-1}}\right]^T

    Parameters
    ----------
    mean : array-like, shape (4, 4)
        Mean of transform from frame A to frame B.

    cov : array, shape (6, 6)
        Covariance of transform from frame A to frame B in exponential
        coordinate space.

    Returns
    -------
    mean_inv : array, shape (4, 4)
        Mean of transform from frame B to frame A.

    cov_inv : array, shape (6, 6)
        Covariance of transform from frame B to frame A in exponential
        coordinate space.

    See Also
    --------
    pytransform3d.transformations.invert_transform :
        Invert transformation without uncertainty.

    References
    ----------
    .. [1] Mangelson, G., Vasudevan, E. (2019). Characterizing the Uncertainty
       of Jointly Distributed Poses in the Lie Algebra,
       https://arxiv.org/pdf/1906.07795.pdf
    """
    mean_inv = invert_transform(mean)
    ad_inv = adjoint_from_transform(mean_inv)
    cov_inv = np.dot(ad_inv, np.dot(cov, ad_inv.T))
    return mean_inv, cov_inv


def concat_globally_uncertain_transforms(mean_A2B, cov_A2B, mean_B2C, cov_B2C):
    r"""Concatenate two independent globally uncertain transformations.

    We assume that the two distributions are independent.

    Each of the two transformations is globally uncertain (not in the local /
    body frame), that is, samples are generated through

    .. math::

        \boldsymbol{T} = Exp(\boldsymbol{\xi}) \overline{\boldsymbol{T}},

    where :math:`\boldsymbol{T} \in SE(3)` is a sampled transformation matrix,
    :math:`\overline{\boldsymbol{T}} \in SE(3)` is the mean transformation,
    and :math:`\boldsymbol{\xi} \in \mathbb{R}^6` are exponential coordinates
    of transformations and are distributed according to a Gaussian
    distribution with zero mean and covariance :math:`\boldsymbol{\Sigma} \in
    \mathbb{R}^{6 \times 6}`, that is, :math:`\boldsymbol{\xi} \sim
    \mathcal{N}(\boldsymbol{0}, \boldsymbol{\Sigma})`.

    The concatenation order is the same as in
    :func:`~pytransform3d.transformations.concat`, that is, the transformation
    B2C is left-multiplied to A2B. Note that the order of arguments is
    different from
    :func:`~pytransform3d.uncertainty.concat_locally_uncertain_transforms`.

    Hence, the full model is

    .. math::

        Exp(_C\boldsymbol{\xi'}) \overline{\boldsymbol{T}}_{CA} =
        Exp(_C\boldsymbol{\xi}) \overline{\boldsymbol{T}}_{CB}
        Exp(_B\boldsymbol{\xi}) \overline{\boldsymbol{T}}_{BA},

    where :math:`_B\boldsymbol{\xi} \sim \mathcal{N}(\boldsymbol{0},
    \boldsymbol{\Sigma}_{BA})`, :math:`_C\boldsymbol{\xi} \sim
    \mathcal{N}(\boldsymbol{0}, \boldsymbol{\Sigma}_{CB})`, and
    :math:`_C\boldsymbol{\xi'} \sim \mathcal{N}(\boldsymbol{0},
    \boldsymbol{\Sigma}_{CA})`.

    This version of Barfoot and Furgale [1]_ approximates the covariance up to
    4th-order terms. Note that it is still an approximation of the covariance
    after concatenation of the two transforms.

    Parameters
    ----------
    mean_A2B : array, shape (4, 4)
        Mean of transform from A to B.

    cov_A2B : array, shape (6, 6)
        Covariance of transform from A to B. Models uncertainty in frame B.

    mean_B2C : array, shape (4, 4)
        Mean of transform from B to C.

    cov_B2C : array, shape (6, 6)
        Covariance of transform from B to C. Models uncertainty in frame C.

    Returns
    -------
    mean_A2C : array, shape (4, 4)
        Mean of new pose.

    cov_A2C : array, shape (6, 6)
        Covariance of new pose. Models uncertainty in frame C.

    See Also
    --------
    concat_locally_uncertain_transforms :
        Concatenate two independent locally uncertain transformations.

    pytransform3d.transformations.concat :
        Concatenate two transformations.

    References
    ----------
    .. [1] Barfoot, T. D., Furgale, P. T. (2014).
       Associating Uncertainty With Three-Dimensional Poses for Use in
       Estimation Problems. IEEE Transactions on Robotics, 30(3), pp. 679-693,
       doi: 10.1109/TRO.2014.2298059.
    """
    mean_A2C = concat(mean_A2B, mean_B2C)

    ad_B2C = adjoint_from_transform(mean_B2C)
    cov_A2B_in_C = np.dot(ad_B2C, np.dot(cov_A2B, ad_B2C.T))
    second_order_terms = cov_B2C + cov_A2B_in_C

    cov_A2C = second_order_terms + _compound_cov_fourth_order_terms(
        cov_B2C, cov_A2B_in_C)

    return mean_A2C, cov_A2C


def _compound_cov_fourth_order_terms(cov1, cov2_prime):
    cov1 = _swap_cov(cov1)
    cov2_prime = _swap_cov(cov2_prime)

    cov1_11 = cov1[:3, :3]
    cov1_22 = cov1[3:, 3:]
    cov1_12 = cov1[:3, 3:]

    cov2_11 = cov2_prime[:3, :3]
    cov2_22 = cov2_prime[3:, 3:]
    cov2_12 = cov2_prime[:3, 3:]

    A1 = np.block([
        [_covop1(cov1_22), _covop1(cov1_12 + cov1_12.T)],
        [np.zeros((3, 3)), _covop1(cov1_22)]
    ])
    A2 = np.block([
        [_covop1(cov2_22), _covop1(cov2_12 + cov2_12.T)],
        [np.zeros((3, 3)), _covop1(cov2_22)]
    ])
    B_11 = (_covop2(cov1_22, cov2_11) + _covop2(cov1_12.T, cov2_12)
            + _covop2(cov1_12, cov2_12.T) + _covop2(cov1_11, cov2_22))
    B_12 = _covop2(cov1_22, cov2_12.T) + _covop2(cov1_12.T, cov2_22)
    B_22 = _covop2(cov1_22, cov2_22)
    B = np.block([
        [B_11, B_12],
        [B_12.T, B_22]
    ])

    return _swap_cov(
        (np.dot(A1, cov2_prime) + np.dot(cov2_prime, A1.T)
         + np.dot(A2, cov1) + np.dot(cov1, A2.T)) / 12.0
        + B / 4.0
    )


def _swap_cov(cov):
    return np.block([
        [cov[3:, 3:], cov[3:, :3]],
        [cov[:3, 3:], cov[:3, :3]]
    ])


def _covop1(A):
    return -np.trace(A) * np.eye(len(A)) + A


def _covop2(A, B):
    return np.dot(_covop1(A), _covop1(B)) + _covop1(np.dot(B, A))


def concat_locally_uncertain_transforms(mean_A2B, mean_B2C, cov_A, cov_B):
    r"""Concatenate two independent locally uncertain transformations.

    We assume that the two distributions are independent.

    Each of the two transformations is locally uncertain (not in the global /
    world frame), that is, samples are generated through

    .. math::

        \boldsymbol{T} = \overline{\boldsymbol{T}} Exp(\boldsymbol{\xi}),

    where :math:`\boldsymbol{T} \in SE(3)` is a sampled transformation matrix,
    :math:`\overline{\boldsymbol{T}} \in SE(3)` is the mean transformation,
    and :math:`\boldsymbol{\xi} \in \mathbb{R}^6` are exponential coordinates
    of transformations and are distributed according to a Gaussian
    distribution with zero mean and covariance :math:`\boldsymbol{\Sigma} \in
    \mathbb{R}^{6 \times 6}`, that is, :math:`\boldsymbol{\xi} \sim
    \mathcal{N}(\boldsymbol{0}, \boldsymbol{\Sigma})`.

    The concatenation order is the same as in
    :func:`~pytransform3d.transformations.concat`, that is, the transformation
    B2C is left-multiplied to A2B. Note that the order of arguments is
    different from
    :func:`~pytransform3d.uncertainty.concat_globally_uncertain_transforms`.

    Hence, the full model is

    .. math::

        \overline{\boldsymbol{T}}_{CA} Exp(_A\boldsymbol{\xi'}) =
        \overline{\boldsymbol{T}}_{CB} Exp(_B\boldsymbol{\xi})
        \overline{\boldsymbol{T}}_{BA} Exp(_A\boldsymbol{\xi}),

    where :math:`_B\boldsymbol{\xi} \sim \mathcal{N}(\boldsymbol{0},
    \boldsymbol{\Sigma}_B)`, :math:`_A\boldsymbol{\xi} \sim
    \mathcal{N}(\boldsymbol{0}, \boldsymbol{\Sigma}_A)`, and
    :math:`_A\boldsymbol{\xi'} \sim \mathcal{N}(\boldsymbol{0},
    \boldsymbol{\Sigma}_{A,total})`.

    This version of Meyer et al. [1]_ approximates the covariance up to
    2nd-order terms.

    Parameters
    ----------
    mean_A2B : array, shape (4, 4)
        Mean of transform from A to B: :math:`\overline{\boldsymbol{T}}_{BA}`.

    mean_B2C : array, shape (4, 4)
        Mean of transform from B to C: :math:`\overline{\boldsymbol{T}}_{CB}`.

    cov_A : array, shape (6, 6)
        Covariance of noise in frame A: :math:`\boldsymbol{\Sigma}_A`. Noise
        samples are right-multiplied with the mean transform A2B.

    cov_B : array, shape (6, 6)
        Covariance of noise in frame B: :math:`\boldsymbol{\Sigma}_B`. Noise
        samples are right-multiplied with the mean transform B2C.

    Returns
    -------
    mean_A2C : array, shape (4, 4)
        Mean of new pose.

    cov_A_total : array, shape (6, 6)
        Covariance of accumulated noise in frame A.

    See Also
    --------
    concat_globally_uncertain_transforms :
        Concatenate two independent globally uncertain transformations.

    pytransform3d.transformations.concat :
        Concatenate two transformations.

    References
    ----------
    .. [1] Meyer, L., Strobl, K. H., Triebel, R. (2022). The Probabilistic
       Robot Kinematics Model and its Application to Sensor Fusion.
       In IEEE/RSJ International Conference on Intelligent Robots and Systems
       (IROS), Kyoto, Japan (pp. 3263-3270),
       doi: 10.1109/IROS47612.2022.9981399.
       https://elib.dlr.de/191928/1/202212_ELIB_PAPER_VERSION_with_copyright.pdf
    """
    mean_A2C = concat(mean_A2B, mean_B2C)

    ad_B2A = adjoint_from_transform(invert_transform(mean_A2B))
    cov_B_in_A = np.dot(ad_B2A, np.dot(cov_B, ad_B2A.T))
    cov_A_total = cov_B_in_A + cov_A

    return mean_A2C, cov_A_total


def pose_fusion(means, covs):
    """Fuse Gaussian distributions of multiple poses.

    Parameters
    ----------
    means : array-like, shape (n_poses, 4, 4)
        Homogeneous transformation matrices.

    covs : array-like, shape (n_poses, 6, 6)
        Covariances of pose distributions in exponential coordinate space.

    Returns
    -------
    mean : array, shape (4, 4)
        Fused pose mean.

    cov : array, shape (6, 6)
        Fused pose covariance.

    V : float
        Error of optimization objective.

    References
    ----------
    .. [1] Barfoot, T. D., Furgale, P. T. (2014).
       Associating Uncertainty With Three-Dimensional Poses for Use in
       Estimation Problems. IEEE Transactions on Robotics, 30(3), pp. 679-693,
       doi: 10.1109/TRO.2014.2298059.
    """
    n_poses = len(means)
    covs_inv = [np.linalg.inv(cov) for cov in covs]

    mean = np.eye(4)
    LHS = np.empty((6, 6))
    RHS = np.empty(6)
    for _ in range(20):
        LHS[:, :] = 0.0
        RHS[:] = 0.0
        for k in range(n_poses):
            x_ik = exponential_coordinates_from_transform(
                np.dot(mean, invert_transform(means[k])))
            J_inv = left_jacobian_SE3_inv(x_ik)
            J_invT_S = np.dot(J_inv.T, covs_inv[k])
            LHS += np.dot(J_invT_S, J_inv)
            RHS += np.dot(J_invT_S, x_ik)
        x_i = np.linalg.solve(-LHS, RHS)
        mean = np.dot(transform_from_exponential_coordinates(x_i), mean)

    cov = np.linalg.inv(LHS)

    V = 0.0
    for k in range(n_poses):
        x_ik = exponential_coordinates_from_transform(
            np.dot(mean, invert_transform(means[k])))
        V += 0.5 * np.dot(x_ik, np.dot(covs_inv[k], x_ik))
    return mean, cov, V


def to_ellipsoid(mean, cov):
    """Compute error ellipsoid.

    An error ellipsoid indicates the equiprobable surface. The resulting
    ellipsoid includes one standard deviation of the data along each main
    axis, which covers approximately 68.27% of the data. Multiplying the
    radii with factors > 1 will increase the coverage. The usual factors
    for Gaussian distributions apply:

    * 1 - 68.27%
    * 1.65 - 90%
    * 1.96 - 95%
    * 2 - 95.45%
    * 2.58 - 99%
    * 3 - 99.73%

    Parameters
    ----------
    mean : array-like, shape (3,)
        Mean of distribution.

    cov : array-like, shape (3, 3)
        Covariance of distribution.

    Returns
    -------
    ellipsoid2origin : array, shape (4, 4)
        Ellipsoid frame in world frame. Note that there are multiple solutions
        possible for the orientation because an ellipsoid is symmetric.
        A body-fixed rotation around a main axis by 180 degree results in the
        same ellipsoid.

    radii : array, shape (3,)
        Radii of ellipsoid, coinciding with standard deviations along the
        three axes of the ellipsoid. These are sorted in ascending order.
    """
    from scipy import linalg
    radii, R = linalg.eigh(cov)
    if np.linalg.det(R) < 0:  # undo reflection (exploit symmetry)
        R *= -1
    ellipsoid2origin = transform_from(R=R, p=mean)
    return ellipsoid2origin, np.sqrt(np.abs(radii))


def to_projected_ellipsoid(mean, cov, factor=1.96, n_steps=20):
    """Compute projected error ellipsoid.

    An error ellipsoid shows equiprobable points. This is a projection of a
    Gaussian distribution in exponential coordinate space to 3D.

    Parameters
    ----------
    mean : array-like, shape (4, 4)
        Mean of pose distribution.

    cov : array-like, shape (6, 6)
        Covariance of pose distribution in exponential coordinate space.

    factor : float, optional (default: 1.96)
        Multiple of the standard deviations that should be plotted.

    n_steps : int, optional (default: 20)
        Number of discrete steps plotted in each dimension.

    Returns
    -------
    x : array, shape (n_steps, n_steps)
        Coordinates on x-axis of grid on projected ellipsoid.

    y : array, shape (n_steps, n_steps)
        Coordinates on y-axis of grid on projected ellipsoid.

    z : array, shape (n_steps, n_steps)
        Coordinates on z-axis of grid on projected ellipsoid.
    """
    from scipy import linalg
    vals, vecs = linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]

    radii = factor * np.sqrt(vals[:3])

    # Grid on ellipsoid in exponential coordinate space
    x, y, z = unit_sphere_surface_grid(n_steps)
    x *= radii[0]
    y *= radii[1]
    z *= radii[2]
    P = np.column_stack((x.reshape(-1), y.reshape(-1), z.reshape(-1)))
    P = np.dot(P, vecs[:, :3].T)

    # Grid in Cartesian space
    T_diff = transforms_from_exponential_coordinates(P)
    # same as T_diff[m, :3, :3].T.dot(T_diff[m, :3, 3]) for each m
    P = np.einsum("ikj,ik->ij", T_diff[:, :3, :3], T_diff[:, :3, 3])
    P = (np.dot(P, mean[:3, :3].T) + mean[np.newaxis, :3, 3]).T

    shape = x.shape
    x = P[0].reshape(*shape)
    y = P[1].reshape(*shape)
    z = P[2].reshape(*shape)

    return x, y, z


def plot_projected_ellipsoid(
        ax, mean, cov, factor=1.96, wireframe=True, n_steps=20, color=None,
        alpha=1.0):  # pragma: no cover
    """Plots projected equiprobable ellipsoid in 3D.

    An error ellipsoid shows equiprobable points. This is a projection of a
    Gaussian distribution in exponential coordinate space to 3D.

    Parameters
    ----------
    ax : axis
        Matplotlib axis.

    mean : array-like, shape (4, 4)
        Mean pose.

    cov : array-like, shape (6, 6)
        Covariance in exponential coordinate space.

    factor : float, optional (default: 1.96)
        Multiple of the standard deviations that should be plotted.

    wireframe : bool, optional (default: True)
        Plot wireframe of ellipsoid and surface otherwise.

    n_steps : int, optional (default: 20)
        Number of discrete steps plotted in each dimension.

    color : str, optional (default: None)
        Color in which the equiprobably lines should be plotted.

    alpha : float, optional (default: 1.0)
        Alpha value for lines.

    Returns
    -------
    ax : axis
        Matplotlib axis.
    """
    x, y, z = to_projected_ellipsoid(mean, cov, factor, n_steps)

    if wireframe:
        ax.plot_wireframe(
            x, y, z, rstride=2, cstride=2, color=color, alpha=alpha)
    else:
        ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0)

    return ax
