# default data 
import grpc
import books_pb2
import books_pb2_grpc
from concurrent import futures
import logging
import pandas as pd

from psycopg2 import pool, OperationalError

from grpc_reflection.v1alpha import reflection

BOOKS = [
    books_pb2.Book(id=1, title="1984", author="George Orwell", price=1500),
    books_pb2.Book(id=2, title="To Kill a Mockingbird", author="Harper Lee", price=1800),
    books_pb2.Book(id=3, title="The Great Gatsby", author="F. Scott Fitzgerald", price=2000),
]


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




class Books(books_pb2_grpc.BooksServicer):
    def GetBooks(self, request, context):
        books = db_get_book_data()
        response = [
            books_pb2.Book(
                id=book['id'],
                title=book['title'],
                author=book['author'],
                price=book['price']
            )
            for book in books
        ]
        
        return books_pb2.GetBooksResponse(
            books=response
            )
    
    def GetBookById(self, request, context):
        book = db_get_specific_book_data(request.id)
        
        response = books_pb2.Book(
            id=book['id'],
            title=book['title'],
            author=book['author'],
            price=book['price']
        )
        
        return books_pb2.GetBookByIdResponse(
            book=response
            )
    
    def AddBook(self, request, context):
        id = 1
        title = request.title
        author = request.author
        price = request.price

        validated_book_data, error = get_and_validate_book_data(id, title, author, price)


        db_response = db_add_book(
            title=validated_book_data['title'],
            author=validated_book_data['author'],
            price=validated_book_data['price'],
        )

        if db_response == "success" :
            code = 201
        else :
            code = 500

        response = books_pb2.GeneralResponse(
            message=db_response,
            code=code
        )

        return books_pb2.AddBookResponse(
            response=response
            )
    
    def EditBook(self, request, context):
        book_id = request.id
        title = request.title
        author = request.author
        price = request.price

        validated_book_data, error = get_and_validate_book_data(book_id, title, author, price)

        db_response = db_update_book(id=validated_book_data['id'], 
                                     title=validated_book_data['title'], 
                                     author=validated_book_data['author'],
                                     price=validated_book_data['price'])

        if db_response == "success" :
            code = 200
        else :
            code = 500


        response = books_pb2.GeneralResponse(
            message=db_response,
            code=code
        )

        return books_pb2.EditBookResponse(response=response)
        
        

    def DeleteBook(self, request, context):
        db_response = db_delete_book(request.id)


        if db_response == "success" :
            code = 200
        else :
            code = 500

        response = books_pb2.GeneralResponse(
            message=db_response,
            code=code
        )
        
        return books_pb2.DeleteBookResponse(
            response=response
        )

        
    
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


def server():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    books_pb2_grpc.add_BooksServicer_to_server(Books(), server)

    SERVICE_NAME = (
        books_pb2.DESCRIPTOR.services_by_name['Books'].full_name,
        reflection.SERVICE_NAME
    )

    reflection.enable_server_reflection(SERVICE_NAME, server)

    server.add_insecure_port("[::]:"+port)
    server.start()
    print("book server listing on port : " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    server()


    


