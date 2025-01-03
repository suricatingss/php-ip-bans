import sqlite3, sys, json
from os import path, getcwd
from typing import Union

db = sqlite3.connect("bansystem.sqlite")
cursor = db.cursor()

def non_return(query:str, args:Union[tuple, list, None] = None):
    if args is None: cursor.execute(query)
    else: cursor.execute(query,args)
    db.commit()

def returning(query:str, args:Union[tuple,list, None] = None, json_string = True):
    if args is None: cursor.execute(query)
    else: cursor.execute(query,args)
    rows = cursor.fetchall()
    # Fetch the titles
    column_names = [description[0] for description in cursor.description]
    
    # Combine into a list of dictionaries
    result = [dict(zip(column_names, row)) for row in rows]
    
    return json.dumps(result) if json_string == True else result

def array_convert(array:list):
    args = []
    for arg in array:
        if arg.lower() == "null": args.append(None)
        elif arg == "true": args.append(True)
        elif arg == "false": args.append(False)
        else: 
            try: # converter para INT
                num = int(arg)
                args.append(num)
            except ValueError: # converter para FLOAT
                try:
                    num = float(arg)
                    args.append(num)
                except ValueError: # é uma string
                    args.append(arg)
    return args
    

if __name__ == "__main__":
    stmt = sys.argv[1]
    args = array_convert(sys.argv[2:])
    
    for arg in args:
        print(f"{type(arg)} -- {arg}")
    
    if stmt.split(' ')[0].upper() in ("SELECT","SHOW","DESCRIBE"): 
        r = returning(stmt, args, json_string=True)
        print(r)
        #print(r[1:len(r) - 1])
    else: non_return(stmt, args)  
