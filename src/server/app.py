from dataclasses import asdict
import datetime
from flask import Flask, request, jsonify
import logging
import os

from library.backend.api import BookService, UserService
from library.backend.api import InvalidStateException, NotFoundException
from library.backend.models import Book

# Initialize Flask app
app = Flask(__name__)

@app.route('/books/<book_id>', methods=['GET'])
def getBook(book_id):
    """
        getBook() : Retrieve book by ID (currently, ISBN)
    """
    try:
        book = BookService().getBook(book_id)
    except NotFoundException:
        return "Book with ID '%s' not found" % book_id, 404
    else:
        return jsonify(asdict(book)), 200

@app.route('/books', methods=['GET'])
def listBooks():
    """
        listBooks() : List all books. At most one of 'query' and 'is_out' may
        be specified. If 'query' is specified, returns only books whose title
        or author contains 'query' as a substring. If 'is_out' is specified,
        filters to only books that are (or are not) currently checked out.
    """
    if 'query' in request.args and 'is_out' in request.args:
        return "'query' and 'is_out' filters cannot both be specified", 400

    if 'is_out' in request.args:
        is_out = bool(int(request.args['is_out']))
        books = BookService().listBooksByStatus(is_out)
    elif 'query' in request.args:
        q = request.args['query']
        books = BookService().listBooks(q)
    else:
        books = BookService().listBooks()

    return jsonify(list(map(asdict, books))), 200

@app.route('/books', methods=['POST'])
def createBook():
    """
        createBook() : Create a new Book.
    """
    try: 
        json = request.json['book']
        book = Book(json['isbn'], json['title'], json['author'],
                    json['category'], json['year'], json['thumbnail'])
    except KeyError:
        return "Missing property", 400
    else:
        BookService().createBook(book)
        return "Book created", 200

@app.route('/books/<book_id>/checkout', methods=['POST'])
def checkoutBook(book_id):
    """
        checkoutBook() : Mark this book as checked out by a given user. Book
        must not be currently checked out.
    """
    if 'user_id' not in request.json:
        return "Missing 'user_id' property", 400

    user_id = request.json['user_id']
    # TODO: deal with this not being a real user ID
    user = UserService().getUser(user_id)

    try:
        BookService().checkoutBook(book_id, user)
    except InvalidStateException:
        return "Book with ISBN %s already out" % book_id, 400
    else:
        return "Checked out", 200

@app.route('/books/<book_id>/return', methods=['POST'])
def returnBook(book_id):
    """
        returnBook() : Mark this book as returned, by whoever checked it out.
        Book must be currently checked out.
    """
    try:
        BookService().returnBook(book_id)
    except InvalidStateException:
        return "Book with ISBN %s not checked out" % book_id, 400
    else:
        return "Returned", 200

@app.route('/books/<book_id>/history', methods=['GET'])
def listBookCheckoutHistory(book_id):
    """
        listBookCheckoutHistory() : List the CHECKOUT and RETURN log events
        for this book. Ordered from earliest to latest.
    """
    logs = BookService().listBookCheckoutHistory(book_id)
    return jsonify(list(map(asdict, logs))), 200


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
