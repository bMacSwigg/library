import json
from urllib.request import urlopen

from library.backend.models import Book


class LookupService:

    GOOGLE_BOOKS_ENDPOINT = 'https://www.googleapis.com/books/v1/volumes?q=isbn:%s'

    def lookupIsbn(self, isbn: str) -> Book:
        res = json.load(urlopen(self.GOOGLE_BOOKS_ENDPOINT % isbn))
        vals = res['items'][0]['volumeInfo']
        title = vals['title'] if 'title' in vals else ''
        authors = vals['authors'] if 'authors' in vals else []
        author = ', '.join(authors)
        if 'mainCategory' in vals:
            category = vals['mainCategory']
        elif 'categories' in vals and len(vals['categories']) > 0:
            category = vals['categories'][0]
        else:
            category = ''
        year = vals['publishedDate'][:4] if 'publishedDate' in vals else ''
        if 'imageLinks' in vals and 'thumbnail' in vals['imageLinks']:
            thumbnail = vals['imageLinks']['thumbnail']
        else:
            thumbnail = ''
        return Book(isbn, title, author, category, year, thumbnail)
