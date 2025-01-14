from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import inspect
from sqlalchemy.sql import text
import pandas as pd
from operator import itemgetter
from krazy import utility_functions as uf

'''
PostgresSql wrapper functions
For all functions, pass connected engine
'''

def create_connection(username, host, database, password):
    '''
    Create sqlalchemy connection for postgresql
    '''
    url = URL.create(
    drivername="postgresql",
    username=username,
    host=host,
    database=database,
    password=password
)
    return create_engine(url)

def get_schema_names(engine):
    '''
    Takes SQLAlchemy engine and returns schema names as list
    '''
    inspector = inspect(engine)
    return inspector.get_schema_names()

def get_table_names(engine)->dict:
    '''
    Takes SQLAlchemy engine and returns schema wise table names as dictionary
    '''
    inspector = inspect(engine)
    schemas = get_schema_names(engine)
    tables = {}
    for schema in schemas:
        tables[schema] = (inspector.get_table_names(schema=schema))

    return tables

def table_search(table_name: str, engine:create_engine)->list:
    '''
    Searches for given table name in tables on Postgressql Server
    Pass sqlalchemy engine with connection on
    '''

    table_names=get_table_names(engine)
    
    if table_names:
        srch_results = []
        for key in list(table_names.keys()):
            table_names_schema = table_names[key]
            for name in table_names_schema:
                if table_name in name.lower():
                    srch_results.append([key, name])
        return srch_results
    else:
        return None

def get_table_schema(schema:str, table:str, engine:create_engine, df_to_compare=pd.DataFrame())->list[pd.DataFrame, list]:
    '''
    Returns list containing table schema as dataframe and useful columns as list
    '''
    # check if schema and table exists and return schema as dataframe
    tables = get_table_names(engine)
    if table in tables[schema]:
        sql = f'''
        select *
        from information_schema.columns
        where table_schema = '{schema}'
        and table_name = '{table}';
        '''
        df_table_schema = pd.read_sql_query(sql, engine)
        useful_cols = ['table_name', 'column_name', 'udt_name', 'character_maximum_length']

        if df_to_compare.empty:
            pass
        else:
            cols_length = {}
            for col in df_to_compare.columns:
                cols_length[col] = df_to_compare[col].astype(str).str.len().max()
            
            df_table_schema['df_length'] = df_table_schema['column_name'].map(cols_length)
            df_table_schema.loc[df_table_schema['udt_name'].isin(['varchar']), 'Diff'] = df_table_schema.loc[df_table_schema['udt_name'].isin(['varchar']), 'character_maximum_length'] - df_table_schema.loc[df_table_schema['udt_name'].isin(['varchar']), 'df_length']

            useful_cols.append('df_length')
            useful_cols.append('Diff')

        return [df_table_schema, useful_cols]

    else:
        print(f'Table: {table} not found in schema: {schema}')
        return [None, None]

def table_delete(schema, table_name, engine:create_engine)->None:
    '''
    Deletes given tabe on postgresql server
    '''
    
    table_list = table_search(table_name, engine)
    
    cur = engine.connect()
    cur.execute(text(f'Drop table if exists "{schema}".{table_name};'))
    cur.commit()

def create_table(df:pd.DataFrame, schema, table_name, engine:create_engine)->None:
    '''
    Creates table in Postgresql server based on dataframe supplied
    '''

    df_dtypes = uf.dtype_to_df(df)

    df_dtypes['Data type'] = ''
    
    for ind, row in df_dtypes.iterrows():
        if row['Type'] == 'datetime64[ns]':
            df_dtypes.loc[ind, 'Data type'] = 'date'
        elif row['Type'] == 'float64':
            df_dtypes.loc[ind, 'Data type'] = 'float8'
        elif row['Type'] == 'float':
            df_dtypes.loc[ind, 'Data type'] = 'float8'
        elif row['Type'] == 'int':
            df_dtypes.loc[ind, 'Data type'] = 'int8'
        elif row['Type'] == 'int64':
            df_dtypes.loc[ind, 'Data type'] = 'int8'
        elif df[row['Col']].astype(str).str.len().max() <= 90:
            max_len = df[row['Col']].astype(str).str.len().max()
            df_dtypes.loc[ind, 'Data type'] = f'varchar({max_len+10})'
        else:
            df_dtypes.loc[ind, 'Data type'] = 'text'

    col_string = []
    for ind, row in df_dtypes.iterrows():
        col_string.append(f'''"{row['Col']}" {row['Data type']}''')

    col_string = ', '.join(col_string)

    sql = f'Create table "{schema}".{table_name} ({col_string});'
    
    with engine.begin() as conn:
        conn.execute(text(sql))    
    
    # cur = engine.connect()
    # cur.execute(sql)
    # cur.commit()

def dbase_col_checker_adder(schema:str, table_name:str, df_to_compare:pd.DataFrame, engine, speak=False)->None:


    '''Checks if all columns in df exists in database and adds if not'''

    # check if schema exists
    if schema not in get_schema_names(engine):
        if speak:
            print(f'Schema {schema} does not exist')
        return None
    # check if table exists
    if table_name not in get_table_names(engine)[schema]:
        if speak:
            print(f'Table {table_name} does not exist')
        return None

    # get table schma
    results = get_table_schema(schema, table_name, engine, df_to_compare)

    # get results
    df_compared = results[0]

    # get columns to add
    df_cols = uf.dtype_to_df(df_to_compare)
    df_col_diff = df_cols.loc[~df_cols['Col'].isin(df_compared['column_name'].tolist())]

    df_postgrest_col_dict = {
        'datetime64[ns]':'date',
        'float64': 'float8',
        'int':'int8',
        'int64':'int8',
        'object':'text'
    }

    if df_col_diff.empty:
        if speak:
            print('No new columns to add in db')
    else:
        # add columns
        cur = engine.connect()
        for ind, row in df_col_diff.iterrows():
            cur.execute(text(f'''alter table "{schema}"."{table_name}" add column if not exists "{row['Col']}" {df_postgrest_col_dict[str(row['Type'])]} null;'''))
            cur.commit() 
        if speak:
            print(f'New columns added: {df_col_diff['Col']}')    


    # check column length
    if speak:
        print('Checking column length')
    df_compared = df_compared.loc[df_compared['Diff']<0, ['column_name','df_length', 'Diff']]
    cols_to_modify = df_compared['column_name'].tolist()
    if speak:
        print(f'Columns to modify: {cols_to_modify}')
    # correct column length
    cur = engine.connect()
    for col in cols_to_modify:
        revised_len = df_compared.loc[df_compared['column_name']==col,'df_length'].values[0]
        if speak:
            print(f'Correcting column length for {col} to {revised_len}')
        cur.execute(text(f'''alter table "{schema}"."{table_name}" alter column "{col}" type varchar({str(int(revised_len))});'''))
        cur.commit()

    return df_col_diff['Col'].tolist()

def dbase_updater(engine, schema:str, table_to_update:str, df_to_update:pd.DataFrame, unique_col:str)->None:
    '''Update a table in database based on unique column'''
    # delete temp_table if exists
    cur = engine.connect()
    cur.execute(text(f'''drop table if exists "{schema}".temp_table;'''))
    cur.commit()

    # push data in temp table
    df_to_update.to_sql('temp_table', con=engine, schema=schema, if_exists='replace', index=False)
    # get table columns
    df_cols = pd.read_sql_query(f'''select * from "{schema}".{table_to_update} limit 1;''', engine)
    df_cols = df_cols.columns
    
    # generate update query
    update_query = f'''update "{schema}".{table_to_update} tab1 set '''
    for col in df_to_update.columns:
        if col in df_cols:
            update_query += f'''"{col}" = tem."{col}", '''

    # remove ending comma
    update_query = update_query[:-2]

    #col text for md5 check
    cols_temp, cols_tab1 = '', ''

    cols_list = df_to_update.columns.tolist()
    remove_cols = ['folder', 'file_name']
    cols_list = [col for col in cols_list if col not in remove_cols]

    for col in cols_list:
        if col in df_cols:
            cols_temp += f'''tem."{col}" || '''
            cols_tab1 += f'''tab1."{col}" || '''
    if cols_temp.endswith(' || '):
        cols_temp = cols_temp[:-4]
    if cols_tab1.endswith(' || '):
        cols_tab1 = cols_tab1[:-4]
    
    # add from clause
    update_query += f''' from "{schema}".temp_table as tem where tab1."{unique_col}" = 
        tem."{unique_col}" and
        md5(cast(({cols_temp}) as text)) != md5(cast(({cols_tab1}) as text)) returning *;'''
    
    # update in databse
    results = cur.execute(text(update_query))
    cur.commit()
    # delete temp_table
    cur.execute(text(f'''drop table if exists "{schema}".temp_table;'''))
    return results


def dbase_writer(df: pd.DataFrame, schema, table, engine:create_engine, append=True)->None:
    '''
    writes data to table. Accepts following arguments for append:
    True = append to existing data
    False = deletes all rows and then insert data into existing table
    delete_table = delete table, recreate table and writes data
    '''
    cur = engine.connect()

    if schema not in get_schema_names(engine):
        print(f'Schema {schema} does not exist')
        return None
    
    tables = get_table_names(engine)

    if append=='delete_table':
        
        # delete table
        table_delete(schema=schema, table_name=table, engine=engine)
        print(f'Table: {table} deleted')

        # create table
        create_table(df, schema, table, engine)
        print(f'Table: {table} re-created')

    elif append==False:
                        
        # delete rows
        cur.execute(text(f'Delete from "{schema}".{table};'))
        print(f'Deleted all data from table: {table}')

    else:
        pass

    # check and add columns
    new_cols = dbase_col_checker_adder(schema, table, df, engine, speak=False)
    if new_cols is not None:
        print(f'New columns added: {new_cols}')

    # write to db
    df.to_sql(table, engine, if_exists='append', index=False, schema=schema)

def dbase_writer_dup_handled(engine, df_purge:pd.DataFrame, schema:str, table_name:str, unique_col:str=None, files_processed:pd.DataFrame=None,update_dup:bool=False)->int:
    '''
    Writes to database after removing duplicates on given column. Always appends.
    if update_dup=True, updates existing records in database
    '''
    files_written = False
    cur = engine.connect()
    print(f'length of data: {len(df_purge)}')
    if df_purge.empty:
        print('No data to push')
        return None
    else:
        # check if table exists
        dbase_tables = get_table_names(engine)

        if table_name in dbase_tables[schema]:
            pass
        else:
            # create table
            create_table(df_purge, schema, table_name, engine)
            # establish primary key
            cur.execute(text(f'''alter table "{schema}".{table_name} add row_id serial NOT NULL;'''))
            cur.execute(text(f'''alter table "{schema}".{table_name} add constraint {table_name}_pk primary key (row_id);'''))
            cur.commit()

        if unique_col==None:
            pass
        else:
            ## get unique ID in database
            data = cur.execute(text(f'''select distinct "{unique_col}" from "{schema}".{table_name} ;''')).fetchall()
            ## get first element from each element from list of lists
            ref_id = list(map(itemgetter(0), data))

            if update_dup:
                # get duplicates
                df_duplicates = df_purge.loc[df_purge[unique_col].isin(ref_id)]
                # update duplicate in database
                print(f'Updating {len(df_duplicates)} existing records in database')
                results = dbase_updater(engine, schema, table_name, df_duplicates, unique_col)
                files_written = True

            ## remove already existing items
            df_purge = df_purge.loc[~df_purge[unique_col].isin(ref_id)]

        # push data to database
        if df_purge.empty:
            print(f'No new records to push to database')
        else:
            print(f'Pushing {len(df_purge)} records to database')
            dbase_writer(df_purge, schema, table_name, engine, append=True)
            files_written = True
            print(f'Pushed {len(df_purge)} records to database')            

        # push files processed to database
        if files_written:
            if 'file_control' not in dbase_tables['settings']:
                create_table(files_processed, 'settings', 'file_control', engine)
            
            dbase_writer(files_processed, 'settings', 'file_control', engine, append=True)
            print(f'Pushed files processed to database')

            return True
        
        else:
            # return none if no file written
            return None

def build_sql_select(cols:list, table:str, schema:str, follow_through:str=None)->str:
    '''
    builds select sql string based on table name, schema and follow_through given
    '''
    cols = '","'.join(cols)
    if follow_through:
        if cols=='*':
            sql = f'select * from "{schema}".{table} {follow_through};'
        else:
            sql = f'select "{cols}" from "{schema}".{table} {follow_through};'
    else:
        if cols=='*':
            sql = f'select * from "{schema}".{table};'
        else:
            sql = f'select "{cols}" from "{schema}".{table};'

    return sql

