# BOOK COLLECTOR
## Video Demo:  <https://youtu.be/_zr8rmAvYV4?feature=shared>

## Project Structure:
- `project.py` - main file of the application
- `test_project.py` - test file for project.py
- `completed_books.json` - json file containing information about user's completed books. This file will be created when you rate a book and updated each time you add, update or delete a book
- `.env` - optional file if you want to get recommendations from Chat GPT based on your completed books
- `requirements.txt` - file with dependencies required to run this application

## Description:
My project is a CLI that allows users to manage their book collection and provides them with following functionalities: 
- Browsing books from Google Books API by author or title
- CRUD functionalities on user's book collection:
    - Adding books to their collection by giving them a score
    - Viewing books from their collection
    - Updating scores of their completed books
    - Deleting books from their collection
- Getting personalized book recommendations from Chat GPT based on user's completed books and given scores

## How to run:
**Install requirements**
```bash
pip install requirements.txt
```
**Browse books**
```bash
python project.py --title "book of the five rings"
```
**View completed books**
```bash
python project.py --completed
```

### If you want to get recommendations from Chat GPT

**Create a ```.env``` in file in project directory**
```bash
touch .env
```

**Set your Open AI API key as an environment variable**
```ini
API_KEY="your key"
```

**Get recommendations from Chat GPT**
```
python project.py --recommend
```

## Command Arguments: 
**Search books by title**
```bash
--title TITLE, -t TITLE
```

**Search books by author**
```bash
--author AUTHOR, -a AUTHOR
```

**View your completed books**
```bash
--completed, -c 
```

**Get book recommendations based on your completed books list. Required OpenAi API KEY in .env**

```bash
--recommend, -r       
```

## Design choices and considerations
One of the main challenges was implementing the book recommendation feature. Initially, I considered recommending books based on the highest-rated ones in the user’s favorite categories. However, this approach was limited because not all books have average ratings or categories, and it lacked true personalization. It would mostly suggest popular books rather than those aligned with the user’s unique preferences.

To overcome this, I decided to use a Large Language Model like ChatGPT for generating recommendations. This approach was simple to implement: I send a POST request with the user’s completed books and receive personalized suggestions in return. ChatGPT’s ability to analyze reading patterns and preferences made it a much more powerful and flexible solution than relying solely on category-based recommendations.