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
from typing import (Any, Callable, Dict, FrozenSet, Iterable, Iterator, List,
                    Mapping, Optional, Sequence, Tuple, TypeVar, Union)

_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")
_K = TypeVar("_K")

def value_map(
    f: Callable[[_T], _U], mapping: Mapping[_K, _T]
) -> Mapping[_K, _U]:
    return {k: f(v) for k, v in mapping.items()}

def single_or_collection(elem: Union[str, Iterable[str]]) -> Sequence[str]:
    if isinstance(elem, str):
        return [elem] 
    list_variant = list(elem)
    return list_variant


def powerset(iterable: Iterable[_T]) -> FrozenSet[FrozenSet[_T]]:
    """Calculates the powerset of an interable.


    Parameters
    ----------
    iterable : Iterable[_T]
        An iterable of which we want to calculate the powerset

    Returns
    -------
    FrozenSet[FrozenSet[_T]]
        Returns a frozenset of frozensets containing all elements
        of the powerset

    Examples
    --------
    
    Usage
    >>> powerset([1,2,3])
    >>> # frozenset({() (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)})
    >>> # all elements are also frozensets
    """
    s = list(iterable)
    result = itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1))
    return frozenset(map(frozenset, result))  # type: ignore

def identity(x: _T) -> _T:
    return x

def not_in_supersets(
        contingency: Dict[FrozenSet[_T], FrozenSet[_U]]
        ) -> Dict[FrozenSet[_T], FrozenSet[_U]]:
    """This function filters out all values that also exist in supersets
    in the dictionary for the values that exist in
    all pairs in the mapping key sets to value sets

    TODO: Make a clear description for this function

    Parameters
    ----------
    contingency : Dict[FrozenSet[_T], FrozenSet[_U]]
        A dictionary that maps key set to sets of values

    Returns
    -------
    Dict[FrozenSet[_T], FrozenSet[_U]]
        A dictionary that maps sets to sets of of values.
        The values of that belong to a key set only contain
        values that do not exist in a superset of the keyset.
    """    
    ret_dict: Dict[FrozenSet[_T], FrozenSet[_U]] = {}
    sets = frozenset(contingency.keys())
    for key_set in sets:
        strict_supersets = frozenset(filter(
            lambda s: s.issuperset(key_set) and s != key_set,
            sets))
        in_supersets: FrozenSet[_U] = frozenset()
        if len(strict_supersets) > 0:
            in_supersets = union(*map(lambda k: contingency[k], strict_supersets))
        ret_dict[key_set] = contingency[key_set].difference(in_supersets)
    return ret_dict


def flatten_dicts(*dicts: Mapping[_T, _U]) -> Dict[_T, _U]:
    """Recursive function that combines a list of dictionaries
    into a single dictionary. When a key exists multiple times, 
    the last one is preserved.

    Parameters
    ----------
    dicts
        A sequence dicts that should be combined

    Returns
    -------
    Dict[_T, _U]
        A single dictionary combining all given dictionaries.
    """    
    try:
        head, *tail = dicts
        return {**head, **flatten_dicts(*tail)}
    except ValueError:
        return {}

def intersection(*sets: FrozenSet[_T]) -> FrozenSet[_T]:
    """Return the intersection of all sets in the parameters
    
    Parameters
    ----------
    sets
        A sequence of frozensets that should be combined

    Returns
    -------
    FrozenSet[_T]
        A frozenset that contains the intersection of all the sets
    """    
    try:
        head, *tail = sets
        return head.intersection(*tail)
    except ValueError:
        return frozenset()

def union(*sets: FrozenSet[_T]) -> FrozenSet[_T]:
    """Return the union of all sets in the parameters
    
    Parameters
    ----------
    sets
        A sequence of frozensets that should be combined

    Returns
    -------
    FrozenSet[_T]
        A frozenset that contains the union of all the sets
    """    
    try:
        head, *tail = sets
        return head.union(*tail)
    except ValueError:
        return frozenset()

def invert_mapping(source: Mapping[_T, _V]) -> Dict[_V, _T]:
    result = {
        value: key  for (key, value) in source.items()
    }
    return result

def find_subsets(s: FrozenSet[_T], n: int) -> FrozenSet[FrozenSet[_T]]:
    
    subsets_n = frozenset( # type: ignore
        map(frozenset, itertools.combinations(s, n))) # type: ignore
    return subsets_n # type: ignore

def all_subsets(fset: FrozenSet[_T], 
                n_min: int, n_max: int) -> FrozenSet[FrozenSet[_T]]:
    """Find all subsets of `fset` with size `n_min` to and including 
    `n_max`

    Parameters
    ----------
    fset : FrozenSet[_T]
        The input set
    n_min : int
        The mininum size of the subsets
    n_max : int
        The maximum size of the subsets

    Returns
    -------
    FrozenSet[FrozenSet[_T]]
        A set of subsets
    """    
    subsets = (find_subsets(fset, n) for n in range(n_min, n_max + 1))
    result = union(*subsets)
    return result

def expandgrid(**itrs: Iterable[_T]) -> Dict[str, List[_T]]:
    """Port of the expand.grid function from R

    Parameters
    ----------
    itrs: Keyword variables with an iterable as argument

    Returns
    -------
    Dict[str, List[_T]]
        A dictionary with as values all possible combinations in a gridlike 
        ordering
    """
    variables = list(itrs.keys())
    iterators = list(itrs.values())
    product = list(itertools.product(*iterators))
    return {variable: [x[i] for x in product] for i, variable in enumerate(variables)}

def mapsnd(func: Callable[[_U], _V]) -> Callable[[_T, _U], Tuple[_T, _V]]:
    """This function converts a function with signature `u -> v` to a function
    with signature `(t, u) -> (t, v)`. 
    
    That is, a function that is applied to the second
    element of a tuple and where the first element is preserved.

    Parameters
    ----------
    func 
        The original function

    Returns
    -------
    Callable[[_T, _U], Tuple[_T, _V]]
        The new function

    Examples
    --------
    Usage

    >>> def plustwo(number: int) -> int:
    ...     return number + 2
    >>> tuple_variable = (2, 3)
    >>> mapped_p2 = mapsnd(plustwo)
    >>> result = mapped_p2(tuple_variable)
    >>> print(result)
    >>> # (2, 5)
    """    
    @functools.wraps(func)
    def wrap(fst: _T, snd: _U) -> Tuple[_T, _V]:
        result = func(snd)
        return (fst, result)
    return wrap

def all_equal(iterable: Iterable[Any]) -> bool:
    """Checks if all the elements of an iterable are the same

    Parameters
    ----------
    iterable
        An iterable of generic type

    Returns
    -------
    bool
        True if all elements are the same
    """    
    g = itertools.groupby(iterable)
    return next(g, True) and not next(g, False) # type: ignore


    


def list_unzip(iterable: Iterable[Tuple[_T, _U]]) -> Tuple[Sequence[_T], Sequence[_U]]:
    """Unzips an iterable of tuples of two elements, and returns a tuple of two lists,
    where the first contains all the first elements of the tuples and the latter the second
    elements

    Parameters
    ----------
    iterable
        An iterable of tuples of indiscriminate type

    Returns
    -------
    Tuple[Sequence[_T], Sequence[_U]]
        A tuple of two sequences: 
        
        - The first contains all first elements (of type `_T`)
        - The second contains all second elements (of type `_U`)

    Examples
    --------
    Usage

    >>> tuple_list = [(1, "a"), (2, "b"), (3, "c")]
    >>> idx, abcs = list_unzip(tuple_list)
    >>> print(idx)
    >>> # [1, 2, 3]
    >>> print(abcs)
    >>> # ["a", "b", "c"]
    """    
    try:
        fst_iter, snd_iter = zip(*iterable)
        fst_sequence, snd_sequence = list(fst_iter), list(snd_iter)
    except ValueError:
        return [], [] # type: ignore
    return fst_sequence, snd_sequence # type: ignore

def list_unzip3(
        iterable: Iterable[Tuple[_T, _U, _V]]) -> Tuple[Sequence[_T], Sequence[_U], Sequence[_V]]:
    """Unzips an iterable of tuples of three elements, and returns a tuple of three lists,
    where the first contains all the first elements of the tuples and the latter the second
    elements, etc.

    Parameters
    ----------
    iterable
        An iterable of tuples of indiscriminate type

    Returns
    -------
    Tuple[Sequence[_T], Sequence[_U], Sequence[_V]]
        A tuple of three sequences: 
        
        - The first contains all first elements (of type `_T`)
        - The second contains all second elements (of type `_U`)
        - The third contains all third elements (of type `_V`)

    Examples
    --------
    Usage

    >>> tuple_list = [(1, "a", 20), (2, "b", 40), (3, "c", 60)]
    >>> idx, abcs, ints = list_unzip3(tuple_list)
    >>> print(idx)
    >>> # [1, 2, 3]
    >>> print(abcs)
    >>> # ["a", "b", "c"]
    >>> print(ints)
    >>> # [20, 40, 60]
    """    
    try:
        fst_sequence, snd_sequence, trd_sequence = zip(*iterable)  # type ignore
    except ValueError:
        return [], [], [] #type: ignore
    return list(fst_sequence), list(snd_sequence), list(trd_sequence) # type: ignore

def filter_snd_none_zipped(iter: Iterable[Tuple[_T, Optional[_U]]]) -> Tuple[Sequence[_T], Sequence[_U]]:
    """Filter a list of tuples where the second element is not None

    Parameters
    ----------
    iter : Iterable[Tuple[_T, Optional[_U]]]
        A list of tuples where the second element may be `None`

    Returns
    -------
    Tuple[Sequence[_T], Sequence[_U]]
        A tuple of two lists of equal length based on all tuples where the 
        second element was not `None`:

        - A list of elements with type `_T`
        - A list of elements with type `_U`

    See Also
    --------
    filter_snd_none
        This function works similarly, but here the 
        iterable is not in `zipped` form.
    """    
    filtered = filter(lambda x: x[1] is not None, iter)
    return list_unzip(filtered) # type: ignore

def filter_snd_none(fst_iter: Iterable[_T], 
                snd_iter: Iterable[Optional[_U]]
                ) -> Tuple[Sequence[_T], Sequence[_U]]:
    """Filter two iterables of equal length for pairs where the second element is not None
    
    Parameters
    ----------
    fst_iter
        The first iterable
    snd_iter
        The second iterable where elements may be `None`.

    Returns
    -------
    Tuple[Sequence[_T], Sequence[_U]]
         A tuple of two lists of equal length based on all pairs based on index where the 
        element in the second list was not `None`:

        - A list containing all eligble elements from `fst_iter`
        - A list containing all eligble elements from `snd_iter`

    Examples
    --------

    Usage:

    >>> a = [1,2,3,4,5,6,7,8,9,10]
    >>> b = ["a", None, "c", "d", "e", "f", "g", None,"i", "j"]
    >>> a_filtered, b_filtered = filter_snd_none(a,b)
    >>> print(a_filtered)
    >>> # [1, 3, 4, 5, 6, 7, 9, 10]
    >>> print(b_filtered)
    >>> # ["a", "c", "d", "e", "f", "g", "i", "j"]

    See Also
    --------
    filter_snd_none_zipped : 
        This function works similarly, but here the 
        iterable is in `zipped` form, i.e., a list of tuples. 
    """    
    zipped: Iterable[Tuple[_T, _U]] = filter(lambda x: x[1] is not None, zip(fst_iter, snd_iter)) # type: ignore
    return list_unzip(zipped)



def zip_chain(iterable: Iterable[Tuple[Sequence[_T], Sequence[_U]]]) -> Iterator[Tuple[_T, _U]]:
    combined = (zip(a,b) for (a,b) in iterable)
    chained = itertools.chain.from_iterable(combined)
    yield from chained

def unzip_chain(iterable: Iterable[Tuple[Sequence[_T], Sequence[_U]]]) -> Tuple[Sequence[_T], Sequence[_U]]:
    results = list_unzip(zip_chain(iterable))
    return results

def sort_on(index: int, seq: Sequence[Tuple[_T, _U]]) -> Sequence[Tuple[_T, _U]]:
    """A function that allows you to sort a sequence on the `n-th` element of a tuple
    it contains. This function orders in descending order (high to low).

    Parameters
    ----------
    index : int
        The index of the tuple element on which you desire to sort
    seq 
        The sequence of tuples

    Returns
    -------
    Sequence[Tuple[_T, _U]]
        A sorted sequence of tuples
    """    
    return sorted(seq, key=lambda k: k[index], reverse=True) # type: ignore

def multisort(seq: Sequence[Tuple[_T, Sequence[_U]]]) -> Sequence[Sequence[Tuple[_T,_U]]]:
    len_scores = len(seq[0][1])
    unpacked = [[(key, scores[i]) for (key, scores) in seq] for i in range(len_scores)]
    sorted_unpacked = [sort_on(1, sublist) for sublist in unpacked]
    return sorted_unpacked

def fst(tup: Tuple[_T, Any]) -> _T:
    first_element = tup[0]
    return first_element

def mapping_map(mapping: Mapping[_T, _V], iterable: Iterable[_T]) -> Iterable[_V]:
    return (mapping[val] for val in iterable)

def seq_or_map_to_map(seq_or_map: Union[Sequence[_T], Mapping[int, _T]]) -> Mapping[int, _T]:
    if isinstance(seq_or_map, Mapping):
        return seq_or_map
    assert(isinstance(seq_or_map, Sequence)) # seq_or_map is a sequence
    result =  {idx: val for (idx, val) in enumerate(seq_or_map)}
    return result
