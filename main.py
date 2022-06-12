import matplotlib.pyplot as plt
import numpy as np

from tools import *


def filter1d_conv(data, σ):
    """
    Convolves the data with a gaussian kernel. When data has multiple dimensions, the kernel is applied along the first dimension. Unoptimised, complexity is O(N^2). O(1) version is possible.
    data: np.array, N×...-dimensional array to be blurred along the 1st dimension. Used to blur correlation matrices for regression.
    σ: float, the standard deviation of the Gaussian kernel.
    """
    # TODO: optimise performance of `filter1d_conv` by either reducing kernel size or using an O(1) filter
    N = data.shape[0]  # kernel overlaps with the entire vector
    kernel = np.exp(-np.arange(-N, N + 1) ** 2 / (2 * σ**2))
    kernel /= np.sum(kernel)

    def conv1d(data):
        return np.convolve(data, kernel, mode="full")[N:-N]

    return np.apply_along_axis(conv1d, 0, data)


def fit_curve(data, density=10, order=1, σ=1):
    """
    Uses regression to fit a curve to a set of noisy points.
    data: np.array with dimensions N×M, a list of M-dimensional points. M=2 for a 2D curve.
    density: int, how many time more points to construct the curve from
    order: int, the order of the fitted curve. 1 for linear, 2 for quadratic, etc.
    σ: float, the standard deviation of the Gaussian kernel relative to teh density of the original data points. Lower values mean a curve fitting closer to the data points but a greater likelihood of failing to invert a matrix.
    """
    order += 1  # account for constant term
    N, M = data.shape
    ND = N * density - density + 1
    X = np.zeros([ND, order])
    lin = np.linspace(0, 1, N)
    for i in range(order):
        X[::density, i] = lin**i
    Y = np.zeros([ND, M])
    Y[::density, :] = data
    X_query = np.zeros([ND, order])
    lin = np.linspace(0, 1, ND)
    for i in range(order):
        X_query[:, i] = lin**i
    XᵀX = X[:, :, None] * X[:, None, :]  # outer products
    XᵀY = X[:, :, None] * Y[:, None, :]
    XᵀX_blur = filter1d_conv(XᵀX, σ=density*σ)  # blur statistical moments
    XᵀY_blur = filter1d_conv(XᵀY, σ=density*σ)  # blur statistical moments
    try:
        XᵀX_inv = np.linalg.inv(XᵀX_blur)  # TODO: Normalise `XᵀX_blur` matrix before inverse for stabler results
    except np.linalg.LinAlgError:
        printr("WARNING: Singular matrix, using pseudo-inverse. Resulting curve may be inaccurate.")
        XᵀX_inv = np.linalg.pinv(XᵀX_blur)
    A = np.einsum("ijk,ikl->ijl", XᵀX_inv, XᵀY_blur)  # compute model
    Y_curve = np.einsum("ik,ikj->ij", X_query, A)  # query model
    return Y_curve


data = np.array([[0, 1, 1, 2, 2, 3], [0, 0, 1, 1, 0, 0.0]]).transpose()

prop_cycle = plt.rcParams["axes.prop_cycle"]
colors = prop_cycle.by_key()["color"]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(data[:, 0], data[:, 1], c=colors[0], label="data")
for i in range(1, 6):
    Y = fit_curve(data, density=100, order=i, σ=0.9)
    ax.plot(Y[:, 0], Y[:, 1], c=colors[i], label=f"order {i}")
ax.legend()
ax.set_aspect("equal")
plt.savefig('orders.svg', dpi=300)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(data[:, 0], data[:, 1], c=colors[0], label="data")
for i in range(4):
    Y = fit_curve(data, density=100, order=3, σ=0.5 + 0.2 * i)
    ax.plot(Y[:, 0], Y[:, 1], c=colors[i + 1], label=f"stddev {0.5 + 0.2 * i}")
ax.legend()
ax.set_aspect("equal")
plt.savefig('fit.svg', dpi=300)
plt.show()
