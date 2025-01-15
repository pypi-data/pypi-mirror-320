# Copyright (C) 2021 The InstanceLib Authors. All Rights Reserved.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import functools
import itertools
from typing import Iterable, Optional, Sequence, Tuple, Union

from h5py._hl.dataset import Dataset  # type: ignore

import numpy as np
import numpy.typing as npt

from ..typehints import KT, DType


def to_bicolumn_proba(matrix: npt.NDArray[DType]) -> npt.NDArray[DType]:
    """Converts a matrix to bi column probability
    matrix if it is a single column matrix.
    Otherwhise, no changes occurs.

    Parameters
    ----------
    matrix : npt.NDArray[Any]
        An input matrix that is possibly a single column matrix

    Returns
    -------
    npt.NDArray[Any]
        The converted matrix
    """
    if len(matrix.shape) == 2:
        if matrix.shape[1] == 1:
            neg_prob = 1.0 - matrix
            prob_np: npt.NDArray[DType] = np.column_stack((neg_prob, matrix))  # type: ignore
            return prob_np
    if len(matrix.shape) == 1:
        neg_prob = 1.0 - matrix
        prob_np: npt.NDArray[DType] = np.column_stack((neg_prob, matrix))  # type: ignore
        return prob_np
    return matrix


def get_lists(slices: Iterable[Tuple[int, Optional[int]]]) -> Sequence[int]:
    def convert_back(slice: Tuple[int, Optional[int]]) -> Sequence[int]:
        start, end = slice
        if end is None:
            return [start]
        idxs = list(range(start, end))
        return idxs

    result = list(itertools.chain.from_iterable(map(convert_back, slices)))
    return result


def slicer(
    matrix: Union[Dataset, npt.NDArray[DType]],
    slices: Iterable[Tuple[int, Optional[int]]],
) -> npt.NDArray[DType]:
    def get_slices_1d():  # type: ignore
        for slice_min, slice_max in slices:
            if slice_max is not None:
                yield matrix[slice_min:slice_max]
            else:
                yield matrix[slice_min]

    def get_slices_2d():  # type: ignore
        for slice_min, slice_max in slices:
            if slice_max is not None:
                yield matrix[slice_min:slice_max, :]
            else:
                yield matrix[slice_min, :]

    dims = len(matrix.shape)  # type: ignore
    if dims == 1:
        return np.hstack(list(get_slices_1d()))  # type: ignore
    return np.vstack(list(get_slices_2d()))  # type: ignore


def memslicer(
    matrix: Union[Dataset, npt.NDArray[DType]],
    slices: Iterable[Tuple[int, Optional[int]]],
) -> npt.NDArray[DType]:
    idxs = get_lists(slices)
    min_idx, max_idx = min(idxs), max(idxs)
    new_idxs = tuple([idx - min_idx for idx in idxs])
    dims = len(matrix.shape)  # type: ignore

    def get_slice_1d() -> npt.NDArray[DType]:
        big_slice_mat: npt.NDArray[DType] = matrix[min_idx : (max_idx + 1)]  # type: ignore
        small_slice_mat = big_slice_mat[new_idxs]
        return small_slice_mat

    def get_slice_2d() -> npt.NDArray[DType]:
        big_slice_mat: npt.NDArray[DType] = matrix[min_idx : (max_idx + 1), :]  # type: ignore
        small_slice_mat = big_slice_mat[new_idxs, :]  # type: ignore
        return small_slice_mat

    if dims == 1:
        mat = get_slice_1d()
        return mat
    if dims == 2:
        mat = get_slice_2d()
        return mat
    raise NotImplementedError("No Slicing for 3d yet")


def matrix_to_vector_list(
    matrix: npt.NDArray[DType],
) -> Sequence[npt.NDArray[DType]]:
    def get_vector(index: int) -> npt.NDArray[DType]:
        return matrix[index, :]

    n_rows = matrix.shape[0]
    rows = range(n_rows)
    return list(map(get_vector, rows))


def matrix_tuple_to_vectors(
    keys: Sequence[KT], matrix: npt.NDArray[DType]
) -> Tuple[Sequence[KT], Sequence[npt.NDArray[DType]]]:
    return keys, matrix_to_vector_list(matrix)


def matrix_tuple_to_zipped(
    keys: Sequence[KT], matrix: npt.NDArray[DType]
) -> "Sequence[Tuple[KT, npt.NDArray[DType]]]":
    result = list(zip(keys, matrix_to_vector_list(matrix)))
    return result


def combiner(
    chunk_a: Tuple[Sequence[KT], npt.NDArray[DType]],
    chunk_b: Tuple[Sequence[KT], npt.NDArray[DType]],
) -> Tuple[Sequence[KT], npt.NDArray[DType]]:
    keys_a, mat_a = chunk_a
    keys_b, mat_b = chunk_b
    keys: Sequence[KT] = [*keys_a, *keys_b]
    mat: npt.NDArray[DType] = np.vstack((mat_a, mat_b))  # type: ignore
    return keys, mat


def chunk_combiner(
    chunks: Iterable[Tuple[Sequence[KT], npt.NDArray[DType]]]
) -> Tuple[Sequence[KT], npt.NDArray[DType]]:
    result = functools.reduce(lambda a, b: combiner(a, b), chunks)
    return result  # type: ignore
