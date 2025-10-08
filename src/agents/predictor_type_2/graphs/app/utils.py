from typing import List, Literal
from collections import Counter
import pydash

from src.utils.vector_store import DocumentType


def check_keyword(docs: List[DocumentType], keyword: Literal["bill", "invoice"]):
    count = 0
    for doc in docs:
        if keyword in doc["metadata"]["trx_type"].lower():
            count += 1
    return True if count > 1 else False


def check_common_category(docs: List[DocumentType]):
    most_common_cat_name = ""
    most_common_cat_id = ""
    
    trx_docs = pydash.filter_(docs, lambda d: d["metadata"]["type"] == "transaction")

    if (len(trx_docs) > 0):
        category_name_list = [doc["metadata"]["account_name"] for doc in trx_docs]
        category_id_list = [doc["metadata"]["account_id"] for doc in trx_docs]

        if len(category_name_list) > 0:
            counter_list = Counter(category_name_list).most_common()
            for items in counter_list:
                cat_name = items[0]
                cat_index = category_name_list.index(cat_name)
                cat_id = category_id_list[cat_index]

                if cat_id != "":
                    most_common_cat_name = cat_name
                    most_common_cat_id = cat_id
                    break

    return (most_common_cat_name, most_common_cat_id)
