import json
import requests

from backend.models import Book, User

_MAILGUN_APIKEY_FILE = 'C:\\Users\\User\\Documents\\GitHub\\library\\notifs\\mailgun.secret'
_EMAIL_FROM = 'Brian\'s Library <library@mcswiggen.me>'
_CHECKOUT_TEMPLATE = 'Checkout Notification'
_RETURN_TEMPLATE = 'Return Notification'


class Email:

    def __init__(self):
        with open(_MAILGUN_APIKEY_FILE, 'r') as file:
            self.api_key = file.read()

    def send_checkout_message(self, book: Book, user: User):
        subs = {
            'book': {
                'title': book.title,
                'author': book.author,
                'thumbnail': book.thumbnail
            },
            'user': {
                'name': user.name
            },
            'checkout_time': book.checkout_time
        }
        subject = 'Thanks for borrowing \'%s\'' % book.title
        self.send_message([user.email], subject, _CHECKOUT_TEMPLATE, subs)

    def send_return_message(self, book: Book, user: User, ret_time: str):
        subs = {
            'book': {
                'title': book.title,
                'author': book.author,
                'thumbnail': book.thumbnail
            },
            'user': {
                'name': user.name
            },
            'return_time': ret_time
        }
        subject = 'Thanks for returning \'%s\'' % book.title
        self.send_message([user.email], subject, _RETURN_TEMPLATE, subs)

    def send_message(self, to_emails, subject, template, substitutions):
        subs = json.dumps(substitutions)
        resp = requests.post(
            'https://api.mailgun.net/v3/mg.mcswiggen.me/messages',
            auth=('api', self.api_key),
  	    data={'from': _EMAIL_FROM,
                'to': to_emails,
  		'subject': subject,
                'template': template,
  		'h:X-Mailgun-Variables': subs})
        print(resp.status_code)
        print(resp.text)

    def send_test_message(self):
        book = Book('isbn', 'Babel', 'R.F. Kuang', '', '',
                'http://books.google.com/books/content?id=rkO-zgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
                True, 'Brian', 'Some time')
        user = User(1, 'Brian McSwiggen', 'brian.mcswiggen@gmail.com')
        self.send_checkout_message(book, user)


class FakeEmail(Email):

    def send_message(self, to_emails, subject, template, substitutions):
        print(to_emails, subject, template, substitutions)

if __name__ == '__main__':
    email = Email()
    email.send_test_message()
