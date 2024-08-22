import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import delete, select
from sqlalchemy.orm import DeclarativeBase

from models import Question, Category

QUESTIONS_PER_PAGE = 10


# DB/APP Pre-setup
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def paginate_questions(request, selection, page_limit_number=QUESTIONS_PER_PAGE):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * page_limit_number
    end = start + page_limit_number
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None, db=db):
    # create and configure the app
    app = Flask(__name__)

    app.config.from_object("config")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    """
    @TODO - DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO - DONE: Use the after_request decorator to set Access-Control-Allow
    """

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTION"
        )
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "internal server error"}
            ),
            500,
        )

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories", methods=["GET"])
    def get_categories():
        stmt_select_all_categories = select(Category).order_by(Category.id)
        categories = db.session.scalars(stmt_select_all_categories).all()
        dict_categories = {str(category.id): category.type for category in categories}
        if len(categories) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "categories": dict_categories,
            }
        )

    """
    @TODO - DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        stmt_select_all_questions = select(Question).order_by(Question.id)
        stmt_select_all_categories = select(Category).order_by(Category.id)
        categories = db.session.scalars(stmt_select_all_categories).all()
        dict_categories = {str(category.id): category.type for category in categories}
        questions = db.session.scalars(stmt_select_all_questions).all()
        formatted_questions = paginate_questions(request, questions)
        if len(formatted_questions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions),
                "categories": dict_categories,
                "current_category": "All",
            }
        )

    """
    @TODO - DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        try:
            stmt_question_by_id = select(Question).where(Question.id == id)
            selected_question = db.session.scalars(stmt_question_by_id).one_or_none()
            if selected_question is None:
                abort(404)

            db.session.delete(selected_question)
            db.session.commit()

            return (
                jsonify(
                    {
                        "success": True,
                        "deleted": id,
                    }
                ),
                200,
            )
        except Exception as e:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def submit_question():
        body = request.get_json(silent=True)
        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)
        search = body.get("searchTerm", None)
        try:
            if search:
                stmt_search_question = (
                    select(Question)
                    .where(Question.question.icontains(search))
                    .order_by(Question.id)
                )
                search_results = db.session.scalars(stmt_search_question).all()
                formatted_questions = paginate_questions(request, search_results)
                count_results = len(search_results)

                return jsonify(
                    {
                        "success": True,
                        "questions": formatted_questions,
                        "total_questions": count_results,
                        "current_category": "All",
                    }
                )
            else:
                if (
                    (question is None)
                    or (answer is None)
                    or (difficulty is None)
                    or (category is None)
                ):
                    abort(400)

                new_question = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category,
                )

                db.session.add(new_question)
                db.session.commit()

                return (
                    jsonify(
                        {
                            "success": True,
                        }
                    ),
                    200,
                )
        except Exception as e:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    """
    @TODO - DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_questions_by_category(id):
        stmt_category_type = select(Category.type).where(Category.id == id)
        selected_category = db.session.scalars(stmt_category_type).one_or_none()
        if selected_category is None:
            abort(404)

        stmt_select_all_questions = (
            select(Question).where(Question.category == str(id)).order_by(Question.id)
        )
        questions = db.session.scalars(stmt_select_all_questions).all()
        formatted_questions = paginate_questions(request, questions)
        if len(formatted_questions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions),
                "current_category": selected_category,
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app
