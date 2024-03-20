from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Book:
    isbn: str  # ISBN of this book, also serves as primary ID
    title: str  # Full title of this book
    author: str  # Full name of the author
    category: str  # Type of book, e.g. "Fiction"
    year: str  # Publication year
    thumbnail: str  # URL to a cover thumbnail (~128px width)
    is_out: bool = False  # True if the book is currently checked out
    checkout_user: str = ''  # The user who checked it out (only set if is_out)
    checkout_time: str = ''  # Timestamp of checkout (only set if is_out)
