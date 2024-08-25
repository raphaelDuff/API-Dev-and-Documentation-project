import os
import unittest
import json
from dotenv import load_dotenv
from sqlalchemy import select
from app import create_app, db
from models import Question


# DATABASE URL
load_dotenv()
db_user = os.getenv("POSTGRESQL_USER")
db_password = os.getenv("POSTGRESQL_PW")
database_name = "trivia_test"
SQLALCHEMY_TEST_DATABASE_URI = (
    f"postgresql://{db_user}:{db_password}@localhost:5432/{database_name}"
)


class TriviaTestCase(unittest.TestCase):
    """This class represents the test case for Trivia flask app"""

    def setUp(self) -> None:
        """Define test variables and initialize app"""
        self.test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_TEST_DATABASE_URI,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
        self.app = create_app(test_config=self.test_config)
        self.client = self.app.test_client()
        self.new_question = {
            "question": "What is Morpheus' hovercraft name in the Matrix movie?",
            "answer": "Nabucodonosor",
            "category": "5",
            "difficulty": 5,
        }

    def tearDown(self) -> None:
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_categories_post_not_allowed(self):
        """Test Categories: POST Method - it should returns not allowed"""
        res = self.client.post("/categories")
        self.assertEqual(res.status_code, 405)

    def test_categories_put_not_allowed(self):
        """Test Categories: POST Method - it should returns not allowed"""
        res = self.client.put("/categories")
        self.assertEqual(res.status_code, 405)

    def test_get_categories(self):
        """Test Categories: GET Method  - it should returns the available categories"""
        res = self.client.get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_paginated_questions(self):
        """Test Home - verify if the paginated Questions page is working"""
        res = self.client.get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client.get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_book(self):
        res = self.client.delete("/questions/2")
        data = json.loads(res.data)
        stmt_select_question_by_id = select(Question).where(Question.id == 2)

        with self.app.app_context():
            selected_question = db.session.scalars(
                stmt_select_question_by_id
            ).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 2)
        self.assertEqual(selected_question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client.delete("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_search_question(self):
        res = self.client.post("/questions", json={"searchTerm": "Lestat"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertGreaterEqual(data["total_questions"], 1)
        self.assertEqual(data["current_category"], "Entertainment")

    def test_search_question_without_results(self):
        res = self.client.post("/questions", json={"searchTerm": "jnbiasdhnfgaihs"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["current_category"], "")

    def test_priorize_search(self):
        """If the new question and the search were provided, the code should use only search term"""
        res = self.client.post(
            "/questions",
            json={
                "question": "Who is the best brazilian AWPer of all time?",
                "answer": "_duff_",
                "difficulty": 5,
                "category": "6",
                "searchTerm": "Lestat",
            },
        )
        data = json.loads(res.data)

        stmt_select_question = select(Question).where(Question.answer == "_duff_")

        with self.app.app_context():
            selected_questions = db.session.scalars(stmt_select_question).one_or_none()

        self.assertEqual(selected_questions, None)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertGreaterEqual(data["total_questions"], 1)
        self.assertEqual(data["current_category"], "Entertainment")

    def test_create_new_question(self):
        res = self.client.post("/questions", json=self.new_question)
        data = json.loads(res.data)

        stmt_select_question = select(Question).where(
            Question.answer == "Nabucodonosor"
        )
        with self.app.app_context():
            selected_questions = db.session.scalars(stmt_select_question).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreaterEqual(len(selected_questions), 1)

    def test_400_create_new_question(self):
        """Fail due to missing Question attribute - No answer provided"""
        res = self.client.post(
            "/questions",
            json={"question": "Who is the best brazilian AWPer of all time?"},
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_quiz_start(self):
        res = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [],
                "quiz_category": {"type": "Geography", "id": "3"},
            },
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_400_quiz_no_previous_question(self):
        res = self.client.post(
            "/quizzes", json={"quiz_category": {"type": "Geography", "id": "3"}}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_400_quiz_no_quiz_category(self):
        res = self.client.post("/quizzes", json={"previous_questions": []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")


if __name__ == "__main__":
    unittest.main()
