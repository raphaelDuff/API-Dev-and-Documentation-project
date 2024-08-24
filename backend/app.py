from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.expression import func

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

    CORS(app, resources={r"/*": {"origins": "*"}})

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

    @app.route("/questions", methods=["GET"])
    def get_questions():
        stmt_select_all_questions = select(Question).order_by(Question.id)
        stmt_select_all_categories = select(Category).order_by(Category.id)
        categories = db.session.scalars(stmt_select_all_categories).all()
        dict_categories = {str(category.id): category.type for category in categories}
        questions = db.session.scalars(stmt_select_all_questions).all()
        formatted_questions = paginate_questions(request, questions)

        first_question = db.session.scalars(stmt_select_all_questions).first()
        stmt_current_category = select(Category.type).where(
            Category.id == int(first_question.category)
        )
        selected_category = db.session.scalars(stmt_current_category).one_or_none()

        if selected_category is None:
            abort(422)

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions),
                "categories": dict_categories,
                "current_category": selected_category,
            }
        )

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
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

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

                if count_results > 0:
                    first_question = db.session.scalars(stmt_search_question).first()
                    stmt_current_category = select(Category.type).where(
                        Category.id == int(first_question.category)
                    )
                    selected_category = db.session.scalars(
                        stmt_current_category
                    ).one_or_none()

                    if selected_category is None:
                        abort(422)

                else:
                    selected_category = ""

                return jsonify(
                    {
                        "success": True,
                        "questions": formatted_questions,
                        "total_questions": count_results,
                        "current_category": selected_category,
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
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_questions_by_category(id):
        stmt_category_type = select(Category.type).where(Category.id == id)
        selected_category = db.session.scalars(stmt_category_type).one_or_none()
        if selected_category is None:
            abort(400)

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

    @app.route("/quizzes", methods=["POST"])
    def run_quizzes():
        body = request.get_json(silent=True)
        previous_questions = body.get("previous_questions", None)
        category = body.get("quiz_category", None)
        if category is None:
            abort(400)

        if category["id"] == 0:
            stmt_get_random_question = (
                select(Question)
                .where(Question.id.notin_(previous_questions))
                .order_by(func.random())
                .limit(1)
            )
        else:
            stmt_get_random_question = (
                select(Question)
                .where(Question.category == str(category["id"]))
                .where(Question.id.notin_(previous_questions))
                .order_by(Question.id)
                .order_by(func.random())
                .limit(1)
            )

        random_question = db.session.scalars(stmt_get_random_question).first()
        ramdom_question_formatted = random_question.format()

        return (
            jsonify(
                {
                    "success": True,
                    "question": ramdom_question_formatted,
                }
            ),
            200,
        )

    return app
