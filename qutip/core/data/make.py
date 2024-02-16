from typing import Tuple
from .dispatch import Dispatcher as _Dispatcher
from . import csr, dense, dia, COO, CSR, Dense, Dia
import numpy as np

__all__ = [
    "diag",
    "one_element_coo",
    "one_element_csr",
    "one_element_dense",
    "one_element_dia",
    "one_element",
]


def _diag_signature(diagonals, offsets=0, shape=None):
    """
    Construct a matrix from diagonals and their offsets.  Using this
    function in single-argument form produces a square matrix with the given
    values on the main diagonal.
    With lists of diagonals and offsets, the matrix will be the smallest
    possible square matrix if shape is not given, but in all cases the
    diagonals must fit exactly with no extra or missing elements. Duplicated
    diagonals will be summed together in the output.

    Parameters
    ----------
    diagonals : sequence of array_like of complex or array_like of complex
        The entries (including zeros) that should be placed on the diagonals in
        the output matrix.  Each entry must have enough entries in it to fill
        the relevant diagonal and no more.
    offsets : sequence of integer or integer, optional
        The indices of the diagonals.  `offsets[i]` is the location of the
        values `diagonals[i]`.  An offset of 0 is the main diagonal, positive
        values are above the main diagonal and negative ones are below the main
        diagonal.
    shape : tuple, optional
        The shape of the output as (``rows``, ``columns``).  The result does
        not need to be square, but the diagonals must be of the correct length
        to fit in exactly.
    """
    pass


diag = _Dispatcher(_diag_signature, name="diag", inputs=(), out=True)
diag.add_specialisations(
    [
        (CSR, csr.diags),
        (Dia, dia.diags),
        (Dense, dense.diags),
    ],
    _defer=True,
)

del _diag_signature


class OutOfBoundsError(ValueError):
    def __init__(
        self, shape: Tuple[int, int], position: Tuple[int, int]
    ) -> None:
        msg = f"Position of the elements out of bound: {position} in {shape}"
        super().__init__(msg)


def one_element_coo(shape, position, value=1.0):
    """
    Create a matrix with only one nonzero element.

    Parameters
    ----------
    shape : tuple
        The shape of the output as (``rows``, ``columns``).

    position : tuple
        The position of the non zero in the matrix as (``rows``, ``columns``).

    value : complex, optional
        The value of the non-null element.
    """
    if not (0 <= position[0] < shape[0] and 0 <= position[1] < shape[1]):
        raise OutOfBoundsError(shape, position)

    data = np.array([value], dtype=complex)
    row = np.array([position[0]])
    col = np.array([position[1]])
    return COO((data, (row, col)), copy=False, shape=shape)


def one_element_csr(shape, position, value=1.0):
    """
    Create a matrix with only one nonzero element.

    Parameters
    ----------
    shape : tuple
        The shape of the output as (``rows``, ``columns``).

    position : tuple
        The position of the non zero in the matrix as (``rows``, ``columns``).

    value : complex, optional
        The value of the non-null element.
    """
    if not (0 <= position[0] < shape[0] and 0 <= position[1] < shape[1]):
        raise OutOfBoundsError(shape, position)
    data = csr.empty(*shape, 1)
    sci = data.as_scipy(full=True)
    sci.data[0] = value
    sci.indices[0] = position[1]
    sci.indptr[: position[0] + 1] = 0
    sci.indptr[position[0] + 1:] = 1
    return data


def one_element_dense(shape, position, value=1.0):
    """
    Create a matrix with only one nonzero element.

    Parameters
    ----------
    shape : tuple
        The shape of the output as (``rows``, ``columns``).

    position : tuple
        The position of the non zero in the matrix as (``rows``, ``columns``).

    value : complex, optional
        The value of the non-null element.
    """
    if not (0 <= position[0] < shape[0] and 0 <= position[1] < shape[1]):
        raise OutOfBoundsError(shape, position)
    data = dense.zeros(*shape, 1)
    nda = data.as_ndarray()
    nda[position] = value
    return data


def one_element_dia(shape, position, value=1.0):
    """
    Create a matrix with only one nonzero element.

    Parameters
    ----------
    shape : tuple
        The shape of the output as (``rows``, ``columns``).

    position : tuple
        The position of the non zero in the matrix as (``rows``, ``columns``).

    value : complex, optional
        The value of the non-null element.
    """
    if not (0 <= position[0] < shape[0] and 0 <= position[1] < shape[1]):
        raise OutOfBoundsError(shape, position)
    data = np.zeros((1, shape[1]), dtype=complex)
    data[0, position[1]] = value
    offsets = np.array([position[1] - position[0]])
    return Dia((data, offsets), copy=False, shape=shape)


one_element = _Dispatcher(
    one_element_dense, name="one_element", inputs=(), out=True
)
one_element.add_specialisations(
    [
        (COO, one_element_coo),
        (CSR, one_element_csr),
        (Dense, one_element_dense),
        (Dia, one_element_dia),
    ],
    _defer=True,
)
