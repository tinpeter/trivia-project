import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class QuestionTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.database_name = "trivia_test"
        self.database_user = os.environ.get("DB_USER", "postgres")
        self.database_password = os.environ.get("DB_PASSWORD", "1")
        self.database_host = os.environ.get("DB_HOST", "localhost:5432")
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

        self.new_question = {"question": "Where is Messi from?", "answer": "Argentina", "difficulty": 5, "category": 6}

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get("api/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("api/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_new_questions(self):
        res = self.client().post("api/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))

    def test_delete_questions(self):
        res = self.client().delete("api/questions/1")
        data = json.loads(res.data)

        question = Question.query.order_by(Question.id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)

    def test_get_categories(self):
        res = self.client().get("api/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))

    def test_get_questions_by_category(self):
        res = self.client().get("api/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_search_questions(self):
        search_term = {"searchTerm": "Where"}
        res = self.client().post("api/questions/search", json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_play_quiz(self):
        quiz_round = {"previous_questions": [], "quiz_category": {"type": "Science", "id": 1}}
        res = self.client().post("api/quizzes", json=quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()