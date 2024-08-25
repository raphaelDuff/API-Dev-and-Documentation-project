# Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Setting up the Front End
The frontend app was built using create-react-app and uses NPM to manage software dependencies. NPM Relies on the package.json file located in the frontend directory of this repository.
```bash
npm install
```

```bash
npm start
```


## API Reference

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable
- 500: Internal server error

### Endpoints 

`GET '/api/v1.0/categories'`
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category.
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json 
{
    "categories": { "1" : "Science",
    "2" : "Art",
    "3" : "Geography",
    "4" : "History",
    "5" : "Entertainment",
    "6" : "Sports" },
    "success": True
}
```

`GET '/api/v1.0/categories/${id}/questions'`
- Fetches questions for a cateogry specified by id request argument
- Request Arguments: id - integer
- Returns: An object with questions for the specified category, total questions, and current category of the first question returned

```json 
{
    "questions": [
        {
            "id": 1,
            "question": "This is a question",
            "answer": "This is an answer",
            "difficulty": 5,
            "category": 4
        },
    ],
    "total_questions": 100,
    "current_category": "History",
    "success": True
}
```

`GET '/api/v1.0/questions?page=${integer}'`
- Fetches a paginated set of questions, a total number of questions, all categories and current category string.
- Request Arguments: page - integer
- Returns: An object with 10 paginated questions, total questions, object including all categories, and current category string

```json 
{
    "questions": [
        {
            "id": 1,
            "question": "This is a question",
            "answer": "This is an answer",
            "difficulty": 5,
            "category": 2
        },
    ],
    "total_questions": 100,
    "categories": { "1" : "Science",
    "2" : "Art",
    "3" : "Geography",
    "4" : "History",
    "5" : "Entertainment",
    "6" : "Sports" },
    "current_category": "History",
    "success": True
}
```

`DELETE '/api/v1.0/questions/${id}'`
- Deletes a specified question using the id of the question
- Request Arguments: id - integer
- Returns: An object with the success of the operation and the id of the deleted question

```json 
{
    "success": True,
    "id": 2
}
```

`POST '/api/v1.0/questions'`
- Sends a post request in order to search for a specific question by search term
- Request Body
```json
{
    "searchTerm": "this is the term the user is looking for"
}
```
- Returns: any array of questions, a number of totalQuestions that met the search term and the current category string

```json 
{
    "questions": [
        {
            "id": 1,
            "question": "This is a question",
            "answer": "This is an answer",
            "difficulty": 5,
            "category": 5
        },
    ],
    "total_questions": 100,
    "current_category": "Entertainment",
    "success": True
}
```

`POST '/api/v1.0/questions'`
- Sends a post request in order to add a new question
- Request Body
```json
{
    "question":  "Heres a new question string",
    "answer":  "Heres a new answer string",
    "difficulty": 1,
    "category": 3,
}
```
- Returns: the success state - True or False

```json 
{
    "success": True
}
```

`POST '/api/v1.0/quizzes'`
- Sends a post request in order to get the next question
- Request Body
```json
{
    "previous_questions": [1, 4, 20, 15]
    "quiz_category": {"type": "Geography","id": "3"}
}
```
- Returns: a single a question object

```json 
{
    "question": {
        "id": 1,
        "question": "This is a question",
        "answer": "This is an answer",
        "difficulty": 5,
        "category": 3
    }
}
```

## Testing

To deploy and run the tests:

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_app.py
```
