import json
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Mapping,
    FrozenSet,
    Iterator,
    Set,
    Tuple,
    TypeVar,
    Optional,
)

import numpy.typing as npt
import pandas as pd

from ..environment.text import TextEnvironment
from ..instances import Instance
from ..utils.func import list_unzip3

IT = TypeVar("IT", bound="Instance[Any, Any, Any, Any]", covariant=True)


@dataclass
class Qrel:
    topic: str
    doc_id: str
    relevancy: int


def hidden(p: Path) -> bool:
    return p.stem.startswith(".") or p.stem.startswith("_")


def read_doctexts(
    doctext_file: Path,
) -> Optional[Mapping[str, Mapping[str, str]]]:
    def process_line(line: str) -> Optional[Tuple[str, Mapping[str, str]]]:
        try:
            obj: Mapping[str, str] = json.loads(line)
            key = obj["id"]
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        return key, obj

    try:
        with doctext_file.open() as f:
            dictionary = {
                tup[0]: tup[1]
                for line in f.readlines()
                if (tup := process_line(line)) is not None
            }
    except UnicodeDecodeError:
        return None

    return dictionary


def build_doc_map(
    topic_docs: Mapping[str, Mapping[str, Mapping[str, str]]]
) -> Mapping[str, Set[str]]:
    docmap: Mapping[str, Set[str]] = dict()
    for topic, docs_dict in topic_docs.items():
        for doc_key in docs_dict:
            docmap.setdefault(doc_key, set()).add(topic)
    return docmap


def read_docids(docid_file: Path) -> FrozenSet[str]:
    with docid_file.open() as f:
        docids = frozenset([line.strip() for line in f.readlines()])
    return docids


def read_qrel(qrel_file: Path) -> pd.DataFrame:
    def qrel_iterator() -> Iterator[Qrel]:
        with open(qrel_file, "r", encoding="utf8") as f:
            for line in f:
                if len(line.split()) != 4:
                    continue
                topic_id, _, doc_id, rel = line.split()
                yield Qrel(topic_id, doc_id, int(rel))

    qrels = list(qrel_iterator())
    df = pd.DataFrame(qrels)
    df = df.set_index("doc_id")
    return df


def read_topics(topic_dir: Path) -> pd.DataFrame:
    jsons = list()
    for file in topic_dir.iterdir():
        with file.open() as f:
            jsons.append(*[json.loads(line) for line in f.readlines()])
    df = pd.DataFrame(jsons)
    df = df.set_index("id")
    return df


def read_qrel_dataset(base_dir: Path):
    qrel_dir = base_dir / "qrels"
    doctexts_dir = base_dir / "doctexts"
    topics_dir = base_dir / "topics"
    docids_dir = base_dir / "docids"
    doc_ids = {f.name: read_docids(f) for f in docids_dir.iterdir()}
    texts = {f.name: read_doctexts(f) for f in doctexts_dir.iterdir()}
    qrels = {f.name: read_qrel(f) for f in qrel_dir.iterdir()}
    topics = read_topics(topics_dir)
    return doc_ids, texts, qrels, topics


class TrecDataset:
    def __init__(
        self,
        docids: Mapping[str, FrozenSet[str]],
        texts: Mapping[str, Mapping[str, Mapping[str, str]]],
        qrels: Mapping[str, pd.DataFrame],
        topics: pd.DataFrame,
        pos_label: str = "Relevant",
        neg_label: str = "Irrelevant",
    ) -> None:
        self.docids = docids
        self.texts = texts
        self.qrels = qrels
        self.topics = topics

        self.pos_label = pos_label
        self.neg_label = neg_label

        self.topic_keys = list(self.topics.index)

        self.docmap = build_doc_map(self.texts)

    def get_topicqrels(self, topic_key: str) -> pd.DataFrame:
        return self.qrels[topic_key]

    def get_labels(self, topic_key: str, document: str) -> FrozenSet[str]:
        qrel_df = self.qrels[topic_key]
        relevancy = qrel_df.xs(document).relevancy
        if relevancy == 1:
            return frozenset([self.pos_label])
        return frozenset([self.neg_label])

    def get_documents(self, topic_key: str) -> FrozenSet[str]:
        if topic_key in self.docids:
            return frozenset(self.docids[topic_key])
        if topic_key in self.qrels:
            return frozenset(self.qrels[topic_key].index)
        return frozenset()

    def get_document(self, topic_key: str, doc_id: str) -> str:
        topics = list(self.docmap[doc_id])
        if len(topics) == 1:
            doc = self.texts[topics[0]][doc_id]
        elif topic_key in topics:
            doc = self.texts[topic_key][doc_id]
        else:
            raise KeyError(f"{topic_key} not in {topics}")
        title = doc["title"]
        content = doc["content"]
        return f"{title} {content}"

    def get_env(
        self, topic_key: str
    ) -> TextEnvironment[str, npt.NDArray[Any], str]:
        def yielder():
            def get_all(doc_id: str):
                data = self.get_document(topic_key, doc_id)
                labels = self.get_labels(topic_key, doc_id)
                return doc_id, data, labels

            for doc_id in self.get_documents(topic_key):
                try:
                    data_tuple = get_all(doc_id)
                except KeyError:
                    pass
                else:
                    yield data_tuple

        indices, data, labels = list_unzip3(yielder())
        env = TextEnvironment[str, npt.NDArray[Any], str].from_data(
            [self.neg_label, self.pos_label], indices, data, labels, None
        )
        return env

    def get_envs(
        self,
    ) -> Mapping[str, TextEnvironment[str, npt.NDArray[Any], str]]:
        return {tk: self.get_env(tk) for tk in self.topic_keys}

    @classmethod
    def from_path(cls, base_dir: Path):
        qrel_dir = base_dir / "qrels"
        doctexts_dir = base_dir / "doctexts"
        topics_dir = base_dir / "topics"
        docids_dir = base_dir / "docids"
        doc_ids = {
            f.name: read_docids(f)
            for f in docids_dir.iterdir()
            if not hidden(f)
        }
        texts = {
            f.name: docs
            for f in doctexts_dir.iterdir()
            if not hidden(f) and (docs := read_doctexts(f)) is not None
        }
        qrels = {
            f.name: read_qrel(f) for f in qrel_dir.iterdir() if not hidden(f)
        }
        topics = read_topics(topics_dir)
        return cls(doc_ids, texts, qrels, topics)
