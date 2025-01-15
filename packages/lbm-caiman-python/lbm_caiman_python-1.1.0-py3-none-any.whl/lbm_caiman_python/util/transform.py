import warnings
import numpy as np
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm


def vectorize(movie, pixel_indices: np.ndarray = None, order="C"):
    """
    Reshape an array: [time, df, cols] -> [n_pixels, time]

    Parameters
    ----------
    movie: np.ndarray
        movie of shape [time, df, cols]

    pixel_indices: np.ndarray, default None
        pixel indices to include in the vectorized output. 1D array of int that represents indices of a fully
        vectorized movie

    order: str, default "C"
        "C" or "F" order

    Returns
    -------
    np.ndarray
        vectorized movie, shape [n_pixels, time]

    """

    Y = movie.transpose(1, 2, 0).reshape(np.prod(movie.shape[1:]), movie.shape[0], order=order)

    if pixel_indices is not None:
        return Y[pixel_indices]

    return Y


def unvectorize(Y, shape: tuple[int, int], pixel_indices: np.ndarray = None, order="C"):
    """
    Reshape an array: [n_pixels, time] -> [time, df, cols]
    or
    [n_pixels,] -> [df, cols]


    Parameters
    ----------
    Y: np.ndarray
        vectorized movie, shape [n_pixels, time]

    shape: tuple[int, int]
        shape of one frame, [n_rows, n_cols]

    pixel_indices: np.ndarray, default None
        1D array of indices that map pixel indices in Y to real pixel indices in a "full Y" with all pixels

    order: str, default "C"
        "C" or "F" order

    Returns
    -------
    np.ndarray
        movie of shape [time, df, cols] or a 2D image of shape [df, cols]

    """

    if pixel_indices is not None and Y.shape[0] < np.prod(shape):
        if Y.ndim == 1:
            Y_full_shape = (np.prod(shape),)
        else:
            Y_full_shape = (np.prod(shape), Y.shape[1])

        Y_full = np.zeros(Y_full_shape, dtype=Y.dtype)
        Y_full[:] = np.nan
        Y_full[pixel_indices] = Y[:]
        Y = Y_full

    if Y.ndim == 1:
        # return 2D image
        return Y.reshape(shape, order=order)

    # return movie
    return Y.reshape(*shape, Y.shape[1], order=order).transpose(-1, 0, 1)


class Vectorizer(TransformerMixin, BaseEstimator):
    """
    Vectorize movies

    Parameters
    ----------
    order: str, array order
        "C" or "F"
    """

    def __init__(self, pixel_indices: np.ndarray = None, order: str = "C"):
        self.pixel_indices = None
        self.order = order

    def fit(self, movie, y=None):
        """
        Does nothing, exists for API conformity
        """

        return self

    def transform(self, movie: np.ndarray):
        """
        Vectorize the movie. Does nothing if the movie is already vectorized.

        Parameters
        ----------
        movie : array-like, shape [time, df, cols]
            input movie

        Returns
        -------
        np.ndarray
            vectorized movie, shape [n_pixels, time]

        """

        if movie.ndim == 2:
            return movie

        return vectorize(movie, pixel_indices=self.pixel_indices, order=self.order)

    def _more_tags(self):
        # This is a quick example to show the tags API:\
        # https://scikit-learn.org/dev/developers/develop.html#estimator-tags
        # Here, our transformer does not do any operation in `fit` and only validate
        # the parameters. Thus, it is stateless.
        return {"stateless": True}


class UnVectorizer(TransformerMixin, BaseEstimator):
    """
    Unvectorize movies

    Parameters
    ----------
    shape: tuple, [n_rows, n_cols]
        shape of a 2D frame of the movie

    order: str, array order
        "C" or "F"

    """

    def __init__(self, shape: tuple, pixel_indices: np.ndarray = None, order: str = "C"):
        if len(shape) != 2:
            raise ValueError
        self.shape = shape

        self.pixel_indices = pixel_indices
        self.order = order

    def fit(self, movie, y=None):
        """
        Does nothing, exists for API conformity
        """

        return self

    def transform(self, Y: np.ndarray):
        """
        Unvectorize the movie. Does nothing if the movie is already unvectorized.

        Parameters
        ----------
        Y: array-like, shape [n_pixels, time]
            input movie

        Returns
        -------
        np.ndarray
            unvectorized movie, shape [time, df, cols]

        """

        if Y.ndim == 3:
            return Y

        return unvectorize(Y, shape=self.shape, pixel_indices=self.pixel_indices, order=self.order)

    def _more_tags(self):
        # This is a quick example to show the tags API:\
        # https://scikit-learn.org/dev/developers/develop.html#estimator-tags
        # Here, our transformer does not do any operation in `fit` and only validate
        # the parameters. Thus, it is stateless.
        return {"stateless": True}


def calculate_centers(A, dims):
    def calculate_center_component(i):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            ixs = np.where(A[:, i].toarray() > 0.07)[0]
            if ixs.size == 0:
                return np.array([np.nan, np.nan])  # Handle empty slice explicitly
            return np.array(np.unravel_index(ixs, dims)).mean(axis=1)[::-1]

    print("Computing centers in parallel...")
    centers = Parallel(n_jobs=-1)(
        delayed(calculate_center_component)(i) for i in tqdm(range(A.shape[1]), desc="Calculating neuron center coordinates")
    )

    return np.array(centers)
