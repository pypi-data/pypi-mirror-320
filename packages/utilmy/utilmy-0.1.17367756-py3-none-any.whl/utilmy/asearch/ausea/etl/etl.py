

Geneate synnoymous for industry.
Fuzzy Match for industry.







############## Generate question
def db_create_edge_industry_comlist():
   dirdb= "ztmp/db"
   df   = pd_read_file_s3( dirdb + "/db_sqlite/df_edge_industry_activity.parquet")
   cols = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid',
             'L_cat', 'com_extract', 'content_id', 'date', 'dt', 'info', 'n',
             'news_type', 'score', 'text', 'text_id', 'text_qdrant', 'text_summary',
             'title', 'url']
   df.columns  

   df1 = df.groupby(['L_cat', 'L2_cat', 'L3_cat', 'L3_catid' ]).apply(lambda dfi: dfi['com_extract'].values ).reset_index()
   df1.columns = ['L_cat_full','L2_cat', 'L3_cat', 'L3_catid', 'coms'] 

   df1['L_cat'] = df1['L_cat_full'].str.lower() 

   df1['coms'] = df1['coms'].apply(lambda x:  ";".join(x) )
   
   df1[ df1['L_cat'].str.contains("generative ai")  ].head(1).T

   pd_to_file_s3(df1,  dirdb + "/db_sqlite/df_edge_industry_comlist.parquet")






def clean():
    from utilmy import pd_read_file, pd_to_file, hash_int64
    # preprocessing
    df = pd_read_file("./ztmp/df_LZ_merge_90k.parquet")
    log(df)
    df["text_id"] = df["url"].apply(lambda x: hash_int64(x))
    df.rename(
        columns={"pred-L1_cat": "L1_cat", "pred-L2_cat": "L2_cat", "pred-L3_cat": "L3_cat", "pred-L4_cat": "L4_cat"},
        inplace=True)
    df.fillna("", inplace=True)
    pd_to_file(df, "../ztmp/df_LZ_merge_90k_tmp.parquet")





def str_remove_html_tags(html_string):
    import re
    try:
       # Compile the regex pattern once for efficiency
       CLEANR = re.compile('<.*?>')    
       cleantext = re.sub(CLEANR, '', html_string)
       return cleantext
    except Exception as e:
       log(e)
       return html_string 
       

def str_replace_punctuation(text, val=" "):
    return re.sub(r'[^\w\s]', val, text)



############ Details #######################################################
d0 = "src/engine/usea/ztmp/acontentful"
df = pd.read_json(d0 + "/industry_overview.json" )


df0 = pd_read_file_s3(d0 +"/market_size/*.parquet")

cc = Box({})
cc.cols_marketsize = ['datawrapperurls', 'enabled', 'forecastGraphAxisUnit',
       'forecastGraphData', 'forecastGraphXAxis', 'forecastGraphYAxis',
       'full_description_html', 'id', 'industry_id', 'industry_name',
       'moduleTitle', 'pieChartData', 'testing', 'totalAddressableMarket']


###### Details  ##########################################################
df = df0[[  'industry_id', 'industry_name', 'moduleTitle',  'full_description_html',    ]]
df.columns = ['L3_catid', 'L_cat', 'title',  'text_html',   ]
log(df.head(1).T)



######### Details #################################################################
def indus_clean(x):
    x = str_replace_punctuation(x, val=" ")

    x = x.replace("CCUS", "CCUS Carbon Capture Utilization and Storage")
    x = x.replace("NFTs", "nfts nft Non Fungible Tokens Digital Assets")
    x = x.replace(" CRM", " Customer Relationship Management")
    x = x.replace(" & ", " and ")
    x = x.replace(" Tech", " ").replace(" tech", " ")
    x = " ".join(x.split(" "))
    return x 


df['text_id'] = np.arange(0, len(df))
df['L_cat']   = df['L_cat'].apply(lambda x: indus_clean(x) )
df['url']     = df['L3_catid'].apply(lambda x:  'https://eeddge.com/industry/' + str(x) )
df['text']    = df['text_html'].apply(lambda x: str_remove_html_tags(x) )
df['date']    = date_now(fmt="%Y-%m-%d")


df = df.sort_values(['L_cat'])
for x in df['L_cat'].values:
   print(x)


d1 = "src/engine/usea/ztmp/db/db_sqlite/"
pd_to_file(df, d1 + "/df_edge_industry_marketsize.parquet")




df[ df['L_cat'].apply( lambda x:  'carbon' in str(x).lower().split(" ")  ) ]



################################################################################
oopen(df)
df.columns 


colstxt = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract' ]


[  'contentful_link', 'full_overview_text', 'edge_link', 'enabled', 'id',
   'short_description_html', 'industry_id', 'full_description_html',
   'datawrapperurls', 'industry_name']



##########################################################################################
##########################################################################################
d0 = "src/engine/usea/ztmp/acontentful"
df = pd.read_json(d0 + "/industry_overview.json" )

df.columns 


colstxt = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract' ]


[  'contentful_link', 'full_overview_text', 'edge_link', 'enabled', 'id',
   'short_description_html', 'industry_id', 'full_description_html',
   'datawrapperurls', 'industry_name']



######## Data process ##########################
df            = df[[ 'edge_link', 'full_overview_text', 'industry_name', 'short_description_html', 'industry_id' ]]
df.columns    = ['url',  'text_full',  'L_cat', 'text_short', 'L_catid'  ]



df['text_id'] = np.arange(0, len(df))
df['text']  = df['text_short']
df['date']  = "2024-10-01"
df['title'] = df['L_cat']
df[cols2]


d1 = "/Users/kevin.noel/gitdev/agen/gen_dev/aigen/src/engine/usea/ztmp/db/db_sqlite/"
pd_to_file(df, d1 + "/df_edge_industry_overview.parquet")


cols2  = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]





d0 = "src/engine/usea/ztmp/acontentful"
df = pd.read_json(d0 + "/industry_insight.json" )

df[ df['title'].str.contains('Carbon') ]










######## Data process ##########################
df            = df[[ 'edge_link', 'full_overview_text', 'industry_name', 'short_description_html', 'industry_id' ]]
df.columns    = ['url',  'text_full',  'L_cat', 'text_short', 'L_catid'  ]



df['text_id'] = np.arange(0, len(df))
df['text']  = df['text_short']
df['date']  = "2024-10-01"
df['title'] = df['L_cat']
df[cols2]


d1 = "/Users/kevin.noel/gitdev/agen/gen_dev/aigen/src/engine/usea/ztmp/db/db_sqlite/"
pd_to_file(df, d1 + "/df_edge_industry_overview.parquet")


cols2  = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]





d0 = "src/engine/usea/ztmp/acontentful"
df = pd.read_json(d0 + "/industry_insight.json" )






df[ df['title'].str.contains('Carbon') ]

url="https://www.google.com/alerts/feeds/07358091210874812674/5934016078187640468"



url = entry.link 
title = entry.title 
entry.published
entry.summary 


def str_remove_html_tags(html_string):
    import re
    try:
       # Compile the regex pattern once for efficiency
       CLEANR = re.compile('<.*?>')    
       cleantext = re.sub(CLEANR, '', html_string)
       return cleantext
    except Exception as e:
       log(e)
       return html_string 
       











##########################################################################
######### Training Data for RAG  #########################################

  ######### Company names  ###############################################

/Users/kevin.noel/gitdev/agen/gen_dev/aigen/src/engine/usea/ztmp/db/db_sqlite/df_com_all.parquet

  d2 = "/Users/kevin.noel/gitdev/agen/gen_dev/aigen/src/engine/usea/ztmp/db/db_sqlite/df_com_all.parquet"

  dfc = pd_read_file_s3( dirs3p +"/data/db_dump/daily/com_disruptor_info/*.parquet" )  
  dfc = dfc[[ 'com_id', 'name', 'description_clean', 'com_type' ]] 


  dfc1 = pd_read_file_s3( dirs3p +"/data/db_dump/daily/com_incumbent_info/*.parquet" )
  dfc1 = dfc1[[ 'com_id', 'name', 'description_clean', 'com_type' ]] 

  dfc1 = pd.concat(( dfc1, dfc ))

  dfc1['L_cat'] = ""
  dfc1.columns =  [ 'com_id', 'name', 'description', 'com_type', 'L_cat', ]

  
  dfc1 = pd_read_file_s3(d2)

  dfc1 = dfc1.drop_duplicates(['com_id'])

  dfc1['url'] = dfc1.apply(lambda x: "https://eeddge.com/companies/"+ str(x['com_id']) , axis=1)


  ### https://eeddge.com/companies/39671
  pd_to_file_s3(dfc1, d2 )







    python -m spacy download en_core_web_sm



      alias pydb="python3 -u rag/engine_sql.py"
      export dirtmp="~/gitdev/agen/gen_dev/aigen/ztmp"


    export db="$dirtmp/data/cats/arag/afinal/df_com_all.db"
    export dirparquet="$dirtmp/data/cats/arag/afinal/df_com_all.parquet"
    export dname="df_com_all"


    ### Create SQL table with column settings
        pydb dbsql_create_table --db_path $db --table_name $dname --columns '{"com_id": "VARCHAR(255) PRIMARY KEY", "name": "VARCHAR(255)",  "description": "TEXT",   }'


    ### Insert in sqlite
        export nrows="900000"
        pykg dbsql_save_records_to_db   --dirin $dirparquet   --db_path $db  --table_name $dname --coltext "text"  --colscat 'url,date,title,text,text_summary,L0_catnews,L_cat,com_extract,info,score' --colid "text_id" --nrows $nrows

  
    chmod 777  $db




  ######### industry update
  df = pd_read_file_s3( dirs3p +"/data/db_dump/daily/industry_update_all/*.parquet" )
  ### Index(['content_id', 'dt', 'L3_cat2', 'L3_catid', 'L1_cat', 'L2_cat', 'L3_cat','news_type', 'com_name', 'title', 'text', 'url'],


  cols = ['content_id', 'dt', 'L3_cat2', 'L3_catid', 'L1_cat', 'L2_cat', 'L3_cat','news_type',  'title', 'text', 'url']

  

  df = df.groupby(cols  ).apply( lambda dfi: ";".join( [ str(x)  for x in  dfi['com_name'].values if not pd.isna(x)  ] ) ).reset_index()

  df.columns = cols + ['com_extract']
  df = dfg.reset_index()
  df['com_extract']


  ####### Target field    ####################################################################
  df = df.fillna("")
  df['date']        = df['dt'].apply(lambda x: str(x).split(" ")[0] )  
  df['L_cat']       = df.apply(lambda x: f"{x['L1_cat']} {x['L2_cat']} {x['L3_cat']}" ,axis=1) 
  df['L_cat']       = df['L_cat'].apply(lambda x:  ''.join(c if c.isalpha() else ' ' for c in x) )
  df['L_cat']       = df['L_cat'].apply(lambda x:  x.replace("  ", " ").replace("  ", " ") )

  df['text_qdrant'] = df.apply(lambda x: f"{x['title']}. {x['text']}" ,axis=1) 
  df['L0_catnews']  = df['news_type'].apply(lambda x : x.lower().replace("_", " ") )
  df['info']        = "" #df.apply(lambda x: json.dumps({'origin': 'edge_industry_update'}), axis=1)


  ##### sqlite  
  df['text_summary'] = df.apply(lambda x: f"{x['title']}. {x['text']}" ,axis=1) 
  df['score']        = "1"
  df['text_id'] = df['text_qdrant'].apply(lambda x : hash_textid(x) )

  df['n'] = df['text'].str.len()

  df = df.sort_values('content_id', ascending=False)

  del df['index']


  ccols.cols_qdrant = [ "text_id", 'url', 'date', 'L0_catnews', 'L_cat', 'com_extract', 'text_qdrant', 'info']
  ccols.cols_sqlite = [ "text_id", "url", "date", "L0_catnews", "L_cat", "com_extract", "title", "text", "text_summary", "info", "score" ]
  ccols.cols_rag = ccols.cols_qdrant + [xi for xi in ccols.cols_sqlite if xi not in ccols.cols_qdrant ]
  log( df[ccols.cols_rag].shape )

  pd_to_file_s3(df, "ztmp/data/cats/arag/afinal/df_edge_industry_all.parquet" )





   df1 = df[[  'L2_cat',  'L3_cat']]   

   df['L3_cat'] = df['L3_cat'].apply(lambda x:  ''.join(c if c.isalpha() else ' ' for c in x) )
   df['L3_cat'] = df['L3_cat'].apply(lambda x:  x.replace("  ", " ").replace("  ", " ") )
   dfg           = df[ df['date'].str.contains("2024")  ].groupby("L3_cat").agg({'text_id': 'count'}).reset_index().sort_values(["text_id"], ascending=False)

   for x in dfg['L3_cat'].values:
       print( f'"{x}"')
        


   df['L2_cat'] = df['L2_cat'].apply(lambda x:  ''.join(c if c.isalpha() else ' ' for c in x) )
   df['L2_cat'] = df['L2_cat'].apply(lambda x:  x.replace("  ", " ").replace("  ", " ") )
   dfg           = df[ df['date'].str.contains("2024")  ].groupby("L2_cat").agg({'text_id': 'count'}).reset_index().sort_values(["text_id"], ascending=False)

   for x in dfg['L2_cat'].values:
       print( f'"{x}"')
        

   df.columns         
     ['content_id', 'dt', 'L3_cat2', 'L3_catid', 'L1_cat', 'L2_cat', 'L3_cat',
       'news_type', 'title', 'text', 'url', 'com_extract', 'date', 'L_cat',
       'text_qdrant', 'n', 'text_summary', 'L0_catnews', 'info', 'text_id',
       'score']



   df1         = df[ [ 'news_type',  'L2_cat',  'L3_cat',  ] ]
   df1.columns = ['activity', 'industry_tags1', 'industry_tags2' ]






   df1 = df1.drop_duplicates()
   pd_to_file_s3(df1, 'ztmp/data/cats/arag/questions/Lcats.csv', sep="\t") 


   dfg           = df[ df['date'].str.contains("2024")  ].groupby("L3_cat").agg({'text_id': 'count'}).reset_index().sort_values(["text_id"], ascending=False)


   for x in dfg['L3_cat'].values:
       print( f'"{x}"')
        

                                  L2_cat  text_id
    6   business performance enhancement      877
    9                          computing      821
    24              genomic therapeutics      567
    16            distribution logistics      515
    30                       novel foods      470
    12             digital entertainment      422
    29              next gen automobiles      313
    19            environmental services      306
    1             advanced manufacturing      243
    20    fintech banking infrastructure      227
    33                      primary care      224
    31                 pharma automation      215
    4                           agritech      198
    5         blockchain based computing      196
    3                          aerospace      182
    14                  digital security      175
    18                            energy      166
    21                fintech blockchain      146
    0              advanced air mobility      144
    26                         insurtech      133
    40                 virtual workplace      130
    38                    specialty care      119
    8                climate restoration      117
    25                     holistic care      116
    22                  fintech payments      109
    39                    travel tourism      107
    2                 advanced materials      105
    35                 retail automation       85
    23                 food service tech       84
    27                           martech       81
    7                 climate monitoring       70
    41                       wealth tech       67
    36                        sales tech       62
    15                    digital sports       58
    28            medicinal therapeutics       57
    17                  educational tech       56
    10          connected transportation       49
    37                         self care       27
    34                     property tech       19
    32                 physical security       18
    11           construction automation       10
    13                    digital retail        1

   pd_to_file_s3(dfg, 'ztmp/data/cats/arag/questions/L3_freq_2024.csv', sep="\t") 



import pandas as pd
from collections import Counter

def generate_bigram_frequency(sentence_list):
    """
    sentence_list: list of sentences (need to be split)
    return pandas dataframe with columns ['bigram', 'freq']
    """
    bigrams = [b for s in sentence_list for b in zip(s.split()[:-1], s.split()[1:])]
    bigram_counts = Counter(bigrams)
    df = pd.DataFrame(bigram_counts.items(), columns=['bigram', 'freq'])
    return df[['bigram', 'freq']].sort_values('freq', ascending=False)


dfb = generate_bigram_frequency( dfg['L3_cat'].values )



                                  L3_cat  text_id
76                    precision medicine      433
47          generative ai infrastructure      380
45                     foundation models      364
39                      extended reality      297
46            generative ai applications      296
..                                   ...      ...
34            edtech: corporate learning        8
52           insurtech: commercial lines        8
28                      devops toolchain        1
65     natural language processing tools        1
30  digital retail enhancement platforms        1



  



  ########### News #####################################################
  cols= ['date', 'url', 'text', 'news_type' ]

  #### ['dt', 'com_name', 'com_id', 'com_name2', 'com_id2', 'text', 'url', 'partnership_acquisition', 'partnership_type', 'ind_id', 'ind_name', 'cat_id', 'cat_name', 
  ##'L4_catid', 'L4_cat', 'L1_cat', 'L2_cat', 'L3_cat', 'L1_cat1', 'L2_catid', 'L3_catid', 'L2_catidn', 'L3_cat_des'], dir1 = dirs3p + "/data/db_dump/daily/news_partner_all/df_news_partner_all.parquet"
  dir1 = dirs3p + "/data/db_dump/daily/news_partner_all/df_news_partner_all.parquet"
  df1  = pd_read_file_s3(dir1) 
  #df1 = df1[[ 'dt', 'url', 'text', 'partnership_type' ]]
  #df1.columns   = ['date', 'url', 'text', 'news_type' ]
  df1['origin'] = 'news_partner' 

  df1['com_extract'] = df1['com_name'] +  ";"  + df1['com_name2']  
  df1['activity']    = df1['partnership_type'] 
  df1['date']        = df1['dt']
  df1['L_cat'] =  df1['L1_cat'] + ";" + df1['L2_cat'] + ";" + df1['L3_cat'] + ";" + df1['L4_cat'] 
  df1['title'] = df1['text']
  df1['info']  = ""

  cols1 = [ 'date', 'url', 'title', 'com_extract', 'activity', 'L_cat', 'origin', 'info'       ]
  df2 = df1[cols1]


  #### ['com_id_buyer', 'com_name_buyer', 'L3_catid', 'L3_cat', 'L4_catid', 'L4_cat', 'L4_cat2', 
  ### 'ma_date', 'ma_amount', 'ma_currency', 'ma_type', 'com_id_acquired', 'com_name_acquired', 'funding_amount_acquired', 'title', 'url']
  dir1 = dirs3p + "/data/db_dump/daily/news_merger_all/df_news_merger_all.parquet"
  dfj  = pd_read_file_s3(dir1) 

  dfj['com_extract'] =  dfj['com_name_buyer'] +  ";"  + dfj['com_name_acquired']  
  dfj['activity']    =  dfj['ma_type'] 
  dfj['date']        =  dfj['ma_date']
  dfj['L_cat']       =  dfj['L1_cat'] + ";" + dfj['L2_cat'] + ";" + dfj['L3_cat'] + ";" + dfj['L4_cat'] 
  dfj['info'] = dfj.apply(lambda x: str(x['ma_amount']) + ": " + str(x['ma_currency']) , axis=1)
  dfj['origin'] = 'news_merger' 

  df2 = pd.concat((df2, dfj[cols1] )) 

  def extract_url(html_string):
      import re
      try :
         urls = re.findall(r'href=[\'"]?([^\'" >]+)', html_string)
         return urls[0]
      except Exception as e:
         log(e); return ""    

    dir1 = dirs3p + "/data/db_dump/daily/news_product_all/df_news_product_all.parquet"
    dfj  = pd_read_file_s3(dir1) 
    ##### ['industry_update_item_id', 'date', 'title', 'L3_catid', 'news_type', 'com_id', 'com_name', 'url_text', 'url', 'activity']
    dfj['url']      = dfj['url_text'].apply(lambda x: extract_url(x) )
    dfj['origin']   = 'news_product' 
    dfj['activity'] = dfj['news_type']
    dfj['com_extract'] =  dfj['com_name']  
    dfj['L_cat']       =  dfj['L1_cat'] + ";" + dfj['L2_cat'] + ";" + dfj['L3_cat'] 
    dfj['info']        =  ""

    dfj[cols1]

    df3 = pd.concat((df2[cols1], dfj[cols1] )) 


    #### Cleaning
    df3 = df3.drop_duplicates([ 'url', 'activity' ])

    pd_to_file(df3, "ztmp/data/cats/L0_catnews/rag/df_allnews_internal.parquet")


 


###########################################################################
if __name__ == '__main__':
    import fire 
    fire.Fire()





