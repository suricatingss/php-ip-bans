import sqlite3, time, sys
from datetime import datetime, timedelta
from sqlite_handler import returning

def check(ip):
    # Connect to the SQLite database
    with sqlite3.connect("bansystem.sqlite") as conn:
        cursor = conn.cursor()
        result = returning("SELECT * FROM users WHERE IP = ?", (ip,),json_string=False)
        #print(f"{result} -- {type(result)} -- {len(result)}")
        if len(result) > 0:
            result:dict = result[0]
            if bool(int(result["ban_permanent"])) == True:
                return "permanent"
            else:
                return result["ban_time"] if result["ban_time"] is not None else None
        else: return None


def user_strike(ip):
    timeout:(tuple|int|None)
    with sqlite3.connect("bansystem.sqlite") as conn:
        cursor = conn.cursor()
        usr = returning("SELECT * FROM users WHERE IP LIKE ?",(ip,),json_string=False)

        cursor.execute("SELECT value FROM settings WHERE name = 'default_expiry'")
        timeout = cursor.fetchone()
        timeout = int(timeout[0]) if timeout is not None else None

        if len(usr) == 0: # user doesnt exist
            if timeout is not None:
                exp_timestamp = datetime.now() + timedelta(seconds=timeout)
                # Format the date as "YYYY-MM-DD HH:MM:SS"
                formatted_timestamp = exp_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                print(f'{ip} {formatted_timestamp}')
                cursor.execute("INSERT INTO users (IP, strikes, expiry) VALUES (?,?,?)",(ip, 1, formatted_timestamp))
        else:
            user:list = returning("SELECT * FROM users WHERE IP = ?", (ip,), json_string=False)
            user:dict = user[0]
 
            
            if timeout is None: 
                cursor.execute("UPDATE users SET strikes = strikes + 1 \
                            WHERE IP LIKE ?",(ip,))
                    
            elif user["ban_time"] is not None: # the user is banned
                ban_time = datetime.strptime(user["ban_time"], "%Y-%m-%d %H:%M:%S")
                diff = ban_time - datetime.now()
                raw_time = datetime.now() + diff + timedelta(seconds=timeout)
                proper_time = raw_time.strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("UPDATE users SET strikes = strikes + 1, expiry = ? \
                            WHERE IP LIKE ?",(proper_time, ip))
            else: 
                raw_time = datetime.now() + timedelta(seconds=timeout)
                proper_time = raw_time.strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("UPDATE users SET strikes = strikes + 1, expiry = ? \
                            WHERE IP LIKE ?",(proper_time, ip))
                
            conn.commit()
            user_ban_check(ip)
            
def user_ban_check(ip):
    with sqlite3.connect("bansystem.sqlite") as conn:
        cursor = conn.cursor()
        
        user:list = returning("SELECT * FROM users WHERE IP LIKE ?",(ip,),json_string=False)
        user:dict = user[0]
        
        cursor.execute("SELECT timeout FROM strikes WHERE strike_num = ?",(int(user["strikes"]),))
        
        timeout = cursor.fetchone()
        
        if timeout is not None: # the user will be banned
            timeout = int(timeout[0])
            
            if timeout == 0: pass # No Punishment
            elif timeout == -1:
                # Ban Permanently
                cursor.execute("UPDATE users SET ban_permanent = 1 WHERE IP LIKE",(ip,))
            else:
                # temp ban
                ban_time = datetime.now() + timedelta(seconds=timeout)
                stamp_ban = ban_time.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE users SET ban_time = ? WHERE IP LIKE ?",(stamp_ban, ip))
    
        conn.commit()

def user_clean(ip):
    with sqlite3.connect("bansystem.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE IP = ?", (ip,))
        conn.commit()

def cleanup():
    with sqlite3.connect("bansystem.sqlite") as conn:
        cursor = conn.cursor()
        # Delete expired records (the user must not be banned to be cleared)
        cursor.execute("DELETE FROM users WHERE ban_permanent = FALSE AND (ban_time < CURRENT_TIMESTAMP or ban_time IS NULL) AND expiry < CURRENT_TIMESTAMP AND expiry IS NOT NULL")
        # Automatically nullify the ban if its past time
        cursor.execute("UPDATE users SET ban_time = NULL WHERE ban_time < CURRENT_TIMESTAMP")

if __name__ == "__main__":
    cleanup()
    if sys.argv[1] == "check":
        result:str|None = check(sys.argv[2])
        if result is not None: print(result)
    elif sys.argv[1] == "strike":
        user_strike(sys.argv[2])
    elif sys.argv[1] == "clean":
        user_clean(sys.argv[2])
    else:
        raise AttributeError("Either check, strike or clean")
        