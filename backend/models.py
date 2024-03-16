from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Book:
    isbn: str  # ISBN of this book, also serves as primary ID
    title: str  # Full title of this book
    author: str  # Full name of the author
    category: str  # Type of book, e.g. "Fiction"
    year: str  # Publication year
    thumbnail: str  # URL to a cover thumbnail (~128px width)
