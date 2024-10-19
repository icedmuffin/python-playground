from flask import Flask, render_template, request
import pandas as pd


app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def books():
    book_collection = pd.read_csv("data/book.csv")
    book_collection_dictionary = book_collection.to_dict(orient='records')
    
    return render_template("index.html", book_collection_dictionary = book_collection_dictionary)