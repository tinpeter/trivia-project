import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy, pagination
from flask_cors import CORS
from sqlalchemy import func, not_
from random import choice

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    paginated_selection = selection.paginate(page=page, per_page=QUESTIONS_PER_PAGE)

    questions = [question.format() for question in paginated_selection]

    return questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/api/categories")
    def retrieve_categories():
        try:
            data_list = Category.query.order_by(Category.id).all()
            categories = {category.id: category.type for category in data_list}

            if len(categories) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "categories": categories,
                    "total_categories": len(Category.query.all())
                }
            )
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/api/questions")
    def retrieve_questions():
        try:
            selection = Question.query.order_by(Question.id)
            current_questions = paginate_questions(request, selection)

            # Lấy danh sách các danh mục
            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "categories": formatted_categories
                }
            )
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/api/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id)
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all())
                }
            )

        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/api/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question= body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            if bool(new_question) and bool(new_answer):
                question.insert()
                selection = Question.query.order_by(Question.id)
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )

        except:
            abort(422)
            raise

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/api/questions/search', methods=['POST'])
    def search_questions():
        data = request.json
        try:
            if 'searchTerm' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Missing field: searchTerm'
                }), 400

            search_term = data['searchTerm']
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions
            }), 200
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions)
            }), 200
        except:
            abort(404)

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
    @app.route('/api/quizzes', methods=['POST'])
    def play_quiz():
        data = request.json

        category = data.get('quiz_category')
        previous_questions = data.get('previous_questions', [])

        try:
            query = Question.query.filter(not_(Question.id.in_(previous_questions)))
            if category['id']:
                query = query.filter_by(category=category['id'])
            question = query.order_by(func.random()).first()

            if question:
                formatted_question = question.format()
                return jsonify({
                    'success': True,
                    'question': formatted_question
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'question': None
                }), 200
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    # Handling 404 errors (Not Found)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    # Handling error 422 (Unable to handle)
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    # Handle other unexpected errors
    @app.errorhandler(Exception)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    if __name__ == '__main__':
        app.debug = True
        app.run(host='0.0.0.0', port=5000)

    return app

