from flask import Flask, render_template, request, jsonify
import pandas as pd
import logging
from psycopg2 import pool, OperationalError
import strawberry
from strawberry.flask.views import GraphQLView
from typing import Optional, List
import user_management

app = Flask(__name__)

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

# Define GraphQL types directly as Python classes
@strawberry.type
class Book:
    id: int
    title: str
    author: str
    price: float

@strawberry.type
class GQLResponse:
    messege: str
    code: int

# Define GQL query class with resolvers
@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        book_data = db_get_book_data()
        
        return [
            Book(
                id=book["id"],
                title=book["title"],
                author=book["author"],
                price=book["price"]
            )
            for book in book_data
        ]
    
    @strawberry.field
    def getBook(self, id: Optional[int] = None, 
                title: Optional[str] = None, 
                author: Optional[str] = None, 
                price:Optional[float] = None) -> List[Book]:
        
        book_data = db_get_book_data()

        if title:
            book_data = [book for book in book_data if title.lower() in book["title"].lower()]
        
        if author:
            book_data = [book for book in book_data if author.lower() in book["author"].lower()]

        if id != None:
            book_data = [book for book in book_data if id == book['id']]
        
        if price != None:
            book_data = [book for book in book_data if price == book['price']]


        return [
            Book(
                id=book["id"],
                title=book["title"],
                author=book["author"],
                price=book["price"]
            )
            for book in book_data
        ]


    @strawberry.field
    def deleteBook(self, id:int) -> GQLResponse:
        messege = db_delete_book(id)

        if messege == "success" :
            code = 200
        else :
            code = 500
        
        return GQLResponse(
            messege=messege,
            code=code
        )
    

    @strawberry.field
    def addBook(self, title:str, author:str, price:int) -> GQLResponse:
        messege = db_add_book(title, author, price)

        if messege == "success" :
            code = 200
        else :
            code = 500
        
        return GQLResponse(
            messege=messege,
            code=code
        )


    @strawberry.field
    def updateBook(self, id:int, title:str, author:str, price:int) -> GQLResponse:
        messege = db_update_book(id, title, author, price)

        if messege == "success" :
            code = 200
        else :
            code = 500
        
        return GQLResponse(
            messege=messege,
            code=code
        )



schema = strawberry.Schema(query=Query)

# Add the GraphQL route
app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql_view", schema=schema))


@app.route("/", methods=['POST', 'GET'])
def home():

    # if there is delete request
    if request.method == 'POST' and request.form['action'] == "delete":

        id = int(request.form.get('id'))
        db_delete_book(id)

    #if there is reset data request
    elif request.method == 'POST' and request.form['action'] == "reset":
        db_reset_data()

    #if there is backup data request
    elif request.method == 'POST' and request.form['action'] == "save_to_csv":
        db_save_existing_table_to_scv()

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


@app.route("/register", methods=['POST', 'GET'])
def register():
    return render_template('register.html')

# -----------------
# Rest api
# -----------------

@app.route("/getBooks", methods=['GET'])
def api_get_books():
    books = db_get_book_data()
    books_json = {
        "books":[
            {"id" : book["id"],
             "author" : book["author"],
             "title" : book["title"],
             "price" : book["price"]}
            for book in books
        ]
    }
    
    return jsonify(books_json), 200


@app.route("/addBook", methods=['POST'])
def api_add_book():
    data = request.get_json()
    id = 1
    title = data.get('title')
    author = data.get('author')
    price = data.get('price')

    validated_book_data, errors = get_and_validate_book_data(id, title, author, price)
    if errors:
        return {"errors" :errors}, 400
    
    db_response = db_add_book(validated_book_data['title'],
                    validated_book_data['author'],
                    validated_book_data['price'])
    
    if db_response == "success" :
        return jsonify({"message": "Book added successfully"}), 201
    else :
        return jsonify({"message": db_response}), 500


@app.route("/deleteBook", methods=['POST'])
def api_delete_book():
    data = request.get_json()
    id = data.get('id')

    print(id)
    print(type(id))

    if not id :
        return jsonify({"message" : "error missing id"}), 400
   
    try:
        id = float(id)
    except ValueError:
        return jsonify({"message" : "Error, book id value must be integer"}), 400
        
    message = db_delete_book(id)

    status_code = 200 if message == "success" else 400
    return jsonify({"message": message}), status_code


@app.route("/updateBook", methods=['POST'])
def api_update_book():
    data = request.get_json()
    id = data.get('id')
    author = data.get('author')
    title = data.get('title')
    price = data.get('price')

    validated_book_data, errors = get_and_validate_book_data(id, title, author, price)
    if errors:
        return jsonify({"errors" :errors}), 400

    message = db_update_book(validated_book_data['id'],validated_book_data['title'], validated_book_data['author'], validated_book_data['price'])
    status_code = 200 if message == "success" else 400

    return jsonify({"message" : message}), status_code
   

def db_save_existing_table_to_scv():
    books = db_get_book_data()
    df = pd.DataFrame(books)
    df.drop(columns=['id'])
    df.to_csv("data/book_original.csv", index=False)
        
    
    return books


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
        errors.append("Error : book price value must be float")
    
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
            message = "success"
    except Exception as e :
        message = f"Exception error : {e}"
        logging.error(message)
    finally :
        if connection:
            connection_pool.putconn(connection)

    return message
    

def db_delete_book(id):
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("DELETE FROM public.books WHERE id =%s", (id,))
            connection.commit()
            message = "success"
    except Exception as e :
        message = f"Exception error : {e}"
        logging.error(message)
    finally:
        if connection:
            connection_pool.putconn(connection)

    return message


def db_update_book(id, title, author, price):
    try :
        connection = get_connection()
        with connection.cursor() as cursor :
            cursor.execute("UPDATE public.books SET title = %s, author = %s, price =%s WHERE id = %s;", (title, author, price, id))
            connection.commit()
            message = "success"
    except Exception as e :
        message = f"Exception error : {e}"
        logging.error(message)
    
    finally:
        if connection:
            connection_pool.putconn(connection)

    return message


if __name__ == "__main__":
    app.run(port=5000, debug=True)
