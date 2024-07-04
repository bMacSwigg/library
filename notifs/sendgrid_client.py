from python_http_client.exceptions import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from backend.models import Book, User

_SENDGRID_APIKEY_FILE = 'C:\\Users\\User\\Documents\\GitHub\\library\\notifs\\sendgrid.secret'
_EMAIL_FROM = 'library@mcswiggen.me'
_TEMPLATE_ID = 'd-74cf8e9d8c07421ebcc87200c7c3d9e3'


class Email:
    """Handles email notifications."""

    def __init__(self):
        with open(_SENDGRID_APIKEY_FILE, 'r') as file:
            api_key = file.read()
            self.sg = SendGridAPIClient(api_key)

    def sendAlert(self, message, *args):
        print(message)
        message = Mail(
            from_email=_EMAIL_FROM,
            to_emails='brian.mcswiggen+alerts@gmail.com',
            subject='Alert from library',
            html_content=message.format(*args))
        try:
            resp = self.sg.send(message)
            print(resp.status_code)
            print(resp.body)
            print(resp.headers)
        except HTTPError as e:
            print(e.to_dict)

    def sendCheckoutEmail(self, book: Book, user: User):
        message = Mail(
            from_email=_EMAIL_FROM,
            to_emails='brian.mcswiggen+alerts@gmail.com',  # user email
            subject='Checkout Notification')
        message.dynamic_template_data = {
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
        message.template_id = _TEMPLATE_ID
        try:
            resp = self.sg.send(message)
            print(resp.status_code)
            print(resp.body)
            print(resp.headers)
        except HTTPError as e:
            print(e.to_dict)
            

if __name__ == '__main__':
    email = Email()
    book = Book('isbn', 'Babel', 'R.F. Kuang', '', '',
                'http://books.google.com/books/content?id=rkO-zgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
                True, 'Brian', 'Some time')
    user = User(1, 'Brian McSwiggen', 'brian.mcswiggen@gmail.com')
    print(book, user)
    email.sendCheckoutEmail(book, user)
