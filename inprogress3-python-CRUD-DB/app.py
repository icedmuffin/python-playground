from flask import Flask, render_template, request
import pandas as pd
import logging
from psycopg2 import pool, OperationalError

app = Flask(__name__)

connection_pool = pool.SimpleConnectionPool(
    1, 20, 
    host="127.0.0.1",
    database="books_db",
    user="",
    password=""
)

def get_connection():
    try :
        return connection_pool.getconn()
    except OperationalError as e:
        logging.error(f"Operational error {e}")


@app.route("/", methods=['POST', 'GET'])
def home():

    # if there is delete request
    if request.method == 'POST' and request.form['action'] == "delete":

        id = int(request.form.get('id'))
        db_delete_book(id)

    #if there is reset data request
    elif request.method == 'POST' and request.form['action'] == "reset":
        db_reset_data()

    #if there update data request
    elif request.method == 'POST' and request.form['action'] ==  "update":
        id = request.form.get('id')
        title = request.form.get('title')
        author = request.form.get('author')
        price = request.form.get('price')


        validated_book_data, errors = get_and_validate_book_data(id, title, author, price)
        if errors:
            return {"errors" :errors}, 400

        db_update_book(validated_book_data['id'],validated_book_data['title'], validated_book_data['author'], validated_book_data['price'])

    #if there is add data request
    elif request.method == 'POST' and request.form['action'] == "create":
        id = request.form.get('id')
        title = request.form.get('title')
        author = request.form.get('author')
        price = request.form.get('price')

        validated_book_data, errors = get_and_validate_book_data(id, title, author, price)
        if errors:
            return {"errors" :errors}, 400
    
        db_add_book(validated_book_data['title'],
                    validated_book_data['author'],
                    validated_book_data['price'])


    books = db_get_book_data()
    
    return render_template("index.html", books = books)


@app.route("/add", methods=['POST', 'GET'])
def add_book():
    return render_template("add.html")


@app.route("/edit/<int:id>", methods=['POST', 'GET'])
def edit_page(id):
    # get the product of releveant id
    
    book = db_get_specific_book_data(id)
    return render_template("edit.html", book = book)



def db_get_book_data():
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("SELECT id,title,author,price from public.books ORDER BY id ASC;")
            book_data = cursor.fetchall()
            books = [
                {"id": row[0], "title": row[1], "author": row[2], "price": float(row[3])} 
                for row in book_data
            ]
        return books
    except Exception as e:
        logging.error(f" Exception Error: {e}")
    
    finally:
        if connection:
            connection_pool.putconn(connection)

def db_get_specific_book_data(id):
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("SELECT id,title,author,price from public.books WHERE id = %s;", (id,))
            data = cursor.fetchone()
            book = {"id": data[0], "title": data[1], "author": data[2], "price": float(data[3])}

        return book
    
    except Exception as e:
        return f" Exception Error: {e}"
    
    finally:
        if connection:
            connection_pool.putconn(connection)

def get_and_validate_book_data(id, title, author, price):
    errors = []

    if not title :
        errors.append("Error : Missing book title")
    if not author :
        errors.append("Error : Missing book author")
    try:
        price = float(price)
    except ValueError:
        errors.append("Error : book price value must be integer")
    
    return {"id": id, "title": title, "author": author, "price": price}, errors


def db_reset_data():
    df = pd.read_csv("data/book_original.csv")
    
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            for index, row in df.iterrows() :
                cursor.execute("insert into books (title,author,price) VALUES(%s, %s, %s)", (row['title'],row['author'],row['price']))
            connection.commit()
    except Exception as e :
        logging.error(f"Exception error : {e}")
    
    finally :
        if connection:
            connection_pool.putconn(connection)


def db_add_book(title, author, price):
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("insert into books (title,author,price) VALUES(%s, %s, %s)", (title,author,price))
            connection.commit()
    except Exception as e :
        logging.error(f"Exception error : {e}")
    
    finally :
        if connection:
            connection_pool.putconn(connection)
    

def db_delete_book(id):
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("DELETE FROM public.books WHERE id =%s", (id,))
            connection.commit()
    except Exception as e :
        logging.error(f"Exception error : {e}")
    
    finally:
        if connection:
            connection_pool.putconn(connection)


def db_update_book(id, title, author, price):
    errors = []
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("UPDATE public.books SET title = %s, author = %s, price =%s WHERE id = %s;", (title, author, price, id))
            connection.commit()
    except Exception as e :
        logging.error(f"Exception error : {e}")
    
    finally:
        if connection:
            connection_pool.putconn(connection)



if __name__ == "__main__":
    app.run(port=8000, debug=True)