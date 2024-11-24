from psycopg2 import pool, OperationalError
import logging
from bcrypt import hashpw, gensalt, checkpw

connection_pool = pool.SimpleConnectionPool(
    1, 20, 
    host="127.0.0.1",
    database="books_db",
    user="",
    password=""
)

def get_connection():
    try:
        return connection_pool.getconn()
    except OperationalError as e:
        logging.error(f"Operational error {e}")


# ------------
# regisration
# ------------


def is_user_already_exist(username:str, email:str) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("select 1 from public.user_management where username = %s or email = %s", (username, email))
            data = cursor.fetchone()
    except Exception as e :
        return f"Execption error {e}"
    finally:
        if connection:
            connection_pool.putconn(connection)

    
    return data is not None

    

def db_save_password(username:str, email:str, password:str):
    # check is user already exist 
    user_exist = is_user_already_exist(username=username, email=email)

    if user_exist:
        return "user already registered"
    

    password_hash = hashpw(password.encode(), gensalt())

    try:
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("INSERT INTO public.user_management (username,email,password) VALUES (%s,%s,%s);", 
                           (username,email,password_hash.decode()))
        connection.commit()
    except Exception as e:
        return f"Exception error {e}"
    finally:
        if connection:
            connection_pool.putconn(connection)
        
    return "user successfully registered"


# ------------
# login
# ------------

def check_password(username:str, given_password:str) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("select password from public.user_management where username = %s;", (username,))
            data = cursor.fetchone()
            hash_password = data[0].encode()
    except Exception as e:
        return f"Exception error {e}"
    finally:
        if connection:
            connection_pool.putconn(connection)

    return checkpw(given_password.encode(), hash_password)


