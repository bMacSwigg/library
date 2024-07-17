import os
import datetime
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

@app.route('/books/<book_id>', methods=['GET'])
def getBook(book_id):
    """
        getBook() : Retrieve book by ID (currently, ISBN)
    """
    return "Unimplemented", 418

@app.route('/books', methods=['GET'])
def listBooks():
    """
        listBooks() : Retrieve rsvp data by event & RSVP IDs
    """
    if 'query' in request.json:
        print(request.json['query'])
    if 'status' in request.json:
        print(request.json['status'])
    return "Unimplemented", 418

@app.route('/books', methods=['POST'])
def createBook():
    """
        createBook() : Create a new Book.
    """
    return "Unimplemented", 418

@app.route('/books/<book_id>/checkout', methods=['POST'])
def checkoutBook(book_id):
    """
        checkoutBook() :
    """
    return "Unimplemented", 418

@app.route('/books/<book_id>/return', methods=['POST'])
def returnBook(book_id):
    """
        checkoutBook() :
    """
    return "Unimplemented", 418

@app.route('/books/<book_id>/history', methods=['GET'])
def listBookCheckoutHistory(book_id):
    """
        uploadFeedback() : Upload freeform feedback from the site
        Includes the URL that feedback was uploaded from and other metadata
    """
    return "Unimplemented", 418


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
