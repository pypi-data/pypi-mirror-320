

```python 



#################################################################################
##### LZ dataset indexing

from utilmy import pd_read_file, pd_to_file, hash_int64
# preprocessing
df = pd_read_file("../ztmp/df_LZ_merge_90k.parquet")
df["text_id"] = df["url"].apply(lambda x:hash_int64(x))
df.rename(columns={"pred-L1_cat":"L1_cat", "pred-L2_cat":"L2_cat", "pred-L3_cat":"L3_cat", "pred-L4_cat":"L4_cat"}, inplace=True)
df.fillna("", inplace=True)
pd_to_file(df, "../ztmp/df_LZ_merge_90k_tmp.parquet")




## qdrant sparse indexing

# create collection
python3 -u rag/engine_qd.py  qdrant_sparse_create_collection --server_url "http://localhost:6333" --collection_name "LZnews"

# set payload settings
python3 -u rag/engine_qd.py  qdrant_update_payload_indexes --server_url "http://localhost:6333" --collection_name "LZnews" --payload_settings "{'L0_catnews': 'text', 'L1_cat': 'text', 'L2_cat': 'text', 'L3_cat': 'text', 'L4_cat': 'text'}"

# index documents
python3 -u rag/engine_qd.py qdrant_sparse_create_index --dirin "../ztmp/df_LZ_merge_90k_tmp.parquet" --server_url "http://localhost:6333" --collection_name "LZnews" --colscat "['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'text_id', 'title']" --coltext "text" --batch_size 1 --max_words 256


####################################
# sqlite data saving

# create table with column settings
python3 -u rag/engine_kg.py dbsql_create_table --db_path "../ztmp/db/db_sqlite/datasets.db" --table_name "LZnews" --columns '{"text_id": "VARCHAR(255) PRIMARY KEY","url": "VARCHAR(255)", "title": "VARCHAR(255)", "date": "VARCHAR(255)", "text": "TEXT", "text_summary": "TEXT", "L0_catnews": "VARCHAR(255)", "L1_cat": "VARCHAR(255)", "L2_cat": "VARCHAR(255)", "L3_cat": "VARCHAR(255)", "L4_cat": "VARCHAR(255)", "com_extract": "VARCHAR(255)"}'


# insert records in sqlite
python3 -u engine_kg.py dbsql_save_records_to_db --db_path "../ztmp/db/db_sqlite/datasets.db" --table_name "LZnews" --coltext "text" --colscat '["url", "date", "title","text", "text_summary", "L0_catnews", "L1_cat", "L2_cat", "L3_cat", "L4_cat", "com_extract"]' --colid "text_id" --nrows -1















```




## KG models/finetuning
``` 
3. [Babelscape/rebel-large · Hugging Face](https://huggingface.co/Babelscape/rebel-large)
2. [ibm/knowgl-large · Hugging Face](https://huggingface.co/ibm/knowgl-large)
2. [EmergentMethods/gliner_large_news-v2.1 · Hugging Face](https://huggingface.co/EmergentMethods/gliner_large_news-v2.1)
3. [GLiNER HandyLab - a Hugging Face Space by knowledgator](https://huggingface.co/spaces/knowledgator/GLiNER_HandyLab)
4. [21iridescent/REBEL-ComSci · Hugging Face](https://huggingface.co/21iridescent/REBEL-ComSci)
5. https://alexford9296.medium.com/so-you-want-to-graph-your-business-knowledge-4dc8b3538395

```