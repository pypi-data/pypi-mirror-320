"""

"""

if "import":
    import os, time, traceback, warnings, logging, sys, sqlite3
    warnings.filterwarnings("ignore")


    from collections import Counter
    import json, warnings, spacy, pandas as pd, numpy as np
    from dataclasses import dataclass

    ### KG
    from neo4j import GraphDatabase

    # NLP
    from transformers import (pipeline)
    import spacy
    spacy_model = None

    import llama_index.core
    llama_index.core.set_global_handler("simple")

    ############################################
    from utilmy import pd_read_file, os_makedirs, pd_to_file
    from utilmy import log


    ############################################
    from rag.llm import llm_get_answer
    from utils.utils_base import torch_getdevice, pd_append


################################################################################
def test_create_test_data(dirout="./ztmp/testdata/myraw.parquet"):
    """
    usage: pythpn3 -u enging_kg test_create_test_data --dirout myraw.parquet
    """
    from llama_index.readers.wikipedia import WikipediaReader
    loader = WikipediaReader()
    documents = loader.load_data(
        pages=["Guardians of  Galaxy Vol. 3"], auto_suggest=False
    )
    text_list = documents[0].text.split("\n")
    # remove short lines
    text_list = [text for text in text_list if len(text) > 20]
    text_df = pd.DataFrame(text_list, columns=["text"], dtype=str)
    pd_to_file(text_df, dirout, show=1)


def test0():
    triplet_extractor = pipeline('translation_xx_to_yy', model='Babelscape/mrebel-base',
                                 tokenizer='Babelscape/mrebel-base')

    # We need to use  tokenizer manually since we need special tokens.
    msg = " Red Hot Chili Peppers were formed in Los Angeles by Kiedis, Flea"
    extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(msg,
                                                                                 src_lang="en", return_tensors=True,
                                                                                 return_text=False)[0][
                                                                   "translation_token_ids"]])  # change __en__ for  language of  source.
    log(extracted_text[0])



####################################################################################
#######  doc_id Storage  ###########################################################
def dbsql_fetch_text_by_doc_ids(db_path="./ztmp/db/db_sqlite/datasets.db",
                                table_name: str = "agnews",

                                cols=None,
                                text_ids: list = None) -> list:
    """Fetches text from a local SQLite database based on given document IDs.

    Args:
        db_name (str):     Name of SQLite database file.     : "datasets.db".
        table_name (str):  Name of table in database.     : "agnews".
        text_ids (list):   List of text IDs to fetch text for.     : None.

    Returns:
        list: A list of text strings corresponding to fetched document IDs.

    """
    cols = ['text_id, text'] if cols is None else cols
    colss = ",".join(cols)

    conn = sqlite3.connect(f"{db_path}")
    c    = conn.cursor()

    if text_ids is not None:
        text_ids = tuple([str(text_id) for text_id in text_ids])
    else:
        text_ids = []    

    if len(text_ids) == 1:
        query = f"SELECT {colss} FROM {table_name} WHERE text_id = '{text_ids[0]}'"

    elif len(text_ids) == 0:
        query = f"SELECT {colss} FROM {table_name} "

    else:
        query = f"SELECT {colss} FROM {table_name} WHERE text_id IN {text_ids}"
    log(query)
    c.execute(query)
    log('query done')

    headers = c.description
    results = c.fetchall()

    # zip headers with results
    results = [{headers[i][0]: row[i] for i in range(len(headers))} for row in results]
    conn.close()

    if text_ids is not None and len(text_ids)>0 :
       # sort by original order of text_ids
       results = sorted(results, key=lambda x: text_ids.index(x["text_id"]))
    return results



def dbsql_fetch_text_by_doc_ids_sqlachemy(db_name="sqlite:///ztmp/db/db_sqlite/datasets.db",
                                          table_name="agnews", doc_ids=None, ):
    """Fetches text from a local SQL database based on given document IDs.

    Args:
        db_name (str):  name of SQLite database file.     : "datasets.db".
        table_name (str):  name of table in database.     : "agnews".
        doc_ids (list):  list of document IDs to fetch text for.     : None.

    Returns:
        list: A list of text strings corresponding to fetched document IDs.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.sql import select, column, table
    engine = create_engine(db_name)
    Session = sessionmaker(bind=engine)
    session = Session()

    # doc_ids     = tuple(doc_ids)  # Ensure doc_ids is a tuple
    # query_table = table(table_name, column('id'), column('text'))
    # query       = select([query_table]).where(column('id').in_(doc_ids))

    doc_ids = tuple([str(docid) for docid in doc_ids])  # Ensure doc_ids is a tuple
    raw_sql = text(f"SELECT id, text FROM {table_name} WHERE id IN :doc_ids")

    result = session.execute(raw_sql, {'doc_ids': doc_ids})
    results = [{column: value for column, value in zip(result.keys(), row)} for row in result.fetchall()]

    session.close()
    return results



def dbsql_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    existing_tables = [row[0] for row in cursor.fetchall()]
    return table_name in existing_tables


def dbsql_create_table(db_path="./ztmp/db/db_sqlite/datasets.db", table_name: str = "agnews", columns: dict = None):
    """
    Create a table in SQLite with the specified columns.
    Parameters:
    db_name (str): The name of the SQLite database file.
    table_name (str): The name of the table to create.
    columns (dict): A dictionary where keys are column names and values are the data types (e.g., "TEXT", "INTEGER").

    Example:
    create_table("example.db", "students", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER",
        "grade": "REAL"
    })
    """
    conn = None
    from utilmy import os_makedirs
    os_makedirs(db_path) ### create if no exist
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if columns is None:
            sql_query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        text_id VARCHAR(255) PRIMARY KEY,
                        text TEXT
                    )
                """
        else:
            # Create the SQL statement for creating the table
            columns_def = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
            sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def});"
        cursor.execute(sql_query)

        conn.commit()
        print(f"Table '{table_name}' created successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def dbsql_save_records_to_db(dirin="ztmp/bench/norm/ag_news/*/*.parquet",
                             db_path="./ztmp/db/db_sqlite/datasets.db",
                             table_name="agnews", coltext="text",
                             colscat:list = None,
                             colid="text_id", nrows: int = -1):
    """Saves records from a path of Parquet files to a local SQLite database.

    Args:
        dirin (str )     : path containing Parquet files.     : "ztmp/bench/norm/ag_news/*/*.parquet".
        db_path (str )   : path to SQLite database.     : "./ztmp/db/db_sqlite/datasets.db".
        table_name (str ): name of table in database.     : "agnews".
        coltext (str )   : name of column containing text. 
        colid (str )     : name of column containing text ID. 

    """
    df = pd_read_file(dirin)

    if colscat is None:
        colscat = []

    df = df[[colid, coltext, *colscat]]

    # log(len(df))
    if nrows > 0:
        df = df[:nrows]
    # create mysqlite instance
    os_makedirs(db_path)

    conn = sqlite3.connect(f"{db_path}")
    if dbsql_table_exists(conn, table_name) is False:
        dbsql_create_table(conn, table_name)

    # record_df.to_sql(table_name, conn, if_exists="append", index=False)
    # df = df.rename(columns={colid: "id", coltext: "text"})
    df["text_id"] = df["text_id"].astype("string")
    df.drop_duplicates(subset=["text_id"], keep="first", inplace=True)
    df.to_sql(table_name, conn, if_exists="append", index=False, chunksize=1000)



def dbsql_create_conn(db_uri="sqlite:///ztmp/db/db_sqlite/datasets.db"):
    if "sqlite:///" in db_uri:
        from sqlalchemy import create_engine
        engine = create_engine(db_uri)
        return engine

    elif ".db" in db_uri:
        conn = sqlite3.connect(db_uri)
        return conn







###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()
    # results = neo4j_search_triplets_bykeyword(db_name="neo4j", keywords=["Casio Computer", 'magazine', 'United States'])
    # log(results)
    # df = pd_read_file("ztmp/bench/norm/ag_news/test/df_1.parquet")
    # log(df["id"])




