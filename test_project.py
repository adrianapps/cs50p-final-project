import os
import json
import requests
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from io import StringIO
from project import (
    Book,
    fetch_books,
    book_details,
    book_list,
    save_to_json,
    get_book_recommendations,
)

mock_book_data = {
    "title": "Test Book",
    "authors": ["Test Author"],
    "description": "Test Description",
    "categories": ["Test Category"],
    "averageRating": 4.5,
    "pageCount": 300,
    "score": None,
}

mock_api_response = {"items": [{"volumeInfo": mock_book_data}]}


def test_book_creation():
    book = Book(**mock_book_data)
    assert book.title == mock_book_data["title"]
    assert book.authors == mock_book_data["authors"]
    with pytest.raises(ValueError):
        Book(**{**mock_book_data, "score": 11})


@patch("project.requests.get")
def test_fetch_books(mock_get):
    mock_get.return_value.json.return_value = mock_api_response
    books = fetch_books("test")

    len(books) == 1
    books[0].title = mock_book_data["title"]
    books[0].authors = mock_book_data["authors"]


def test_book_details():
    book = Book(**mock_book_data)
    books = []
    books.append(book)
    idx = 0

    details = (
        f"Title: {books[idx].title}\n"
        f"Authors: {', '.join(books[idx].authors)}\n"
        f"Description: {books[idx].description}\n"
        f"Categories: {books[idx].categories}\n"
        f"Average Rating: {books[idx].averageRating}\n"
        f"Page Count: {books[idx].pageCount}\n"
        f"Score: {books[idx].score}/10\n"
    )

    assert book_details(books, idx) == details
    with pytest.raises(IndexError):
        book_details(books, 1)
    with pytest.raises(TypeError):
        book_details(books, "invalid value")
        book_details(4, idx)


def test_book_list():
    book = Book(**{**mock_book_data, "score": 7})
    books = []
    books.append(book)
    with_score = [
        f"1. Title: {book.title}, Authors: {', '.join(book.authors)}, Score: {book.score}/10"
    ]
    without_score = [f"1. Title: {book.title}, Authors: {', '.join(book.authors)}"]
    assert book_list(books) == without_score
    assert book_list(books, True) == with_score
    with pytest.raises(TypeError):
        book_list(2)


def test_save_to_json():
    book = Book(**mock_book_data)
    books = []
    books.append(book)
    expected_content = json.dumps([book.model_dump()], indent=4)

    outfile = StringIO()
    save_to_json(outfile, books)
    outfile.seek(0)
    content = outfile.read()
    assert content == expected_content


def test_get_book_recommendations():
    book = Book(**{**mock_book_data, "score": 9})
    books = []
    books.append(book)

    # This will fail if you don't provide open ai api key in .env file
    # load_dotenv()
    # api_key = os.environ.get("API_KEY")
    # assert isinstance(get_book_recommendations(books, api_key), str)
    with pytest.raises(requests.HTTPError):
        get_book_recommendations(books, "fake key")
