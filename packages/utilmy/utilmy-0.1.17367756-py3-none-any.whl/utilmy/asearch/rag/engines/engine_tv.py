# -*- coding: utf-8 -*-
"""
    #### Install
        pip install -r pip/py39_full.txt
        pip install utilmy tantivy fastembed ranx fastembed==0.2.6 loguru --no-deps


    #### ENV variables
       cd asearch
        export PYTHONPATH="$(pwd):$PYTHONPATH"
        export torch_device='cpu'

    #### Test
            python rag/engine_tv.py test_tantivy


    #### Dataset
        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail
        https://zenn.dev/kun432/scraps/1356729a3608d6
        https://huggingface.co/datasets/big_patent
        https://huggingface.co/datasets/ag_news


    #### Docs:
           https://tantivy-py.readthedocs.io/en/latest/reference/
                We'll use a test index for the examples that follow.

            import os
            from tantivy import SchemaBuilder, Index, Document
            schema = (
                SchemaBuilder()
                    .add_integer_field("doc_id", indexed=True, stored=True)
                    .add_text_field("title", stored=True)
                    .add_text_field("body")
                    .build()
            )
            index = Index(schema=schema, path=None)
            writer = index.writer(heap_size=15_000_000, num_threads=1)
            doc = Document()
            doc.add_integer("doc_id", 1)
            doc.add_text("title", "The Old Man and the Sea")
            doc.add_text(
                "body",
                (
                    "He was an old man who fished alone in a skiff in"
                    "the Gulf Stream and he had gone eighty-four days "
                    "now without taking a fish."
                ),
            )
            writer.add_document(doc)

            doc = Document()
            doc.add_integer("doc_id", 2)
            doc.add_text("title", "The Old Man and the Sea II")
            doc.add_text("body", "He was an old man who sailed alone.")

            writer.add_document(doc)
            writer.commit()
            index.reload()
            Valid Query Formats

            tantivy-py supports the query language used in tantivy. Below a few basic query formats are shown:

            AND and OR conjunctions.
            searcher = index.searcher()
            query = index.parse_query('(Old AND Man) OR Stream', ["title", "body"])
            (best_score, best_doc_address) = searcher.search(query, 3).hits[0]
            best_doc = searcher.doc(best_doc_address)
            +(includes) and -(excludes) operators.
            query = index.parse_query('+Old +Man chef -fished', ["title", "body"])
            (best_score, best_doc_address) = searcher.search(query, 3).hits[0]
            best_doc = searcher.doc(best_doc_address)
            Note: in a query like above, a word with no +/- acts like an OR.

            phrase search.
            query = index.parse_query('"eighty-four days"', ["title", "body"])
            (best_score, best_doc_address) = searcher.search(query, 3).hits[0]
            best_doc = searcher.doc(best_doc_address)
            integer search
            query = index.parse_query('1', ["doc_id"])
            (best_score, best_doc_address) = searcher.search(query, 3).hits[0]
            best_doc = searcher.doc(best_doc_address)
            Note: for integer search, the integer field should be indexed.

            For more possible query formats and possible query options, see Tantivy Query Parser Docs.

"""
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, pandas as pd, numpy as np, torch, functools
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class

import tantivy
#from fastembed import TextEmbedding
#from sentence_transformers import SentenceTransformer
#from transformers import AutoTokenizer, AutoModelForMaskedLM
#from ranx import Qrels, Run, fuse


from utilmy import pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob
from utilmy import log, log2, log3, log_error, log_warning


########## Local import
from rag.dataprep import (pd_fake_data, dataset_hf_to_parquet)
#from rag.engine_qd import EmbeddingModel


######################################################################################
def test_all():
    ### python engine2.py test_all
    test_tantivy()
    # test_fusion_search()


def test_tantivy(nrows=50):
    """test function for tantivy indexing"""
    dirtmp = "ztmp/df_test.parquet"
    dirindex = "ztmp/tantivy_index"
    if not os.path.exists(dirtmp):
        test_df = pd_fake_data(nrows=nrows, dirout=dirtmp, overwrite=False)
        pd_to_file(test_df, dirtmp)
    else:
        test_df = pd_read_file(dirtmp)

    tantivy_index_documents(
        dirin=dirtmp, datapath=dirindex, kbatch=10, colsused=["title", "text"]
    )
    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]

    query = query.replace("\n", " ")
    results = search_tantivy(query=query, datapath=dirindex)
    log(f"len(results):{len(results)}")
    assert len(results) > 0


def test_query():
    """
       Exact word match:
       Fuzzy Search:
                from tantivy.query import FuzzyTermQuery

                # Create fuzzy query
                # Parameters:
                # - field: field to search in
                # - term: term to match
                # - distance: max edit distance (default=2)
                # - prefix_length: length of prefix that must match exactly (default=0)
                # - transposition_cost_one: whether transpositions cost 1 or 2 edits (default=True)
                query = FuzzyTermQuery("text", "fussy", distance=2)

                # Search
                searcher = index.searcher()
                results = searcher.search(query)

                # Get results
                for hit in results:
                    print(f"Score: {hit.score}, Doc: {hit.doc}")

    
    """
    pass




###################################################################################
##  Tantivy Engine ################################################################
def tantivy_index_get(datapath: str = "./ztmp/tantivy_index", schema_name: str = None):
    if schema_name is None:
        schema = tantivy_schema_get_default()
    else:
        ### Load  function to create  schema only by name string.
        from utilmy import load_function_uri

        schema_builder_fun = load_function_uri(schema_name)
        schema = schema_builder_fun()

    # create datastore
    os_makedirs(datapath)

    index_disk = tantivy.Index(schema, path=str(datapath))
    return index_disk

"""
'date', 'url', 'title',  'text_html',
        'chunk_id', 'chunk_id_int',  'text_chunk',
        'L_cat', 'content_type',
        'L0_catnews',      ### news type
        'com_extract',     ##3 company name
        'info', 'emb', 'question_list',

# Text Field with different options
text_field = schema_builder.add_text_field("text", stored=True)
text_indexed = schema_builder.add_text_field("text_indexed", stored=True, indexing=True)
text_tokenized = schema_builder.add_text_field("text_tokenized", stored=True, tokenizer="en_stem")

indexed=True, stored=True
"""

def tantivy_schema_get_default():
    schema_builder = tantivy.SchemaBuilder()

    schema_builder.add_text_field("chunk_id", stored=True, index_option="basic")
    schema_builder.add_text_field("chunk_id_int", stored=True, index_option="basic")

    
    schema_builder.add_text_field("date", stored=True, index_option="basic")
    schema_builder.add_text_field("url", stored=True, index_option="basic")


    schema_builder.add_text_field("text_chunk", stored=True, index_option="position")
    
    schema_builder.add_text_field("L_cat", stored=True, index_option="basic")
    schema_builder.add_text_field("content_type", stored=True, index_option="basic")
    schema_builder.add_text_field("L0_catnews", stored=True, index_option="basic")
    schema_builder.add_text_field("com_extract", stored=True, index_option="basic")
    schema_builder.add_text_field("tags", stored=True, index_option="basic")
    
    schema_builder.add_text_field("info", stored=True, index_option="basic")
    schema_builder.add_text_field("question_list", stored=True, index_option="basic")
    
    schema = schema_builder.build()
    return schema


def tantivy_index_documents(
        dirin: str,
        datapath: str = None,
        kbatch: int = 10,
        colsused=None,
        db_sep: str = " @ ",
        db_heap_size: int = 50_0000_000,
        db_max_threads: int = 1,
) -> None:
    """Indexes documents into a Tantivy index.
    Args                : 
    dirin (str)         : path containing  documents to be indexed.
    datapath (str)      : path to  Tantivy index.                         : None.
    kbatch (int)        : batch size for committing documents to  index.  : 10.
    colsused (List)     : list of columns to use for indexing.            : None.
    db_sep (str)        : separator to use for concatenating text columns.: " @ ".
    db_heap_size (int)  : heap size for  Tantivy index.                   : 50_0000_000.
    db_max_threads (int): maximum number of threads for  Tantivy index.   : 1.

    Returns:
        None
    """
    df = pd_read_file(path_glob=dirin)

    # create index schema if not already existing
    index_disk = tantivy_index_get(datapath)
    writer = index_disk.writer(heap_size=db_heap_size, num_threads=db_max_threads)

    textcols = (
        [col for col in df.columns if col not in ("text_id",)]
        if colsused is None
        else colsused
    )

    #### Insert inside  index
    for k, row in df.iterrows():
        # log(type(doc.categories))
        title = row.get("title", row["text"][:30])
        fulltext = db_sep.join(
            [str(row[col]) for col in textcols]
        )  # .title, row.text, " ".join(row.categories)])
        writer.add_document(
            tantivy.Document(
                title=title,
                text=row["text"],
                text_id=str(row["text_id"]),
                # categories=row.categories if "categories" in row else "",
                fulltext=fulltext,
            )
        )

        if k % kbatch == 0:
            log("Commit:", k)
            writer.commit()

    writer.commit()
    writer.wait_merging_threads()


def str_to_alphanum_only(txt):
    return "".join([c if c.isalnum() else " " for c in txt])


def search_tantivy(index_tv: str = "./ztmp/tantivy_index", 
                   query: str = "", topk: int = 10,
                   search_cols:list=None,

                   word_list_fuzzy:list=None, 
                   search_cols_fuzzy:list=None):
    """Search a tantivy index
          datapath: str: path to  tantivy index or TV index
          query:   str: query to search
          size: int: number of results to return
          return: list of tuples (score, document) where document is a dictionary of  document fields

            # Field specific search
            "field:term"              # Search in specific field
            "title:python"            # Example

            # Boolean operators
            "term1 AND term2"         # Both terms required
            "term1 OR term2"          # Either term
            "-term"                   # Exclude term
            "+term"                   # Required term

            # Phrase search
            '"exact phrase"'          # Exact phrase match
            '"phrase"~2'              # Phrase with slop (2 words distance)

            # Range queries
            "field:[start TO end]"    # Inclusive range
            "field:{start TO end}"    # Exclusive range

            *: Match all documents
            IN: Set membership (e.g., "field IN [a b c]")
            ^N: Boost factor (e.g., "term^2.0")
            ~N: Fuzzy search distance
            *: Prefix search (e.g., "pre*")


                # Create schema and index
                schema_builder = tantivy.SchemaBuilder()
                schema_builder.add_text_field("text", tokenizer_name="whitespace")
                schema = schema_builder.build()
                index = tantivy.Index(schema)

                Best Practices
                Use for technical terms or codes
                When preserving case is important
                When punctuation should be kept
                For simple space-separated token matching


            # Search using whitespace tokenizer
            query = index.parse_query("term1 term2", ["text"])
                                    
                    ### AND and OR
                    query = '(Old AND Man) OR Stream', ["title", "body"])

                    ### Exclude: Note: in a query like above, a word with no +/- acts like an OR.
                    query = '+Old +Man chef -fished', ["title", "body"])
                    
                    ### Exact Match
                    query= '"eighty-four days"'

                    #### Fuzzy
                    fuzzy_query = "John~1"   ### Edit edit distance of 1

                    query = index.parse_query("sea whale", ["title", "body"])
                    query = index.parse_query("title:men AND body:winter", ["title", "body"])
                    float_query = index.parse_query("3.5", ["rating"])
                    integer_query = index.parse_query("1", ["id"])

                    #### Works!
                        index.parse_query(r'"sea\""', ["title", "body"])

                    ### Define a fuzzy query
                    fuzzy_query = query_parser.parse_query("Joh*n~1")


                    After the tilde, you specify the number of allowed edits. For example, "Joh*n~1" allows for one edit distance.


          https://tantivy-py.readthedocs.io/en/latest/reference/

          def test_parse_query_fuzzy_fields(self, ram_index):
              query = ram_index.parse_query("winter", fuzzy_fields={"title": (True, 1, False)})
              assert (
                  repr(query)
                  Query(BooleanQuery { subqueries: [(Should, FuzzyTermQuery { term: Term(field=0, type=Str, "winter"), 
                     distance: 1, 
                     prefix: true
                     transposition_cost_one: false, 
                      }), (Should, TermQuery(Term(field=1, type=Str, "winter")))] })
              )

            AND and OR conjunctions.
            searcher = index.searcher()

        ### Perform the search
        with searcher.search_context() as context:
            results = searcher.search(fuzzy_query, 10, context=context)

         Always use with statement
Reload index before searching
Keep context operations together
Don't store context objects


    """
    index = tantivy_index_get(index_tv)
    # query_parser = reader.query_parser(["title", "text"], default_conjunction="AND")
    searcher = index.searcher()
    # print(f"Searching for: {query}")

    search_cols = ['title', "body"] if search_cols is None else search_cols
    query_parser  = "whitespace" ### regex *  Joh*n
    try:
        query1 = str_to_alphanum_only(query)
        query1 = index.parse_query(query1, search_cols,  query_parser=query_parser) 

        with searcher.search_context() as context:
            results = searcher.search(query1, topk, context=context).hits


        # log(results)

        ### Results to docs
        score_docs = [
            (score, searcher.doc(doc_address)) for score, doc_address in results
        ]
        return score_docs

    except Exception as err:
        print(traceback.format_exc())
        log(query, err)
        return []



def search_custom_tantivy(index, schema: str, words_exact: list= [],
   words_fuzzy: list = [],
   fuzzy_dist=2,
   top_k: int = 10
):
    searcher = index.searcher()
    combined_scores = {}
    id2doc = {}
    from tantivy import Index, QueryParser, Document, Query

 
    for word in words_exact:
        query = Query.fuzzy_term_query(index.schema, schema, word, distance=0,transposition_cost_one=True)
        results = searcher.search(query, 10).hits
        score_docs = [(score, searcher.doc(doc_address)) for score, doc_address in results]
    
    for doc in score_docs:
        doc_id = doc[1]['chunk_id'][0]
        combined_scores[doc_id] += doc[0]
        id2doc[doc_id] = doc[1]

    for word in words_fuzzy:
        query = Query.fuzzy_term_query(index.schema, schema, word, distance=2,transposition_cost_one=True)
        results = searcher.search(query, 10).hits
        score_docs = [(score, searcher.doc(doc_address)) for score, doc_address in results]
        for doc in score_docs:
           doc_id = doc[1]['chunk_id'][0]
           combined_scores[doc_id] += doc[0]
           id2doc[doc_id] = doc[1]



    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    top_docs = sorted_results[:top_k]



    top_docs_details = []
    for doc_id, score in top_docs:
        doc = id2doc[doc_id]
        top_docs_details.append((score, doc))



    return top_docs_details

###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




"""

    #### Benchmarks:
            sudo docker run -d -p 6333:6333     -v ~/.watchtower/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
            alias py2="python rag/engine_tv.py "

            py2 bench_v1_create_indexes --dirdata_root ztmp/bench/
            py2 bench_v1_run  --dirout ztmp/bench/   --topk 5


            ### Bench
            tantivy : v1  6ms
            Sparse :      23ms
            Dense:        30 ms
            
            ag_news index timings:
            records: 127600
            dense stransformers vectors: 9m28s
            dense fastembed vectors:
            sparse vectors: 9819/12760

###### Docs:
from io import BytesIO

import copy
import datetime
import json
import pickle
import pytest

import tantivy
from conftest import schema, schema_numeric_fields
from tantivy import Document, Index, SchemaBuilder, SnippetGenerator, Query, Occur, FieldType


class TestClass(object):
    def test_simple_search_in_dir(self, dir_index):
        _, index = dir_index
        query = index.parse_query("sea whale", ["title", "body"])

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1

    def test_simple_search_after_reuse(self, dir_index):
        index_dir, _ = dir_index
        index = Index(schema(), str(index_dir))
        query = index.parse_query("sea whale", ["title", "body"])

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1

    def test_simple_search_in_ram(self, ram_index):
        index = ram_index
        query = index.parse_query("sea whale", ["title", "body"])

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["The Old Man and the Sea"]

    def test_simple_search_in_spanish(self, spanish_index):
        index = spanish_index
        query = index.parse_query("vieja", ["title", "body"])

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        search_doc = index.searcher().doc(doc_address)
        assert search_doc["title"] == ["El viejo y el mar"]

    def test_and_query(self, ram_index):
        index = ram_index
        query = index.parse_query(
            "title:men AND body:summer", default_field_names=["title", "body"]
        )
        # look for an intersection of documents
        searcher = index.searcher()
        result = searcher.search(query, 10)

        # summer isn't present
        assert len(result.hits) == 0

        query = index.parse_query("title:men AND body:winter", ["title", "body"])
        result = searcher.search(query)

        assert len(result.hits) == 1

    def test_doc_freq(self, ram_index):
        index = ram_index
        searcher = index.searcher()
        doc_freq = searcher.doc_freq("body", "and")
        assert doc_freq == 3

    def test_and_aggregate(self, ram_index_numeric_fields):
        index = ram_index_numeric_fields
        query = Query.all_query()
        agg_query = {
            "top_hits_req": {
                "top_hits": {
                    "size": 2,
                    "sort": [{"rating": "desc"}],
                    "from": 0,
                    "docvalue_fields": ["rating", "id", "body"],
                }
            }
        }
        searcher = index.searcher()
        result = searcher.aggregate(query, agg_query)
        assert isinstance(result, dict)
        assert "top_hits_req" in result
        assert len(result["top_hits_req"]["hits"]) == 2
        for hit in result["top_hits_req"]["hits"]:
            assert len(hit["docvalue_fields"]) == 3

        assert result == json.loads("
{
"top_hits_req": {
    "hits": [
      {
        "sort": [ 13840124604862955520 ],
        "docvalue_fields": {
          "id": [ 2 ],
          "rating": [ 4.5 ],
          "body": [ "a", "few", "miles", "south", "of", "soledad", "the", "salinas", "river", "drops", "in", "close", "to", "the", "hillside",
            "bank", "and", "runs", "deep", "and", "green", "the", "water", "is", "warm", "too", "for", "it", "has", "slipped", "twinkling",
            "over", "the", "yellow", "sands", "in", "the", "sunlight", "before", "reaching", "the", "narrow", "pool",
            "on", "one", "side", "of", "the", "river", "the", "golden", "foothill", "slopes", "curve", "up",
            "to", "the", "strong", "and", "rocky", "gabilan", "mountains", "but", "on", "the", "valley", "side", "the",
            "water", "is", "lined", "with", "trees", "willows", "fresh", "and", "green", "with", "every", "spring", "carrying", "in", "their", "lower", "leaf",
            "junctures", "the", "debris", "of", "the", "winter", "s", "flooding", "and", "sycamores", "with", "mottled", "white", "recumbent", "limbs",
            "and", "branches", "that", "arch", "over", "the", "pool" ]
        }
      },
      {
        "sort": [ 13838435755002691584 ],
        "docvalue_fields": {
          "body": [ "he", "was", "an", "old", "man", "who", "fished", "alone", "in", "a", "skiff", "inthe", "gulf", "stream",
            "and", "he", "had", "gone", "eighty", "four", "days", "now", "without", "taking", "a", "fish" ],
          "rating": [ 3.5 ],
          "id": [ 1 ]
        }
      }
    ]
  }
}
")

    def test_and_query_numeric_fields(self, ram_index_numeric_fields):
        index = ram_index_numeric_fields
        searcher = index.searcher()

        # 1 result
        float_query = index.parse_query("3.5", ["rating"])
        result = searcher.search(float_query)
        assert len(result.hits) == 1
        assert searcher.doc(result.hits[0][1])["rating"][0] == 3.5

        integer_query = index.parse_query("1", ["id"])
        result = searcher.search(integer_query)
        assert len(result.hits) == 1

        # 0 result
        integer_query = index.parse_query("10", ["id"])
        result = searcher.search(integer_query)
        assert len(result.hits) == 0

    def test_and_query_parser_default_fields(self, ram_index):
        query = ram_index.parse_query("winter", default_field_names=["title"])
        assert repr(query) == "Query(TermQuery(Term(field=0, type=Str, "winter")))"

    def test_and_query_parser_default_fields_undefined(self, ram_index):
        query = ram_index.parse_query("winter")
        assert (
            repr(query)
            == "Query(BooleanQuery { subqueries: [(Should, TermQuery(Term(field=0, type=Str, "winter"))), (Should, TermQuery(Term(field=1, type=Str, "winter")))] })"
        )

    def test_parse_query_field_boosts(self, ram_index):
        query = ram_index.parse_query("winter", field_boosts={"title": 2.3})
        assert (
            repr(query)
            == "Query(BooleanQuery { subqueries: [(Should, Boost(query=TermQuery(Term(field=0, type=Str, "winter")), boost=2.3)), (Should, TermQuery(Term(field=1, type=Str, "winter")))] })"
        )

    def test_parse_query_fuzzy_fields(self, ram_index):
        query = ram_index.parse_query("winter", fuzzy_fields={"title": (True, 1, False)})
        assert (
            repr(query)
            == "Query(BooleanQuery { subqueries: [(Should, FuzzyTermQuery { term: Term(field=0, type=Str, "winter"), distance: 1, transposition_cost_one: false, prefix: true }), (Should, TermQuery(Term(field=1, type=Str, "winter")))] })"
        )

    def test_query_errors(self, ram_index):
        index = ram_index
        # no "bod" field
        with pytest.raises(ValueError):
            index.parse_query("bod:men", ["title", "body"])

    def test_query_lenient(self, ram_index_numeric_fields):
        from tantivy import query_parser_error

        index = ram_index_numeric_fields

        query, errors = index.parse_query_lenient("rating:3.5")
        assert len(errors) == 0
        assert repr(query) == "Query(TermQuery(Term(field=1, type=F64, 3.5)))"

        _, errors = index.parse_query_lenient("bod:men")
        assert len(errors) == 1
        assert isinstance(errors[0], query_parser_error.FieldDoesNotExistError)

        query, errors = index.parse_query_lenient(
            "body:'hello' AND id:<3.5 OR rating:'hi'"
        )
        assert len(errors) == 2
        assert isinstance(errors[0], query_parser_error.ExpectedIntError)
        assert isinstance(errors[1], query_parser_error.ExpectedFloatError)
        assert (
            repr(query)
            == "Query(BooleanQuery { subqueries: [(Should, BooleanQuery { subqueries: [(Must, TermQuery(Term(field=3, type=Str, "hello")))] })] })"
        )

    def test_order_by_search(self):
        schema = (
            SchemaBuilder()
            .add_unsigned_field("order", fast=True)
            .add_text_field("title", stored=True)
            .build()
        )

        index = Index(schema)
        writer = index.writer()

        doc = Document()
        doc.add_unsigned("order", 0)
        doc.add_text("title", "Test title")

        writer.add_document(doc)

        doc = Document()
        doc.add_unsigned("order", 2)
        doc.add_text("title", "Final test title")
        writer.add_document(doc)

        doc = Document()
        doc.add_unsigned("order", 1)
        doc.add_text("title", "Another test title")

        writer.add_document(doc)

        writer.commit()
        index.reload()

        query = index.parse_query("test")

        searcher = index.searcher()

        result = searcher.search(query, 10, offset=2, order_by_field="order")

        assert len(result.hits) == 1

        result = searcher.search(query, 10, order_by_field="order")

        assert len(result.hits) == 3

        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Final test title"]

        _, doc_address = result.hits[1]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Another test title"]

        _, doc_address = result.hits[2]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Test title"]

        result = searcher.search(
            query, 10, order_by_field="order", order=tantivy.Order.Asc
        )

        assert len(result.hits) == 3

        _, doc_address = result.hits[2]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Final test title"]

        _, doc_address = result.hits[1]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Another test title"]

        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Test title"]

    def test_order_by_search_without_fast_field(self):
        schema = (
            SchemaBuilder()
            .add_unsigned_field("order")
            .add_text_field("title", stored=True)
            .build()
        )

        index = Index(schema)
        writer = index.writer()

        doc = Document()
        doc.add_unsigned("order", 0)
        doc.add_text("title", "Test title")

        query = index.parse_query("test")

        searcher = index.searcher()
        result = searcher.search(query, 10, order_by_field="order")
        assert len(result.hits) == 0

    def test_order_by_search_date(self):
        schema = (
            SchemaBuilder()
            .add_date_field("order", fast=True)
            .add_text_field("title", stored=True)
            .build()
        )

        index = Index(schema)
        writer = index.writer()

        doc = Document()
        doc.add_date("order", datetime.datetime(2020, 1, 1))
        doc.add_text("title", "Test title")

        writer.add_document(doc)

        doc = Document()
        doc.add_date("order", datetime.datetime(2022, 1, 1))
        doc.add_text("title", "Final test title")
        writer.add_document(doc)

        doc = Document()
        doc.add_date("order", datetime.datetime(2021, 1, 1))
        doc.add_text("title", "Another test title")

        writer.add_document(doc)

        writer.commit()
        index.reload()

        query = index.parse_query("test")

        searcher = index.searcher()

        result = searcher.search(query, 10, order_by_field="order")

        assert len(result.hits) == 3

        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Final test title"]

        _, doc_address = result.hits[1]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Another test title"]

        _, doc_address = result.hits[2]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Test title"]

    def test_with_merges(self):
        # This test is taken from tantivy's test suite:
        # https://github.com/quickwit-oss/tantivy/blob/42acd334f49d5ff7e4fe846b5c12198f24409b50/src/indexer/index_writer.rs#L1130
        schema = SchemaBuilder().add_text_field("text", stored=True).build()

        index = Index(schema)
        index.config_reader(reload_policy="Manual")

        writer = index.writer()

        for _ in range(100):
            doc = Document()
            doc.add_text("text", "a")

            writer.add_document(doc)

        writer.commit()

        for _ in range(100):
            doc = Document()
            doc.add_text("text", "a")

            writer.add_document(doc)

        # This should create 8 segments and trigger a merge.
        writer.commit()
        writer.wait_merging_threads()

        # Accessing the writer again should result in an error.
        with pytest.raises(RuntimeError):
            writer.wait_merging_threads()

        index.reload()

        query = index.parse_query("a")
        searcher = index.searcher()
        result = searcher.search(query, limit=500, count=True)
        assert result.count == 200

        assert searcher.num_segments < 8

    def test_doc_from_dict_numeric_validation(self):
        schema = (
            SchemaBuilder()
            .add_unsigned_field("unsigned")
            .add_integer_field("signed")
            .add_float_field("float")
            .build()
        )

        good = Document.from_dict(
            {"unsigned": 1000, "signed": -5, "float": 0.4},
            schema,
        )

        good = Document.from_dict(
            {"unsigned": 1000, "signed": -5, "float": 0.4},
            schema,
        )

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {"unsigned": -50, "signed": -5, "float": 0.4},
                schema,
            )

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {"unsigned": 1000, "signed": 50.4, "float": 0.4},
                schema,
            )

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {
                    "unsigned": 1000,
                    "signed": -5,
                    "float": "bad_string",
                },
                schema,
            )

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {
                    "unsigned": [1000, -50],
                    "signed": -5,
                    "float": 0.4,
                },
                schema,
            )

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {
                    "unsigned": 1000,
                    "signed": [-5, 150, -3.14],
                    "float": 0.4,
                },
                schema,
            )

    def test_doc_from_dict_bytes_validation(self):
        schema = SchemaBuilder().add_bytes_field("bytes").build()

        good = Document.from_dict({"bytes": b"hello"}, schema)
        good = Document.from_dict({"bytes": [[1, 2, 3], [4, 5, 6]]}, schema)
        good = Document.from_dict({"bytes": [1, 2, 3]}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"bytes": [1, 2, 256]}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"bytes": "hello"}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"bytes": [1024, "there"]}, schema)

    def test_doc_from_dict_ip_addr_validation(self):
        schema = SchemaBuilder().add_ip_addr_field("ip").build()

        good = Document.from_dict({"ip": "127.0.0.1"}, schema)
        good = Document.from_dict({"ip": "::1"}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"ip": 12309812348}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"ip": "256.100.0.1"}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {"ip": "1234:5678:9ABC:DEF0:1234:5678:9ABC:DEF0:1234"}, schema
            )

        with pytest.raises(ValueError):
            bad = Document.from_dict(
                {"ip": "1234:5678:9ABC:DEF0:1234:5678:9ABC:GHIJ"}, schema
            )

    def test_doc_from_dict_json_validation(self):
        # Test implicit JSON
        good = Document.from_dict({"dict": {"hello": "world"}})

        schema = SchemaBuilder().add_json_field("json").build()

        good = Document.from_dict({"json": {}}, schema)
        good = Document.from_dict({"json": {"hello": "world"}}, schema)
        good = Document.from_dict(
            {"nested": {"hello": ["world", "!"]}, "numbers": [1, 2, 3]}, schema
        )

        list_of_jsons = [
            {"hello": "world"},
            {"nested": {"hello": ["world", "!"]}, "numbers": [1, 2, 3]},
        ]
        good = Document.from_dict({"json": list_of_jsons}, schema)

        good = Document.from_dict({"json": json.dumps(list_of_jsons[1])}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"json": 123}, schema)

        with pytest.raises(ValueError):
            bad = Document.from_dict({"json": "hello"}, schema)

    def test_search_result_eq(self, ram_index, spanish_index):
        eng_index = ram_index
        eng_query = eng_index.parse_query("sea whale", ["title", "body"])

        esp_index = spanish_index
        esp_query = esp_index.parse_query("vieja", ["title", "body"])

        eng_result1 = eng_index.searcher().search(eng_query, 10)
        eng_result2 = eng_index.searcher().search(eng_query, 10)
        esp_result = esp_index.searcher().search(esp_query, 10)

        assert eng_result1 == eng_result2
        assert eng_result1 != esp_result
        assert eng_result2 != esp_result

    def test_search_result_pickle(self, ram_index):
        index = ram_index
        query = index.parse_query("sea whale", ["title", "body"])

        orig = index.searcher().search(query, 10)
        pickled = pickle.loads(pickle.dumps(orig))

        assert orig == pickled

    def test_delete_all_documents(self, ram_index):
        index = ram_index
        writer = index.writer()
        writer.delete_all_documents()
        writer.commit()

        index.reload()
        query = index.parse_query("sea whale", ["title", "body"])
        result = index.searcher().search(query, 10)

        assert len(result.hits) == 0


class TestUpdateClass(object):
    def test_delete_update(self, ram_index):
        query = ram_index.parse_query("Frankenstein", ["title"])
        result = ram_index.searcher().search(query, 10)
        assert len(result.hits) == 1

        writer = ram_index.writer()

        with pytest.raises(ValueError):
            writer.delete_documents("fake_field", "frankenstein")

        with pytest.raises(ValueError):
            writer.delete_documents("title", b"frankenstein")

        writer.delete_documents("title", "frankenstein")
        writer.commit()
        ram_index.reload()

        result = ram_index.searcher().search(query)
        assert len(result.hits) == 0


class TestFromDiskClass(object):
    def test_opens_from_dir_invalid_schema(self, dir_index):
        invalid_schema = SchemaBuilder().add_text_field("🐱").build()
        index_dir, _ = dir_index
        with pytest.raises(ValueError):
            Index(invalid_schema, str(index_dir), reuse=True)

    def test_opens_from_dir(self, dir_index):
        index_dir, _ = dir_index

        index = Index(schema(), str(index_dir), reuse=True)
        assert index.searcher().num_docs == 3

    def test_create_readers(self):
        # not sure what is the point of this test.
        idx = Index(schema())
        idx.config_reader("Manual", 4)
        assert idx.searcher().num_docs == 0
        # by default this is manual mode
        writer = idx.writer(30000000, 1)
        writer.add_document(Document(title="mytitle", body="mybody"))
        writer.commit()
        assert idx.searcher().num_docs == 0
        # Manual is the default setting.
        # In this case, change are reflected only when
        # the index is manually reloaded.
        idx.reload()
        assert idx.searcher().num_docs == 1
        idx.config_reader("OnCommit", 4)
        writer.add_document(Document(title="mytitle2", body="mybody2"))
        writer.commit()
        import time

        for i in range(50):
            # The index should be automatically reloaded.
            # Wait for at most 5s for it to happen.
            time.sleep(0.1)
            if idx.searcher().num_docs == 2:
                return
        assert False


class TestSearcher(object):
    def test_searcher_repr(self, ram_index, ram_index_numeric_fields):
        assert repr(ram_index.searcher()) == "Searcher(num_docs=3, num_segments=1)"
        assert (
            repr(ram_index_numeric_fields.searcher())
            == "Searcher(num_docs=2, num_segments=1)"
        )


class TestDocument(object):
    def test_document(self):
        doc = tantivy.Document(name="Bill", reference=[1, 2])
        assert doc["reference"] == [1, 2]
        assert doc["name"] == ["Bill"]
        assert doc.get_first("name") == "Bill"
        assert doc.get_first("reference") == 1
        assert doc.to_dict() == {"name": ["Bill"], "reference": [1, 2]}

    def test_document_with_date(self):
        date = datetime.datetime(2019, 8, 12, 13, 0, 0)
        doc = tantivy.Document(name="Bill", date=date)
        assert doc["date"][0] == date

    def test_document_repr(self):
        doc = tantivy.Document(name="Bill", reference=[1, 2])
        assert repr(doc) == "Document(name=[Bill],reference=[1,2])"

    def test_document_repr_utf8(self):
        doc = tantivy.Document(name="野菜食べないとやばい", reference=[1, 2])
        assert repr(doc) == "Document(name=[野菜食べないとやばい],reference=[1,2])"

    def test_document_with_facet(self):
        doc = tantivy.Document()
        facet = tantivy.Facet.from_string("/europe/france")
        doc.add_facet("facet", facet)
        assert doc["facet"][0].to_path() == ["europe", "france"]
        doc = tantivy.Document()
        facet = tantivy.Facet.from_string("/asia\\/oceania/fiji")
        doc.add_facet("facet", facet)
        assert doc["facet"][0].to_path() == ["asia/oceania", "fiji"]
        assert doc["facet"][0].to_path_str() == "/asia\\/oceania/fiji"
        assert repr(doc["facet"][0]) == "Facet(/asia\\/oceania/fiji)"
        doc = tantivy.Document(facet=facet)
        assert doc["facet"][0].to_path() == ["asia/oceania", "fiji"]

    def test_document_eq(self):
        doc1 = tantivy.Document(name="Bill", reference=[1, 2])
        doc2 = tantivy.Document.from_dict({"name": "Bill", "reference": [1, 2]})
        doc3 = tantivy.Document(name="Bob", reference=[3, 4])

        assert doc1 == doc2
        assert doc1 != doc3
        assert doc2 != doc3

    def test_document_copy(self):
        doc1 = tantivy.Document(name="Bill", reference=[1, 2])
        doc2 = copy.copy(doc1)
        doc3 = copy.deepcopy(doc2)

        assert doc1 == doc2
        assert doc1 == doc3
        assert doc2 == doc3

    def test_document_pickle(self):
        orig = Document()
        orig.add_unsigned("unsigned", 1)
        orig.add_integer("integer", 5)
        orig.add_float("float", 1.0)
        orig.add_date("birth", datetime.datetime(2019, 8, 12, 13, 0, 5))
        orig.add_text("title", "hello world!")
        orig.add_json("json", '{"a": 1, "b": 2}')
        orig.add_bytes("bytes", b"abc")

        facet = tantivy.Facet.from_string("/europe/france")
        orig.add_facet("facet", facet)

        pickled = pickle.loads(pickle.dumps(orig))

        assert orig == pickled


class TestJsonField:
    def test_query_from_json_field(self):
        schema = (
            SchemaBuilder()
            .add_json_field(
                "attributes",
                stored=True,
                tokenizer_name="default",
                index_option="position",
            )
            .build()
        )

        index = Index(schema)

        writer = index.writer()

        doc = Document()
        doc.add_json(
            "attributes",
            "{
                "order":1.1,
                "target": "submit-button",
                "cart": {"product_id": 103},
                "description": "the best vacuum cleaner ever"
            }",
        )

        writer.add_document(doc)

        doc = Document()
        doc.add_json(
            "attributes",
            {
                "order": 1.2,
                "target": "submit-button",
                "cart": {"product_id": 133},
                "description": "das keyboard",
            },
        )

        writer.add_document(doc)

        writer.commit()
        index.reload()

        query = index.parse_query("target:submit-button", ["attributes"])
        result = index.searcher().search(query, 2)
        assert len(result.hits) == 2

        query = index.parse_query("target:submit", ["attributes"])
        result = index.searcher().search(query, 2)
        assert len(result.hits) == 2

        query = index.parse_query("order:1.1", ["attributes"])
        result = index.searcher().search(query, 2)
        assert len(result.hits) == 1

        # query = index.parse_query_for_attributes("cart.product_id:103")
        # result = index.searcher().search(query, 1)
        # assert len(result.hits) == 1

        # query = index.parse_query_for_attributes(
        #     "target:submit-button AND cart.product_id:133"
        # )
        # result = index.searcher().search(query, 2)
        # assert len(result.hits) == 1


@pytest.mark.parametrize("bytes_kwarg", [True, False])
@pytest.mark.parametrize(
    "bytes_payload",
    [
        b"abc",
        bytearray(b"abc"),
        memoryview(b"abc"),
        BytesIO(b"abc").read(),
        BytesIO(b"abc").getbuffer(),
    ],
)
def test_bytes(bytes_kwarg, bytes_payload):
    schema = SchemaBuilder().add_bytes_field("embedding").build()
    index = Index(schema)
    writer = index.writer()

    if bytes_kwarg:
        doc = Document(id=1, embedding=bytes_payload)
    else:
        doc = Document(id=1)
        doc.add_bytes("embedding", bytes_payload)

    writer.add_document(doc)
    writer.commit()
    index.reload()


def test_schema_eq():
    schema1 = schema()
    schema2 = schema()
    schema3 = schema_numeric_fields()

    assert schema1 == schema2
    assert schema1 != schema3
    assert schema2 != schema3


def test_facet_eq():
    facet1 = tantivy.Facet.from_string("/europe/france")
    facet2 = tantivy.Facet.from_string("/europe/france")
    facet3 = tantivy.Facet.from_string("/europe/germany")

    assert facet1 == facet2
    assert facet1 != facet3
    assert facet2 != facet3


def test_schema_pickle():
    orig = (
        SchemaBuilder()
        .add_integer_field("id", stored=True, indexed=True)
        .add_unsigned_field("unsigned")
        .add_float_field("rating", stored=True, indexed=True)
        .add_text_field("body", stored=True)
        .add_date_field("date")
        .add_json_field("json")
        .add_bytes_field("bytes")
        .build()
    )

    pickled = pickle.loads(pickle.dumps(orig))

    assert orig == pickled


def test_facet_pickle():
    orig = tantivy.Facet.from_string("/europe/france")
    pickled = pickle.loads(pickle.dumps(orig))

    assert orig == pickled


def test_doc_address_pickle():
    orig = tantivy.DocAddress(42, 123)
    pickled = pickle.loads(pickle.dumps(orig))

    assert orig == pickled


class TestSnippets(object):
    def test_document_snippet(self, dir_index):
        index_dir, _ = dir_index
        doc_schema = schema()
        index = Index(doc_schema, str(index_dir))
        query = index.parse_query("sea whale", ["title", "body"])
        searcher = index.searcher()
        result = searcher.search(query)
        assert len(result.hits) == 1

        snippet_generator = SnippetGenerator.create(
            searcher, query, doc_schema, "title"
        )

        for score, doc_address in result.hits:
            doc = searcher.doc(doc_address)
            snippet = snippet_generator.snippet_from_doc(doc)
            highlights = snippet.highlighted()
            assert len(highlights) == 1
            first = highlights[0]
            assert first.start == 20
            assert first.end == 23
            html_snippet = snippet.to_html()
            assert html_snippet == "The Old Man and the <b>Sea</b>"


class TestQuery(object):
    def test_term_query(self, ram_index):
        index = ram_index
        query = Query.term_query(index.schema, "title", "sea")

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["The Old Man and the Sea"]

    def test_term_set_query(self, ram_index):
        index = ram_index

        # Should match 1 document that contains both terms
        terms = ["old", "man"]
        query = Query.term_set_query(index.schema, "title", terms)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["The Old Man and the Sea"]

        # Should not match any document since the term does not exist in the index
        terms = ["a long term that does not exist in the index"]
        query = Query.term_set_query(index.schema, "title", terms)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0

        # Should not match any document when the terms list is empty
        terms = []
        query = Query.term_set_query(index.schema, "title", terms)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0

        # Should fail to create the query due to the invalid list object in the terms list
        with pytest.raises(ValueError, match = r"Can't create a term for Field `title` with value `\[\]`"):
            terms = ["old", [], "man"]
            query = Query.term_set_query(index.schema, "title", terms)

    def test_all_query(self, ram_index):
        index = ram_index
        query = Query.all_query()

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 3

    def test_phrase_query(self, ram_index):
        index = ram_index
        searcher = index.searcher()

        query = Query.phrase_query(index.schema, "title", ["old", "man"])
        # should match the title "The Old Man and the Sea"
        result = searcher.search(query, 10)
        assert len(result.hits) == 1

        query = Query.phrase_query(index.schema, "title", ["man", "old"])
        # sholdn't match any document
        result = searcher.search(query, 10)
        assert len(result.hits) == 0

        query = Query.phrase_query(index.schema, "title", [(1, "man"), (0, "old")])
        # should match "The Old Man and the Sea" with the given offsets
        result = searcher.search(query, 10)
        assert len(result.hits) == 1

        query = Query.phrase_query(index.schema, "title", ["man", "sea"])
        # sholdn't match any document with default slop 0.
        result = searcher.search(query, 10)
        assert len(result.hits) == 0

        query = Query.phrase_query(index.schema, "title", ["man", "sea"], slop=2)
        # should match the title "The Old Man and the Sea" with slop 2.
        result = searcher.search(query, 10)
        assert len(result.hits) == 1

        with pytest.raises(ValueError, match = "words must not be empty."):
            Query.phrase_query(index.schema, "title", [])

    def test_fuzzy_term_query(self, ram_index):
        index = ram_index
        query = Query.fuzzy_term_query(index.schema, "title", "ice")
        # the query "ice" should match "mice"
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Of Mice and Men"]

        query = Query.fuzzy_term_query(index.schema, "title", "mna")
        # the query "mna" should match "man" since the default transposition cost is 1.
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        titles = set()
        for _, doc_address in result.hits:
            titles.update(index.searcher().doc(doc_address)["title"])
        assert titles == {"The Old Man and the Sea"}

        query = Query.fuzzy_term_query(index.schema, "title", "mna", transposition_cost_one=False)
        # the query "mna" should not match any doc since the default distance is 1 and transposition cost is set to 2.
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0

        query = Query.fuzzy_term_query(index.schema, "title", "mna", distance=2, transposition_cost_one=False)
        # the query "mna" should match both "man" and "men" since distance is set to 2.
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2
        titles = set()
        for _, doc_address in result.hits:
            titles.update(index.searcher().doc(doc_address)["title"])
        assert titles == {"The Old Man and the Sea", "Of Mice and Men"}

        query = Query.fuzzy_term_query(index.schema, "title", "fraken")
        # the query "fraken" should not match any doc.
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0

        query = Query.fuzzy_term_query(index.schema, "title", "fraken", prefix=True)
        # the query "fraken" should match "franken", the prefix of "frankenstein", with edit distance 1.
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        titles = set()
        for _, doc_address in result.hits:
            titles.update(index.searcher().doc(doc_address)["title"])
        assert titles == {"Frankenstein", "The Modern Prometheus"}

    def test_boolean_query(self, ram_index):
        index = ram_index
        query1 = Query.fuzzy_term_query(index.schema, "title", "ice")
        query2 = Query.fuzzy_term_query(index.schema, "title", "mna")
        query = Query.boolean_query([
            (Occur.Must, query1), 
            (Occur.Must, query2)
        ])

        # no document should match both queries
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0

        query = Query.boolean_query([
            (Occur.Should, query1), 
            (Occur.Should, query2)
        ])

        # two documents should match, one for each query
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2

        titles = set()
        for _, doc_address in result.hits:
            titles.update(index.searcher().doc(doc_address)["title"])
        assert (
            "The Old Man and the Sea" in titles and  
            "Of Mice and Men" in titles
        )

        query = Query.boolean_query([
            (Occur.MustNot, query1), 
            (Occur.Must, query1)
        ])

        # must not should take precedence over must
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0

        query = Query.boolean_query((
            (Occur.Should, query1), 
            (Occur.Should, query2)
        ))

        # the Vec signature should fit the tuple signature
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2

        # test invalid queries
        with pytest.raises(ValueError, match = "expected tuple of length 2, but got tuple of length 3"):
            Query.boolean_query([
                (Occur.Must, Occur.Must, query1),
            ])

        # test swapping the order of the tuple
        with pytest.raises(TypeError, match = r"'Query' object cannot be converted to 'Occur'"):
            Query.boolean_query([
                (query1, Occur.Must),
            ])

    def test_disjunction_max_query(self, ram_index):
        index = ram_index

        # query1 should match the doc: "The Old Man and the Sea"
        query1 = Query.term_query(index.schema, "title", "sea")
        # query2 should matches the doc: "Of Mice and Men"
        query2 = Query.term_query(index.schema, "title", "mice")
        # the disjunction max query should match both docs.
        query = Query.disjunction_max_query([query1, query2])

        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2

        # the disjunction max query should also take a tie_breaker parameter
        query = Query.disjunction_max_query([query1, query2], tie_breaker=0.5)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2

        with pytest.raises(TypeError, match = r"'str' object cannot be converted to 'Query'"):
            query = Query.disjunction_max_query([query1, "not a query"], tie_breaker=0.5)


    def test_boost_query(self, ram_index):
        index = ram_index
        query1 = Query.term_query(index.schema, "title", "sea")
        boosted_query = Query.boost_query(query1, 2.0)

        # Normal boost query
        assert (
            repr(boosted_query)
            == "Query(Boost(query=TermQuery(Term(field=0, type=Str, "sea")), boost=2))"
        )

        query2 = Query.fuzzy_term_query(index.schema, "title", "ice")
        combined_query = Query.boolean_query([
            (Occur.Should, boosted_query), 
            (Occur.Should, query2)
        ])
        boosted_query = Query.boost_query(combined_query, 2.0)

        # Boosted boolean query
        assert (
            repr(boosted_query)
            == "Query(Boost(query=BooleanQuery { subqueries: [(Should, Boost(query=TermQuery(Term(field=0, type=Str, "sea")), boost=2)), (Should, FuzzyTermQuery { term: Term(field=0, type=Str, "ice"), distance: 1, transposition_cost_one: true, prefix: false })] }, boost=2))"
        )

        boosted_query = Query.boost_query(query1, 0.1)

        # Check for decimal boost values
        assert(
            repr(boosted_query)
            == "Query(Boost(query=TermQuery(Term(field=0, type=Str, "sea")), boost=0.1))"
        )

        boosted_query = Query.boost_query(query1, 0.0)

        # Check for zero boost values
        assert(
            repr(boosted_query)
            == "Query(Boost(query=TermQuery(Term(field=0, type=Str, "sea")), boost=0))"
        )
        result = index.searcher().search(boosted_query, 10)
        for _score, _ in result.hits:
            # the score should be 0.0
            assert _score == pytest.approx(0.0)  

        boosted_query = Query.boost_query(
            Query.boost_query(
                query1, 0.1
            ), 0.1
        )

        # Check for nested boost queries
        assert(
            repr(boosted_query)
            == "Query(Boost(query=Boost(query=TermQuery(Term(field=0, type=Str, "sea")), boost=0.1), boost=0.1))"
        )
        result = index.searcher().search(boosted_query, 10)
        for _score, _ in result.hits:
            # the score should be very small, due to 
            # the unknown score of BM25, we can only check for the relative difference
            assert _score == pytest.approx(0.01, rel = 1)  


        boosted_query = Query.boost_query(
            query1, -0.1
        )

        # Check for negative boost values
        assert(
            repr(boosted_query)
            == "Query(Boost(query=TermQuery(Term(field=0, type=Str, "sea")), boost=-0.1))"
        )

        result = index.searcher().search(boosted_query, 10)
        # Even with a negative boost, the query should still match the document
        assert len(result.hits) == 1
        titles = set()
        for _score, doc_address in result.hits:

            # the score should be negative
            assert _score < 0
            titles.update(index.searcher().doc(doc_address)["title"])
        assert titles == {"The Old Man and the Sea"}

        # wrong query type
        with pytest.raises(TypeError, match = r"'int' object cannot be converted to 'Query'"):
            Query.boost_query(1, 0.1)

        # wrong boost type
        with pytest.raises(TypeError, match = r"argument 'boost': must be real number, not str"):
            Query.boost_query(query1, "0.1")
        
        # no boost type error
        with pytest.raises(TypeError, match = r"Query.boost_query\(\) missing 1 required positional argument: 'boost'"):
            Query.boost_query(query1)


    def test_regex_query(self, ram_index):
        index = ram_index

        query = Query.regex_query(index.schema, "body", "fish")
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["The Old Man and the Sea"]

        query = Query.regex_query(index.schema, "title", "(?:man|men)")
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["The Old Man and the Sea"]
        _, doc_address = result.hits[1]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["Of Mice and Men"]

        # unknown field in the schema
        with pytest.raises(
            ValueError, match="Field `unknown_field` is not defined in the schema."
        ):
            Query.regex_query(index.schema, "unknown_field", "fish")

        # invalid regex pattern
        with pytest.raises(
            ValueError, match=r"An invalid argument was passed"
        ):
            Query.regex_query(index.schema, "body", "fish(")

    def test_more_like_this_query(self, ram_index):
        index = ram_index

        # first, search the target doc
        query = Query.term_query(index.schema, "title", "man")
        result = index.searcher().search(query, 1)
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["title"] == ["The Old Man and the Sea"]

        # construct the default MLT Query
        mlt_query = Query.more_like_this_query(doc_address)
        assert (
            repr(mlt_query)
            == "Query(MoreLikeThisQuery { mlt: MoreLikeThis { min_doc_frequency: Some(5), max_doc_frequency: None, min_term_frequency: Some(2), max_query_terms: Some(25), min_word_length: None, max_word_length: None, boost_factor: Some(1.0), stop_words: [] }, target: DocumentAddress(DocAddress { segment_ord: 0, doc_id: 0 }) })"
        )
        result = index.searcher().search(mlt_query, 10)
        assert len(result.hits) == 0

        # construct a fine-tuned MLT Query
        mlt_query = Query.more_like_this_query(
            doc_address,
            min_doc_frequency=2,
            max_doc_frequency=10,
            min_term_frequency=1,
            max_query_terms=10,
            min_word_length=2,
            max_word_length=20,
            boost_factor=2.0,
            stop_words=["fish"])
        assert (
            repr(mlt_query)
            == "Query(MoreLikeThisQuery { mlt: MoreLikeThis { min_doc_frequency: Some(2), max_doc_frequency: Some(10), min_term_frequency: Some(1), max_query_terms: Some(10), min_word_length: Some(2), max_word_length: Some(20), boost_factor: Some(2.0), stop_words: [\"fish\"] }, target: DocumentAddress(DocAddress { segment_ord: 0, doc_id: 0 }) })"
        )
        result = index.searcher().search(mlt_query, 10)
        assert len(result.hits) > 0
    def test_const_score_query(self, ram_index):
        index = ram_index

        query = Query.regex_query(index.schema, "body", "fish")
        const_score_query = Query.const_score_query(
            query, score = 1.0
        )
        result = index.searcher().search(const_score_query, 10)
        assert len(result.hits) == 1
        score, _ = result.hits[0]
        # the score should be 1.0
        assert score == pytest.approx(1.0)
        
        const_score_query = Query.const_score_query(
            Query.const_score_query(
                query, score = 1.0
            ), score = 0.5
        )
        
        result = index.searcher().search(const_score_query, 10)
        assert len(result.hits) == 1
        score, _ = result.hits[0]
        # nested const score queries should retain the 
        # score of the outer query
        assert score == pytest.approx(0.5)
        
        # wrong score type
        with pytest.raises(TypeError, match = r"argument 'score': must be real number, not str"):
            Query.const_score_query(query, "0.1")

    def test_range_query_numerics(self, ram_index_numeric_fields):
        index = ram_index_numeric_fields
        
        # test integer field including both bounds
        query = Query.range_query(index.schema, "id", FieldType.Integer, 1, 2)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2
        
        # test integer field excluding the lower bound
        query = Query.range_query(index.schema, "id", FieldType.Integer, 1, 2, include_lower=False)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["id"][0] == 2

        # test float field including both bounds
        query = Query.range_query(index.schema, "rating", FieldType.Float, 3.5, 4.0)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        _, doc_address = result.hits[0]
        searched_doc = index.searcher().doc(doc_address)
        assert searched_doc["id"][0] == 1
        
        # test float field excluding the lower bound
        query = Query.range_query(index.schema, "rating", FieldType.Float, 3.5, 4.0, include_lower=False)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0
        
        # test float field excluding the upper bound
        query = Query.range_query(index.schema, "rating", FieldType.Float, 3.0, 3.5, include_upper=False)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0
        
        # test if the lower bound is greater than the upper bound
        query = Query.range_query(index.schema, "rating", FieldType.Float, 4.0, 3.5)
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0
        
    def test_range_query_dates(self, ram_index_with_date_field):
        index = ram_index_with_date_field
        
        # test date field including both bounds
        query = Query.range_query(
            index.schema, 
            "date", 
            FieldType.Date, 
            datetime.datetime(2020, 1, 1), 
            datetime.datetime(2022, 1, 1)
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2
        
        # test date field excluding the lower bound
        query = Query.range_query(
            index.schema, "date", 
            FieldType.Date, 
            datetime.datetime(2020, 1, 1), 
            datetime.datetime(2021, 1, 1), 
            include_lower=False
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        
        # test date field excluding the upper bound
        query = Query.range_query(
            index.schema, 
            "date", 
            FieldType.Date, 
            datetime.datetime(2020, 1, 1), 
            datetime.datetime(2021, 1, 1), 
            include_upper=False
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0
    
    def test_range_query_ip_addrs(self, ram_index_with_ip_addr_field):
        index = ram_index_with_ip_addr_field
        
        # test ip address field including both bounds
        query = Query.range_query(
            index.schema, 
            "ip_addr", 
            FieldType.IpAddr, 
            "10.0.0.0",
            "10.0.255.255"
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
        
        query = Query.range_query(
            index.schema, 
            "ip_addr", 
            FieldType.IpAddr, 
            "0.0.0.0",
            "255.255.255.255"
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 2
        
        # test ip address field excluding the lower bound
        query = Query.range_query(
            index.schema, 
            "ip_addr", 
            FieldType.IpAddr, 
            "10.0.0.1",
            "10.0.0.255",
            include_lower=False
        )
        
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0
        
        # test ip address field excluding the upper bound
        query = Query.range_query(
            index.schema, 
            "ip_addr", 
            FieldType.IpAddr, 
            "127.0.0.0",
            "127.0.0.1",
            include_upper=False
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 0
        
        # test loopback address
        query = Query.range_query(
            index.schema, 
            "ip_addr", 
            FieldType.IpAddr, 
            "::1",
            "::1"
        )
        result = index.searcher().search(query, 10)
        assert len(result.hits) == 1
    
    def test_range_query_invalid_types(
        self, 
        ram_index, 
        ram_index_numeric_fields, 
        ram_index_with_date_field, 
        ram_index_with_ip_addr_field
    ):
        index = ram_index
        query = Query.range_query(index.schema, "title", FieldType.Integer, 1, 2)
        with pytest.raises(ValueError, match="Create a range query of the type I64, when the field given was of type Str"):
            index.searcher().search(query, 10)
        
        index = ram_index_numeric_fields
        query = Query.range_query(index.schema, "id", FieldType.Float, 1.0, 2.0)
        with pytest.raises(ValueError, match="Create a range query of the type F64, when the field given was of type I64"):
            index.searcher().search(query, 10)
        
        index = ram_index_with_date_field
        query = Query.range_query(index.schema, "date", FieldType.Integer, 1, 2)
        with pytest.raises(ValueError, match="Create a range query of the type I64, when the field given was of type Date"):
            index.searcher().search(query, 10)
        
        index = ram_index_with_ip_addr_field
        query = Query.range_query(index.schema, "ip_addr", FieldType.Integer, 1, 2)
        with pytest.raises(ValueError, match="Create a range query of the type I64, when the field given was of type IpAddr"):
            index.searcher().search(query, 10)
    
    def test_range_query_unsupported_types(self, ram_index):
        index = ram_index
        with pytest.raises(ValueError, match="Text fields are not supported for range queries."):
            Query.range_query(index.schema, "title", FieldType.Text, 1, 2)
        
        with pytest.raises(ValueError, match="Json fields are not supported for range queries."):
            Query.range_query(index.schema, "title", FieldType.Json, 1, 2)
        
        with pytest.raises(ValueError, match="Bytes fields are not supported for range queries."):
            Query.range_query(index.schema, "title", FieldType.Bytes, 1, 2)
        
        with pytest.raises(ValueError, match="Facet fields are not supported for range queries."):
            Query.range_query(index.schema, "title", FieldType.Facet, 1, 2)


"""

