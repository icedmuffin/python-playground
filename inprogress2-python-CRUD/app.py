from flask import Flask, render_template, request
import pandas as pd


app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def home():

    # if there is delete request
    if request.method == 'POST' and request.form['action'] == "delete":

        id = int(request.form.get('id'))
        print(id)
        delete_book(id)

    #if there is reset data request
    if request.method == 'POST' and request.form['action'] == "reset":
        print("reseting data table") 
        reset_data()

    #if there update data request
    if request.method == 'POST' and request.form['action'] ==  "update":

        id = request.form.get('id')
        title = request.form.get('title')
        author = request.form.get('author')
        price = request.form.get('price')

        validated_book_data, errors = get_and_validate_book_data(id, title, author, price)
        if errors:
            return {"errors" :errors}, 400



        update_book(validated_book_data['id'], validated_book_data['title'], validated_book_data['author'], validated_book_data['price'])

    #if there is add data request
    if request.method == 'POST' and request.form['action'] == "create":
        
        id = request.form.get('id')
        title = request.form.get('title')
        author = request.form.get('author')
        price = request.form.get('price')

        validated_book_data, errors = get_and_validate_book_data(id, title, author, price)
        if errors:
            return {"errors" :errors}, 400

        add_book(id, title, author, price)



    book_collection = pd.read_csv("data/book.csv")
    book_collection_dictionary = book_collection.to_dict(orient='records')
    
    return render_template("index.html", book_collection_dictionary = book_collection_dictionary)


@app.route("/add", methods=['POST', 'GET'])
def add_book():
    return render_template("add.html")


@app.route("/edit/<int:id>", methods=['POST', 'GET'])
def edit_page(id):
    # get the product of releveant id
    df = pd.read_csv("data/book.csv")
    book_data = df[df.get('id') == id]
    book_data_dictionary = book_data.to_dict(orient='records')[0]

    print(book_data_dictionary)

    return render_template("edit.html", book_data_dictionary = book_data_dictionary)


def get_and_validate_book_data(id, title, author, price):
    validated_data = {}
    errors = []
    
    if not id :
        errors.append("Error : Missing book id") 
    else:
        try:
            id = int(id)
        except ValueError:
            errors.append("Error : book id value must be integer")
    
    validated_data['id'] = id


    if not title :
        errors.append("Error : Missing book title")
    validated_data['title'] = title
    
    if not author :
        errors.append("Error : Missing book author")
    validated_data['author'] = author

    if not price :
        errors.append("Error : Missing book price")
    else:
        try:
            price = float(price)
        except ValueError:
            errors.append("Error : book price value must be integer")
    validated_data['price'] = price
    
    return validated_data, errors


def reset_data():
    df = pd.read_csv("data/book_original.csv")
    df.to_csv('data/book.csv', index=False)


def add_book(id, title, author, price):
    df = pd.read_csv("data/book.csv")

    new_book = {"id": id, "title": title, "author": author, "price": price}
    df.loc[len(df)] = new_book

    df.to_csv('data/book.csv', index=False)


def delete_book(id):
    df = pd.read_csv("data/book.csv")
    book_index = df[df["id"] == id].index
    df.drop(book_index, inplace=True)
    df.to_csv('data/book.csv', index=False)


def update_book(id, title, author, price):
    df = pd.read_csv("data/book.csv")
    book_index = df[df.get('id') == int(id)].index
    df.loc[book_index]=[id,title,author,price]

    df.to_csv('data/book.csv', index=False)


if __name__ == "__main__":
    app.run(port=8000, debug=True)