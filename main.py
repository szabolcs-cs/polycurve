import numpy as np

def moments(A, B, resolution, σ, axis=0): ##TODO: auto sigma, axis=0
  """
  Computes moments, stretches them by `resolution` by interleaving zeros, and blurs them with a Gaussian having σ stddev.
  """
  # TODO: optimise performance of `filter1d_conv` by either reducing kernel size or using an O(1) filter
  data = np.einsum("ij,ik->ijk", A, B) # outer products
  data = np.array([i for x in data for i in [x]+[0*data[0]]*(resolution-1)])[:-resolution+1,...] # stretch
  N = data.shape[0]  # kernel overlaps with the entire vector
  kernel = np.exp(-np.arange(-N, N + 1) ** 2 / (2 * (resolution*σ)**2))
  kernel /= np.sum(kernel)
  return np.apply_along_axis(lambda x:np.convolve(x, kernel, mode="full")[N:-N], axis, data)

def fit_curve(Y, resolution=10, degree=1, σ=0.1, X=None):
  """
  Uses regression to fit a curve to a set of noisy points.
  X: Source dimensions to map from.
     np.array with dimensions N×M, a list of M-dimensional points. Usually M=1.
  Y: Target dimensions to map to.
     np.array with dimensions N×K, a list of K-dimensional points. Usually K=1 or 2.
  resolution: int, how many times more points to construct the curve from
  degree: int, the polynomial degree of the fitted curve. 1 for linear, 2 for quadratic, etc.
  σ: float, the standard deviation of the Gaussian kernel relative to teh resolution of the original data points. Lower values mean a curve fitting closer to the data points but a greater likelihood of failing to invert a matrix.
  """
  if X is None:
    X = np.linspace(0, 1, Y.shape[0])[:, None]
  assert X.shape[0] == Y.shape[0], "X and Y must have the same number of points."
  X_q = np.linspace(np.min(X), np.max(X), resolution*Y.shape[0] - resolution + 1)[...,None]**[range(degree+1)]
  X = X[...,None]**[[range(degree+1)]] # powers of X
  X = np.concatenate(X, axis=0)
  XX = moments(X, X, resolution, σ, axis=0) # compute and process outer products
  XY = moments(X, Y, resolution, σ, axis=0)
  XXXY = np.linalg.solve(XX, XY)
  Y_curve = np.einsum("ik,ikj->ij", X_q, XXXY)
  return Y_curve

if __name__ == "__main__":
  import matplotlib.pyplot as plt

  data = np.array([[0.0, 1, 1, 2, 2, 3], [0, 0, 1, 1, 0, 0.0]]).transpose()
  source = np.array([0.0, 1, 2, 3, 4, 5])[:, None]

  prop_cycle = plt.rcParams["axes.prop_cycle"]
  colors = prop_cycle.by_key()["color"]

  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.scatter(data[:, 0], data[:, 1], c=colors[0], label="Y")
  for i in range(1, 6):
    Y = fit_curve(data, resolution=100, degree=i, σ=0.9, X=source)
    ax.plot(Y[:, 0], Y[:, 1], c=colors[i], label=f"degree={i}")
  ax.legend()
  ax.set_aspect("equal")
  ax.set_title("Fitting curves of different polynomial degrees to 2D points")
  plt.margins(x=0)
  plt.savefig('degrees.svg', dpi=300, bbox_inches='tight')

  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.scatter(data[:, 0], data[:, 1], c=colors[0], label="Y")
  for i in range(4):
    Y = fit_curve(data, resolution=100, degree=3, σ=0.5 + 0.2 * i, X=source)
    ax.plot(Y[:, 0], Y[:, 1], c=colors[i + 1], label=f"σ={0.5 + 0.2 * i}")
  ax.legend()
  ax.set_aspect("equal")
  ax.set_title("3ʳᵈ degree curves of different smoothness")
  plt.margins(x=0)
  plt.savefig('fit.svg', dpi=300, bbox_inches='tight')
  plt.show()
