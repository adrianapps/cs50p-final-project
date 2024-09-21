import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional, Any, Dict


class Book(BaseModel):
    model_config = ConfigDict(revalidate_instances="always")

    title: str
    authors: List[str] = ["Unknown author"]
    description: str = "No description"
    categories: List[str] = ["No categories"]
    averageRating: Optional[float] = None
    pageCount: Optional[int] = None
    score: Optional[int] = None

    @field_validator("score")
    def is_valid_score(cls, v):
        if v is not None and not (1 <= v <= 10):
            raise ValueError("Score must be on a scale of 1 to 10")
        return v


def fetch_books(query: str) -> List[Book]:
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    data: Dict[str, Any] = response.json()
    books: List[Book] = []
    if "items" in data:
        for item in data["items"]:
            volume_info = item.get("volumeInfo", {})
            book = Book(**volume_info)
            books.append(book)
    return books


def book_details(books: List[Book], idx: int) -> str:
    return (
        f"Title: {books[idx].title}\n"
        f"Authors: {', '.join(books[idx].authors)}\n"
        f"Description: {books[idx].description}\n"
        f"Categories: {books[idx].categories}\n"
        f"Average Rating: {books[idx].averageRating}\n"
        f"Page Count: {books[idx].pageCount}\n"
        f"Score: {books[idx].score}/10\n"
    )


def book_list(books: List[Book], is_score: bool = False) -> List[str]:
    book_list = []
    if is_score:
        for i, book in enumerate(books):
            book_list.append(
                f"{i + 1}. Title: {book.title}, Authors: {', '.join(book.authors)}, Score: {book.score}/10"
            )
    else:
        for i, book in enumerate(books):
            book_list.append(
                f"{i + 1}. Title: {book.title}, Authors: {', '.join(book.authors)}"
            )
    return book_list


def save_to_json(outfile, completed_books: List[Book]) -> None:
    json.dump([book.model_dump() for book in completed_books], outfile, indent=4)


def get_book_recommendations(completed_books: List[Book], api_key: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    books = "\n".join(
        f"{i + 1}. {b.title} by {','.join(b.authors)}, score: {b.score}"
        for i, b in enumerate(completed_books)
    )

    prompt = (
        "Here's a list of books I've read along with the scores I gave them on a scale of 1 to 10: \n"
        + books
        + "Would you give me some recommendations based on my list?"
    )

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}],
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )

    if response.status_code == 200:
        result = response.json()
        recommendations = result["choices"][0]["message"]["content"]
        return recommendations
    else:
        response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Book browsing and recommendations")
    parser.add_argument("--title", "-t", help="Search books by title", type=str)
    parser.add_argument("--author", "-a", help="Search books by author", type=str)
    parser.add_argument(
        "--completed", "-c", help="View your completed books", action="store_true"
    )
    parser.add_argument(
        "--recommend",
        "-r",
        help="Get book recommendations based on your completed books list. Required OpenAi API KEY in .env",
        action="store_true",
    )
    args = parser.parse_args()

    # Open JSON file containing completed books
    try:
        with open("completed_books.json", "r") as file:
            existing_books = json.load(file)
            completed_books = [Book(**book_data) for book_data in existing_books]
    except (FileNotFoundError, json.JSONDecodeError):
        completed_books = []

    # Handle book recommendations
    if args.recommend:
        load_dotenv()
        key = os.environ.get("API_KEY")
        if key is None:
            sys.exit("Provide OpenAI API Key in .env file")
        if completed_books is not None:
            try:
                recommendations = get_book_recommendations(completed_books, key)
            except requests.HTTPError as e:
                print(f"HTTP error occured: {e}")
            else:
                print(f"Chat GPT recommendations: {recommendations}")
        else:
            print("You have no completed books to base recommendations on")
        sys.exit()

    # Handle browsing completed books
    if args.completed:
        if not completed_books:
            sys.exit("No completed books")

        while True:
            print("\n".join(book_list(completed_books, is_score=True)))
            try:
                idx = int(input("Choose a book to see detail of: "))
                print(book_details(completed_books, idx - 1))
            except (ValueError, IndexError):
                print("Invalid input. You must type a book's number")
                continue

            while True:
                print(
                    "1. Delete this book from your list\n2. Update your score\n3. Go back\n"
                )
                choice = int(input("Choice: "))
                if choice == 1:
                    removed_book = completed_books.pop(idx - 1)
                    with open("completed_books.json", "w") as file:
                        save_to_json(file, completed_books)
                    print(f"{removed_book.title} successfully removed from the list")
                    break
                elif choice == 2:
                    try:
                        updated_score = int(input("New score: "))
                        updated_book = completed_books[idx - 1].model_copy(
                            update={"score": updated_score}
                        )
                        updated_book.model_validate(updated_book, strict=True)
                    except ValueError:
                        print("Invalid input, you must type the book's updated score")
                        continue
                    completed_books[idx - 1] = updated_book
                    with open("completed_books.json", "w") as file:
                        save_to_json(file, completed_books)
                    print(
                        f"{completed_books[idx - 1]} successfully updated to {updated_score}/10"
                    )
                elif choice == 3:
                    break
                else:
                    print("Type either 1, 2 or 3 to pick an option")
                    continue

    # Handle browsing books by titles and authors
    if args.title:
        books = fetch_books(f"intitle:{args.title}")
    elif args.author:
        books = fetch_books(f"inauthor:{args.author}")
    else:
        sys.exit("You must provide --title or --author to browse books.")

    while True:
        print("\n".join(book_list(books)))
        try:
            idx = int(input("Choose a book to see detail of: "))
            print(book_details(books, idx))
        except (ValueError, IndexError):
            print("Invalid input. You must type a book's number")
            continue

        print("1. Mark this book as complete and give it a score\n" "2. Go back")
        while True:
            choice = int(input("Choice: "))
            if choice == 1:
                try:
                    score = int(input("Rate the book on a scale of 1 to 10: "))
                    rated_book = books[idx].model_copy(update={"score": score})
                    rated_book.model_validate(rated_book, strict=True)
                except ValueError as e:
                    print(e)
                    continue

                completed_books.append(rated_book)

                with open("completed_books.json", "w") as file:
                    save_to_json(file, completed_books)
                print(f"Book marked as complete with score {score}/10")
                break
            elif choice == 2:
                break
            else:
                print("Type either 1 or 2 to pick an option")
                continue


if __name__ == "__main__":
    main()
