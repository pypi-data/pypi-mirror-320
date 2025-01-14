import pandas as pd
from sqlalchemy import create_engine

from utilmy import log


def create_engine_mysql(dbname='initial'):

    user  = os.environ['MYSQL_USER']
    passw = os.environ['MYSQL_PWD']
    engine = create_engine( f'mysql://{user}:{passw}@host/{dbname}')
    return engine 


def dump_mysql_into_sqlite(dir_sqlite):
    mysql_engine  = create_engine_mysql()
    sqlite_engine = create_engine( f'sqlite:///{dir_sqlite}/file.db')

    for table in mysql_engine.table_names():
        log(table)
        df = pd.read_sql_table(table, mysql_engine)
        df.to_sql(table, sqlite_engine, index=False, if_exists='replace')


