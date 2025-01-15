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

from __future__ import annotations

from os import PathLike

from typing import Sequence, Optional, Callable, List, Dict, Any
from tempfile import NamedTemporaryFile

import numpy as np
import numpy.typing as npt
from sklearn.exceptions import NotFittedError  # type: ignore

from gensim.models.doc2vec import Doc2Vec, TaggedLineDocument  # type: ignore
from gensim.utils import save_as_line_sentence  # type: ignore


from .base import BaseVectorizer
from ..utils import SaveableInnerModel


def get_line_docs(documents: Sequence[str]) -> TaggedLineDocument:
    file = NamedTemporaryFile(delete=False, mode="w+b")
    file.close()
    corpus = [[element] for element in documents]
    save_as_line_sentence(corpus, file.name)
    tld = TaggedLineDocument(file.name)
    return tld


def split_tokenizer(text: str) -> List[str]:
    return text.split(" ")


DocTokenizer = Callable[..., List[str]]


class Doc2VecVectorizer(BaseVectorizer[str], SaveableInnerModel):
    _name = "Doc2Vec"
    innermodel: Optional[Doc2Vec]
    tokenizer: DocTokenizer

    def __init__(
        self,
        d2v_params: Dict[str, Any],
        tokenizer: DocTokenizer = split_tokenizer,
        storage_location: "Optional[PathLike[str]]" = None,
        filename: "Optional[PathLike[str]]" = None,
    ) -> None:
        BaseVectorizer.__init__(self)  # type: ignore
        self.tokenizer = tokenizer  # type: ignore
        self.d2v_params = d2v_params
        self.innermodel = None
        SaveableInnerModel.__init__(
            self, self.innermodel, storage_location, filename
        )

    def fit(self, x_data: Sequence[str], **kwargs: Any) -> Doc2VecVectorizer:
        self.innermodel = Doc2Vec(
            documents=get_line_docs(x_data), **self.d2v_params
        )
        self.innermodel.delete_temporary_training_data(  # type: ignore
            keep_doctags_vectors=True, keep_inference=True
        )
        self._fitted = True
        return self

    @SaveableInnerModel.load_model_fallback
    def transform(self, x_data: Sequence[str], **kwargs: Any) -> npt.NDArray[Any]:  # type: ignore
        if self.fitted and self.innermodel is not None:
            return np.array(  # type: ignore
                [
                    self.innermodel.infer_vector(self.tokenizer(doc))  # type: ignore
                    for doc in x_data
                ]
            )
        raise NotFittedError

    def fit_transform(self, x_data: Sequence[str], **kwargs: Any) -> npt.NDArray[Any]:  # type: ignore
        self.fit(x_data)
        return self.transform(x_data)  # type: ignore

    def save(self) -> None:
        if self.innermodel is not None:
            self.innermodel.save(self.filepath)  # type: ignore
            self.saved = True

    def load(self) -> None:
        self.innermodel = Doc2Vec.load(self.filepath)  # type: ignore
