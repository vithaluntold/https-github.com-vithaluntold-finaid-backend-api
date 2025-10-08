import os
from typing import List, Literal, TypedDict
from uuid import uuid4
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


### TYPES
class DocumentMetadataType(TypedDict):
    type: Literal["payee", "transaction"]
    payee_id: str
    payee_name: str
    payee_type: Literal["vendor", "customer"]
    account_id: int
    account_name: str
    account_class: str
    trx_type: str
    trx_desc: str


class DocumentType(TypedDict):
    score: float
    metadata: DocumentMetadataType


class VectorStoreType(TypedDict):
    hit: bool
    documents: List[DocumentType]


### TYPES

EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_STORE_DIR = os.environ["CHROMA_DIR"]


def _get_vector_store(collection_name: str) -> Chroma:
    return Chroma(
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        collection_name=collection_name,
        persist_directory=VECTOR_STORE_DIR,
    )


def _query_clean(q: str) -> str:
    clean_q = "".join(e for e in q if e.isalnum())
    clean_q = clean_q.lower().replace(" ", "")
    return clean_q


def convert_data_to_docs(data_list) -> List[Document]:
    """
    data_list:
        - type (payee/transaction)
          payee_id
          payee_name
          payee_type (vendor/customer)
          account_id
          account_name
          account_class
          trx_type
    """
    docs: List[Document] = []
    for data_item in data_list:
        # either payee name or trx desc is the vector key, both cannot be absent
        query = None
        if data_item["type"] == "payee":
            query = data_item["payee_name"]
        else:
            query = (
                data_item["trx_desc"]
                if data_item["trx_desc"] != ""
                else data_item["payee_name"]
            )

        doc = Document(
            page_content=_query_clean(query),
            metadata={
                "type": data_item["type"],
                "payee_id": data_item["payee_id"],
                "payee_name": data_item["payee_name"],
                "payee_type": data_item["payee_type"],
                "account_id": data_item["account_id"],
                "account_name": data_item["account_name"],
                "account_class": data_item["account_class"],
                "trx_type": data_item["trx_type"],
                "trx_desc": data_item["trx_desc"],
            },
        )
        docs.append(doc)
    return docs


def index_docs(documents: List[Document], collection_name: str) -> List[str]:
    vector_store = _get_vector_store(collection_name)

    uuids = [str(uuid4()) for _ in range(len(documents))]
    ids = vector_store.add_documents(documents=documents, ids=uuids)
    return ids


def fetch_all_data(collection_name: str) -> List[DocumentMetadataType]:
    vector_store = _get_vector_store(collection_name)

    res = vector_store.get()
    data = []
    for metadata in res["metadatas"]:
        data.append(metadata)
    return data


def search_store(
    query: str, collection_name: str, k: int = 1, threshold: float = 0.8
) -> VectorStoreType:
    vector_store = _get_vector_store(collection_name)

    res = vector_store.similarity_search_with_relevance_scores(
        query=_query_clean(query), k=k, score_threshold=threshold
    )
    if len(res) > 0:
        documents = []
        for r in res:
            doc, score = r
            documents.append(
                {
                    "score": score,
                    "metadata": {
                        "type": doc.metadata["type"],
                        "payee_id": doc.metadata["payee_id"],
                        "payee_name": doc.metadata["payee_name"],
                        "payee_type": doc.metadata["payee_type"],
                        "account_id": doc.metadata["account_id"],
                        "account_name": doc.metadata["account_name"],
                        "account_class": doc.metadata["account_class"],
                        "trx_type": doc.metadata["trx_type"],
                        "trx_desc": doc.metadata["trx_desc"],
                    },
                }
            )

        # TODO Filter out highest score alone?
        max_score = max(doc['score'] for doc in documents)
        documents_max = [doc for doc in documents if doc['score'] == max_score]

        return {"hit": True, "documents": documents_max}
    else:
        return {"hit": False, "documents": []}


def delete_store(collection_name: str):
    vector_store = _get_vector_store(collection_name)
    vector_store.delete_collection()
    return {"status": "success"}
