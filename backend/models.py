from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Book:
    isbn: str  # ISBN of this book, also serves as primary ID
    title: str  # Full title of this book
    author: str  # Full name of the author
