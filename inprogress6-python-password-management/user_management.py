import hashlib
import secrets
from psycopg2 import pool, OperationalError
import logging

connection_pool = pool.SimpleConnectionPool(
    1, 20, 
    host="127.0.0.1",
    database="user_management",
    user="",
    password=""
)

def get_connection():
    try:
        return connection_pool.getconn()
    except OperationalError as e:
        logging.error(f"Operational error {e}")


def hash_password(password:str, salt:str):
    password_encoded = password.encode("utf-8")
    password_hash = hashlib.sha256(password_encoded+salt)
    
    return password_hash.hexdigest()


def generate_random_salt():
    return secrets.token_hex(5)


def db_save_password(username:str, password:str):
    user_salt = generate_random_salt
    salt_password_hash = hash_password(password=password, salt=user_salt)






my_password = "test"
my_salt = generate_random_salt()
print(my_password)
print(my_salt)
print(hash_password(my_password, my_salt))