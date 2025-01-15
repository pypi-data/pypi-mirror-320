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

from abc import ABC, abstractmethod

from typing import (
    Any,
    Callable,
    FrozenSet,
    Generic,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

from ..instances import Instance

from ..typehints import KT, LT

from ..utils.func import identity


class LabelProvider(Mapping[KT, FrozenSet[LT]], ABC, Generic[KT, LT]):
    def __getitem__(
        self, __k: Union[Instance[KT, Any, Any, Any], KT]
    ) -> FrozenSet[LT]:
        return self.get_labels(__k)

    @property
    @abstractmethod
    def labelset(self) -> FrozenSet[LT]:
        """Report all possible labels (example usage: for setting up a classifier)

        Returns
        -------
        Set[LT]
            Labels of type `LT`
        """
        raise NotImplementedError

    @abstractmethod
    def remove_labels(
        self, instance: Union[KT, Instance[KT, Any, Any, Any]], *labels: LT
    ) -> None:
        """Remove the labels from this instance

        Parameters
        ----------
        instance : Union[KT, Instance]
            The instance
        *labels: LT
            The labels that should be removed from the instance
        """
        raise NotImplementedError

    @abstractmethod
    def set_labels(
        self, instance: Union[KT, Instance[KT, Any, Any, Any]], *labels: LT
    ) -> None:
        """Annotate the instance with the labels listed in the parameters

        Parameters
        ----------
        instance : Union[KT, Instance]
            The instance
        *labels: LT
            The labels that should be associated with the instance
        """
        raise NotImplementedError

    @abstractmethod
    def get_labels(
        self, instance: Union[KT, Instance[KT, Any, Any, Any]]
    ) -> FrozenSet[LT]:
        """Return the labels that are associated with the instance

        Parameters
        ----------
        instance : Union[KT, Instance]
            The instance

        Returns
        -------
        Set[LT]
            The labels that are associated with the instance
        """
        raise NotImplementedError

    @abstractmethod
    def get_instances_by_label(self, label: LT) -> FrozenSet[KT]:
        """Retrieve which instances are annotated with `label`

        Parameters
        ----------
        label : LT
            A Label

        Returns
        -------
        Set[Instance]
            The identifiers of the instance
        """
        raise NotImplementedError

    @property
    def len_positive(self) -> int:
        docset: Set[KT] = set()
        for label in self.labelset:
            for instance in self.get_instances_by_label(label):
                docset.add(instance)
        return len(docset)

    def document_count(self, label: LT) -> int:
        return len(self.get_instances_by_label(label))

    def __repr__(self) -> str:
        stats = {label: self.document_count(label) for label in self.labelset}
        result = (
            "LabelProvider("
            f"labelset={self.labelset}, \n"
            f"   length={len(self)}, \n"
            f"   statistics={stats})"
        )
        return result

    def __str__(self) -> str:
        return self.__repr__()


def default_label_viewer(
    key: KT, labelprovider: LabelProvider[KT, Any]
) -> Mapping[str, Any]:
    return {"label": ", ".join(map(str, labelprovider[key]))}


def columnar_label_viewer(
    labelset: Optional[Iterable[LT]] = None,
    prefix: str = "",
    boolmapper: Callable[[bool], Any] = identity,
) -> Callable[[KT, LabelProvider[KT, LT]], Mapping[str, Any]]:
    def viewer(
        key: KT, labelprovider: LabelProvider[KT, LT]
    ) -> Mapping[str, Any]:
        chosen_labelset = (
            frozenset(labelset)
            if labelset is not None
            else labelprovider.labelset
        )
        values = {
            f"{prefix}{label}": boolmapper(label in labelprovider[key])
            for label in chosen_labelset
        }
        return values

    return viewer
