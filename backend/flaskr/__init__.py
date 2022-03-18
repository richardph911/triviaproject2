import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selections):
    page = request.args.get('page', 1, type=int)
    start_page = (page - 1) * QUESTIONS_PER_PAGE
    end_page = start_page + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selections]
    current_questions = questions[start_page:end_page]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={'/': {'origin': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PUT, POST, DELETE, OPTIONS, PATCH')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        category_list = Category.query.all()
        categories = {}
        for value in category_list:
            categories[value.id] = value.type

        if len(category_list) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories
        })

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
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # list of questions
        selection = Question.query.all()
        total_question = len(selection)
        current_questions = paginate_questions(request, selection)
        # list of categories
        category_list = Category.query.all()
        categories = {}
        for value in category_list:
            categories[value.id] = value.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': total_question,
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'delete': id
            })
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
    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        new_question = data.get('question')
        new_answer = data.get('answer')
        new_difficulty = data.get('difficulty')
        new_category = data.get('category')

        if ((new_question is None) or (new_answer is None)):
            #flash("Please fill all the required fields")
            abort(422)
        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions
                # 'total_questions': len(Question.query.all())

            })
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search_questions():
        # Get user input
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        # If a search term has been entered, apply filter for question string
        # and check if there are results
        try:
            if search_term:
                selection = Question.query.filter(Question.question.ilike
                                                  (f'%{search_term}%')).all()

            # paginate and return results
            paginated = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions':  paginated,
                'totalQuestions': len(selection),
                'currentCategory': None
            })
        except:
            abort(404)
            
    # @app.route('/questions/search', methods=['POST'])
    # def search_questions():
    #     data = request.get_json()
    #     search_term = data.get('searchTerm')
    #     try:
    #         if search_term:
    #             selection = Question.query.filter(
    #                 Question.question.ilike(f'%{search_term}%')).all()

    #         questions = paginate_questions(request, selection)

    #         return jsonify({
    #             'success': True,
    #             'questions': questions,
    #             'total_questions': len(related_questions)
    #         })
    #     except Exception as e:
    #         print(e)
    #         abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        try:
            selection = Question.query.filter_by(category=category.id).all()
            questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': questions,
                'totalQuestions': len(Question.query.all()),
                'currentCategory': category.type
            })
        except Exception as e:
            print(e)
            abort(400)

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
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            data = request.get_json()
            category = data['quiz_category']
            previous_questions = data['previous_questions']

            if category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(
                    category=category['id']).all()
            # random question if not as previous
            next_question = None
            if(questions):
                next_question = random.choice(questions).format()

            return jsonify({
                'success': True,
                'question': next_question
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': error,
            'message': " Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app
