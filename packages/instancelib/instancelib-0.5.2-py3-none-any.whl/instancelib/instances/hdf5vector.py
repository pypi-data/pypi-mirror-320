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

import itertools
import pickle
from os import PathLike
from typing import (Any, Callable, Dict, Generic, Iterator, Optional, Sequence,
                    Tuple, Union)
import h5py  # type: ignore
import numpy as np  # type: ignore
import numpy.typing as npt
from h5py._hl.dataset import Dataset  # type: ignore

from ..exceptions import NoVectorsException
from ..utils.chunks import divide_iterable_in_lists, get_range
from ..utils.func import filter_snd_none, list_unzip, identity
from ..utils.numpy import (matrix_to_vector_list, matrix_tuple_to_vectors,
                           matrix_tuple_to_zipped, slicer)
from .vectorstorage import VectorStorage, ensure_writeable


from ..typehints import KT, DType


def keys_wrapper(keys: Sequence[Any]) -> Sequence[Union[int, str]]:
    def key_wrapper(key: Any) -> Union[int, str]:
        if isinstance(key, (int, str)):
            return key
        return str(key)
    converted = [key_wrapper(key) for key in keys]
    return converted



class HDF5VectorStorage(VectorStorage[KT, npt.NDArray[DType], npt.NDArray[DType]], Generic[KT, DType]):
    """This class provides the handling of on disk vector storage in HDF5 format.
    In many cases, storing feature matrices or large sets of vectors
    in memory is not feasible.
    
    This class provides methods that `InstanceProvider` implementations
    can use to ensure that only the vectors needed by some operations are 
    kept in memory. This class enables processing all vector in chunks that
    do fit in memory, enabling ordering all unlabeled instances for very large
    datasets.

    Parameters
    ----------
        h5path : str
            The path to the hdf5 file
        mode : str, optional
            The file mode (see `h5py` documentation), by default "r"
    """    
    
    __writemodes = ["a", "r+", "w", "w-", "x"]
    def __init__(self, h5path: "PathLike[str]", mode: str = "r") -> None:
        self.__mode = mode
        self.h5path = h5path
        self.key_dict: Dict[KT, int] = dict()
        self.inv_key_dict: Dict[int, KT] = dict()
        self.reload()

    @property
    def writeable(self) -> bool:
        """Check if the storage is writeable

        Returns
        -------
        bool
            True when writeable
        """        
        return self.__mode in self.__writemodes

    def __len__(self) -> int:
        """Returns the size of the dataset
        Returns
        -------
        int
            The size of the dataset
        """        
        return len(self.key_dict)

    @property
    def datasets_exist(self) -> bool:
        """Check if the HDF5 file contains a dataset

        Returns
        -------
        bool
            True, if the file contains a dataset
        """        
        with h5py.File(self.h5path, self.__mode) as hfile:
            exist = "vectors" in hfile and "keys" in hfile
        return exist    

    def reload(self) -> None:
        """Reload the index from disk
        """        
        with h5py.File(self.h5path, self.__mode) as hfile:
            if "dicts" in hfile:
                dicts = hfile["dicts"]
                assert isinstance(dicts, Dataset)
                self.key_dict = pickle.loads(dicts[0]) # type: ignore
                self.inv_key_dict = pickle.loads(dicts[1]) # type: ignore
            
    def __enter__(self):
        return self

    @ensure_writeable
    def __store_dicts(self) -> None:
        """Store the index dictionaries to disk in the HDF5 file
        """        
        with h5py.File(self.h5path, self.__mode) as hfile:
            if "dicts" not in hfile:
                dt = h5py.special_dtype(vlen=np.dtype("uint8")) # type: ignore
                hfile.create_dataset("dicts", (2,), dtype=dt) # type: ignore
            dicts = hfile["dicts"]
            assert isinstance(dicts, Dataset)
            dicts[0] = np.frombuffer( # type: ignore
                pickle.dumps(self.key_dict), dtype="uint8") #type: ignore
            dicts[1] = np.frombuffer( # type: ignore
                pickle.dumps(self.inv_key_dict), dtype="uint8") # type: ignore
    
    @ensure_writeable
    def rebuild_index(self, type_restorer: Callable[[Any], KT] = identity) -> None:
        """Rebuild the index after manual manipulation of a HDF5 file.

        Raises
        ------
        NoVectorsException
            If there are no vectors, or if they are stored incorrectly
        """        
        if not self.datasets_exist:
            raise NoVectorsException("There are no vectors stored in this file, "
                                     "therefore, the index dictionaries cannot "
                                     "be rebuilt.")
        self.key_dict: Dict[KT, int] = dict()
        self.inv_key_dict: Dict[int, KT] = dict()
        with h5py.File(self.h5path, self.__mode) as hfile:
            keys = hfile["keys"]
            assert isinstance(keys, Dataset)
            for i, key in enumerate(keys): # type: ignore
                r_key = type_restorer(key)
                self.key_dict[r_key] = i # type: ignore
                self.inv_key_dict[i] = r_key # type: ignore
        self.__store_dicts()
        
    
            
    def __exit__(self, type, value, traceback): # type: ignore
        if self.__mode in self.__writemodes:
            self.__store_dicts()
    
    def close(self) -> None:
        """Close the file and store changes to the index to disk
        """        
        self.__exit__(None, None, None) # type: ignore

    @ensure_writeable
    def _create_matrix(self, first_slice: npt.NDArray[DType]) -> None:
        """Create a vectors colum in the HDF5 file and add the
        the vectors in `first_slice`

        Parameters
        ----------
        first_slice : npt.NDArray[DType]
            A matrix
        """        
        vector_dim = first_slice.shape[1]
        with h5py.File(self.h5path, self.__mode) as hfile:
            if "vectors" not in hfile:
                hfile.create_dataset( # type: ignore
                    "vectors", data=first_slice, 
                    maxshape=(None, vector_dim), dtype="f", chunks=True)

    @ensure_writeable
    def _create_keys(self, keys: Sequence[KT]) -> None:
        """Create a key column in the HDF5 file.

        Parameters
        ----------
        keys : Sequence[KT]
            The keys that should be written
        """        
        with h5py.File(self.h5path, self.__mode) as hfile:
            converted_keys = keys_wrapper(keys)
            if "keys" not in hfile:
                hfile.create_dataset("keys", # type: ignore
                    data = converted_keys, maxshape=(None,)) # type: ignore
            for i, key in enumerate(keys):
                self.key_dict[key] = i
                self.inv_key_dict[i] = key
  
    @ensure_writeable
    def _append_matrix(self, matrix: npt.NDArray[DType]) -> bool:
        """Append a matrix to storage (only for internal use)

        Parameters
        ----------
        matrix : npt.NDArray[DType]
            A matrix. The vector dimension should match with this object

        Returns
        -------
        bool
            [description]

        Raises
        ------
        NoVectorsException
            [description]
        """        
        if not self.datasets_exist:
            raise NoVectorsException("Cannot append without existing vectors")
        with h5py.File(self.h5path, self.__mode) as hfile:
            dataset = hfile["vectors"]
            assert isinstance(dataset, Dataset)
            old_shape = dataset.shape # type: ignore
            mat_shape = matrix.shape
            assert mat_shape[1] == old_shape[1]
            new_shape = (dataset.shape[0] + mat_shape[0], mat_shape[1]) # type: ignore
            dataset.resize(size=new_shape) # type: ignore
            dataset[-mat_shape[0]:,:] = matrix
        return True 

    @ensure_writeable
    def _append_keys(self, keys: Sequence[KT]) -> bool:
        """Append keys to the vector storage

        Parameters
        ----------
        keys : Sequence[KT]
            The keys that should be appended to storage

        Returns
        -------
        bool
            True, if the operation succeeded

        Raises
        ------
        NoVectorsException
            If there are no vectors in storage, non can be appended
        """        
        if not self.datasets_exist:
            raise NoVectorsException("Cannot append without existing vectors")
        assert all(map(lambda k: k not in self.key_dict, keys))
        new_keys = keys_wrapper(keys) # type: ignore
        with h5py.File(self.h5path, self.__mode) as hfile:
            key_set = hfile["keys"]
            assert isinstance(key_set, Dataset)
            old_shape = key_set.shape # type: ignore
            arr_shape = (len(new_keys),)
            new_shape = (old_shape[0] + arr_shape[0],) # type: ignore
            key_set.resize(size=new_shape) # type: ignore
            key_set[-arr_shape[0]:] = new_keys
            start_index: int = old_shape[0] # type: ignore
            for i, key in enumerate(keys):
                hdf5_idx = start_index + i
                self.key_dict[key] = hdf5_idx
                self.inv_key_dict[hdf5_idx] = key
        self.__store_dicts()
        return True
        
    def __getitem__(self, k: KT) -> npt.NDArray[DType]:
        if not self.datasets_exist:
            raise NoVectorsException("There are no vectors stored in this object")
        h5_idx = self.key_dict[k]
        with h5py.File(self.h5path, self.__mode) as hfile:
            dataset = hfile["vectors"]
            assert isinstance(dataset, Dataset)
            data = dataset[h5_idx,:] # type: ignore
        return data # type: ignore

    @ensure_writeable
    def __setitem__(self, k: KT, value: npt.NDArray[DType]) -> None:
        assert self.datasets_exist
        if k in self:
            h5_idx = self.key_dict[k]
            with h5py.File(self.h5path, self.__mode) as hfile:
                dataset = hfile["vectors"]
                assert isinstance(dataset, Dataset)
                dataset[h5_idx] = value # type: ignore
            return
        raise KeyError 

    def __delitem__(self, v: KT) -> None:
        raise NotImplementedError
    
    def __contains__(self, item: object) -> bool:
        return item in self.key_dict
        
    def __iter__(self) -> Iterator[KT]:
        yield from self.key_dict

    @ensure_writeable
    def add_bulk_matrix(self, keys: Sequence[KT], matrix: npt.NDArray[DType]) -> None:
        """Add matrices in bulk

        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifiers. The following should hold: `len(keys) == matrix.shape[0]`
        matrix : npt.NDArray[DType]
            A matrix. The rows should correspond with the identifiers in keys
        """        
        assert len(keys) == matrix.shape[0]
        if not self.datasets_exist:
            self._create_matrix(matrix)
            self._create_keys(keys)
            return
        if all(map(lambda k: k not in self.key_dict, keys)):
            if self._append_keys(keys):
                self._append_matrix(matrix)
            return

    @ensure_writeable
    def _update_vectors(self, keys: Sequence[KT], values: Sequence[npt.NDArray[DType]]) -> None:
        """Update vectors in bulk
        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifiers
        values : Sequence[npt.NDArray[DType]]
            A list of new vectors
        """        
        assert len(keys) == len(values)
        if values:
            with h5py.File(self.h5path, self.__mode) as hfile:
                dataset = hfile["vectors"]
                assert isinstance(dataset, Dataset)
                for key, value in zip(keys, values):
                    h5_idx = self.key_dict[key]
                    dataset[h5_idx] = value # type: ignore
            
    @ensure_writeable
    def add_bulk(self, input_keys: Sequence[KT], input_values: Sequence[Optional[npt.NDArray[DType]]]) -> None:
        """Add a bulk of keys and values (vectors) to the vector storage

        Parameters
        ----------
        input_keys : Sequence[KT]
            The keys of the Instances
        input_values : Sequence[Optional[npt.NDArray[DType]]]
            The vectors that correspond with the indices
        """        
        assert len(input_keys) == len(input_values) and len(input_keys) > 0

        # Filter all keys that do not have a vector (input_values may contain None)
        keys, values = filter_snd_none(input_keys, input_values) # type: ignore
        
        if not values:
            return
        
        # Check if the vector storage exists
        if not self.datasets_exist:
            matrix: npt.NDArray[DType] = np.vstack(values) # type: ignore
            self._create_keys(keys)
            self._create_matrix(matrix)
            return
        
        # Check if the keys do not already exist in storage
        if all(map(lambda k: k not in self.key_dict, keys)):
            # This is the ideal case, all vectors can directly
            # be appended as a matrix
            matrix = np.vstack(values) # type: ignore
            self.add_bulk_matrix(keys, matrix)
            return
        
        # Find out which (key, vector) pairs are already stored
        not_in_storage = filter(lambda kv: kv[0] not in self.key_dict, zip(keys, values))
        in_storage = filter(lambda kv: kv[0] in self.key_dict, zip(keys, values))
        
        # Update the already present key vector pairs
        old_keys, updated_vectors = list_unzip(in_storage)
        self._update_vectors(old_keys, updated_vectors)

        # Append the new key vector pairs
        new_keys, new_vectors = list_unzip(not_in_storage)
        if new_vectors:
            matrix: npt.NDArray[DType] = np.vstack(new_vectors) # type: ignore
            self.add_bulk_matrix(new_keys, matrix)

    

    def _get_matrix(self, h5_idxs: Sequence[int]) -> Tuple[Sequence[KT], npt.NDArray[DType]]:
        """Return a matrix that correspond with the internal `h5_idxs`.

        Parameters
        ----------
        h5_idxs : Sequence[int]
            A list of internal indices that correspond with the indices

        Returns
        -------
        Tuple[Sequence[KT], npt.NDArray[DType]]
            A tuple containing:

                - The public indices (from the :class:`~allib.instances.InstanceProvider`)
                - A matrix where the rows map to the external indices
        Raises
        ------
        NoVectorsException
            If there are no vectors stored in this object
        """        
        if not self.datasets_exist:
            raise NoVectorsException("There are no vectors stored in this object")
        with h5py.File(self.h5path, self.__mode) as dfile:
            dataset = dfile["vectors"]
            assert isinstance(dataset, Dataset)
            slices = get_range(h5_idxs)
            result_matrix: npt.NDArray[DType] = slicer(dataset, slices) # type: ignore
            included_keys = list(map(lambda idx: self.inv_key_dict[idx], h5_idxs))
        return included_keys, result_matrix # type: ignore

    def get_vectors(self, keys: Sequence[KT]) -> Tuple[Sequence[KT], Sequence[npt.NDArray[DType]]]:
        """Return the vectors that correspond with the `keys` 

        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifier keys

        Returns
        -------
        Tuple[Sequence[KT], Sequence[npt.NDArray[DType]]]
            A tuple containing two lists:

                - A list with identifier (order may differ from `keys` argument)
                - A list with vectors 
        """        
        ret_keys, ret_matrix = self.get_matrix(keys)
        ret_vectors = matrix_to_vector_list(ret_matrix)
        return ret_keys, ret_vectors

    def get_matrix(self, keys: Sequence[KT]) -> Tuple[Sequence[KT], npt.NDArray[DType]]:
        """Return a matrix containing the vectors that correspond with the `keys`

        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifier keys

        Returns
        -------
        Tuple[Sequence[KT], npt.NDArray[DType]]
            A tuple containing:

                - A list with identifier keys
                    (order may differ from `keys` argument)
                - A matrix containing the vectors 
                    (rows correspond with the returned list)

        Raises
        ------
        NoVectorsException
            If there are no vectors returned
        """        
        if not self.datasets_exist:
            raise NoVectorsException("There are no vectors stored in this object")
        in_storage = frozenset(self.key_dict).intersection(keys)
        h5py_idxs = map(lambda k: self.key_dict[k], in_storage)
        sorted_keys = sorted(h5py_idxs)
        return self._get_matrix(sorted_keys)

    def get_matrix_chunked(self, 
                           keys: Sequence[KT], 
                           chunk_size: int = 200) -> Iterator[Tuple[Sequence[KT], npt.NDArray[DType]]]:
        """Return matrices in chunks of `chunk_size` containing the vectors requested in `keys`

        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifier keys
        chunk_size : int, optional
            The size of the chunks, by default 200

        Yields
        -------
        Tuple[Sequence[KT], npt.NDArray[DType]]
            A tuple containing:

                - A list with identifier keys
                    (order may differ from `keys` argument)
                - A matrix containing the vectors 
                    (rows correspond with the returned list)

        Raises
        ------
        StopIteration
            When there are no more chunks to process
        """        
        if not self.datasets_exist:
            raise StopIteration
        in_storage = frozenset(self.key_dict).intersection(keys)
        h5py_idxs = map(lambda k: self.key_dict[k], in_storage)
        sorted_keys = sorted(h5py_idxs)
        chunks = divide_iterable_in_lists(sorted_keys, chunk_size)
        yield from map(self._get_matrix, chunks)

    def get_vectors_chunked(self, 
                            keys: Sequence[KT], 
                            chunk_size: int = 200
                            ) -> Iterator[Tuple[Sequence[KT], Sequence[npt.NDArray[DType]]]]:
        """Return vectors in chunks of `chunk_size` containing the vectors requested in `keys`

        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifier keys
        chunk_size : int, optional
            The size of the chunks, by default 200

        Yields
        -------
        Tuple[Sequence[KT], Sequence[npt.NDArray[DType]]]
            A tuple containing two lists:

                - A list with identifiers (order may differ from `keys` argument)
                - A list with vectors 
        """        
        results = itertools.starmap(matrix_tuple_to_vectors, self.get_matrix_chunked(keys, chunk_size))
        yield from results # type: ignore

    def get_vectors_zipped(self, keys: Sequence[KT], chunk_size: int = 200) -> Iterator[Sequence[Tuple[KT, npt.NDArray[DType]]]]:
        """Return vectors in chunks of `chunk_size` containing the vectors requested in `keys`

        Parameters
        ----------
        keys : Sequence[KT]
            A list of identifier keys
        chunk_size : int, optional
            The size of the chunks, by default 200

        Yields
        -------
        Sequence[Tuple[KT, npt.NDArray[DType]]]
            A list containing tuples of:

                - An identifier (order may differ from `keys` argument)
                - A vector 
        """
        results = itertools.starmap(matrix_tuple_to_zipped, self.get_matrix_chunked(keys, chunk_size))
        yield from results # type: ignore
           

    def vectors_chunker(self, chunk_size: int = 200) -> Iterator[Sequence[Tuple[KT, npt.NDArray[DType]]]]:
        """Return vectors in chunks of `chunk_size`. This generator will yield all vectors contained
        in this object.

        Parameters
        ----------
        chunk_size : int, optional
            The size of the chunks, by default 200


        Yields
        -------
        Sequence[Tuple[KT, npt.NDArray[DType]]]
            A list containing tuples of:

                - An identifier
                - A vector
        """        
        results = itertools.starmap(matrix_tuple_to_zipped, self.matrices_chunker(chunk_size))
        yield from results # type: ignore
           
    def matrices_chunker(self, chunk_size: int = 200):
        """Yield matrices in chunks of `chunk_size` containing all the vectors in this object

        Parameters
        ----------
        chunk_size : int, optional
            The size of the chunks, by default 200

        Yields
        -------
        Tuple[Sequence[KT], npt.NDArray[DType]]
            A tuple containing:

                - A list with identifier keys
                - A matrix containing the vectors 
                    (row indices correspond with the list indices)

        Raises
        ------
        StopIteration
            When there are no more chunks to process
        """        
        if not self.datasets_exist:
            raise StopIteration
        h5py_idxs = self.inv_key_dict.keys()
        sorted_keys = sorted(h5py_idxs)
        chunks = divide_iterable_in_lists(sorted_keys, chunk_size)
        yield from map(self._get_matrix, chunks)
