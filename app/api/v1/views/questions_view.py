# Questions Views.
from flask import Blueprint, request, jsonify
from ..models.questions_model import QuestionModel
from app.api.v1.models.meetups_model import MeetupsModel
from app.api.v1.utils.utils import requires_token


v1_questions_blueprint = Blueprint('v1_q', __name__, url_prefix='/api/v1')
QUESTION_MODEL = QuestionModel()
MEETUP = MeetupsModel()


@v1_questions_blueprint.route('/questions', methods=['POST'])
@requires_token
def post_question(user):
    """Post a question route."""
    required = ["title", "meetup", "body", "createdBy"]
    try:
        data = request.get_json()
        for items in required:
            if items not in data.keys():
                return jsonify({
                    "status": 400,
                    "error": "Please provide the following fields. " \
                     "`{}`".format(items)
                }), 400
            for key, value in data.items():
                if not value.replace(" ", "").strip():
                    return jsonify({
                        "status": 400,
                        "error": "{} is missing.".format(key)
                        }), 400
        title = data.get("title")
        meetup = data.get("meetup")
        body = data.get("body")
        created_by = user.get("id")
        if created_by:
            if isinstance(created_by, str):
                if not created_by.isdigit():
                    return jsonify({
                        "status": 400,
                        "error": "Can only pass digits for user id!"
                    }), 400
            if isinstance(created_by, int):
                created_by = created_by
        if meetup:
            if isinstance(meetup, str):
                if not meetup.isdigit():
                    return jsonify({
                        "status": 400,
                        "error": "Can only pass digits for meetup id!"
                    }), 400
                meetup = int(meetup)
            if isinstance(meetup, int):
                meetup = meetup
        meetup = MEETUP.get_meetup(meetup)
        new_question = QUESTION_MODEL.question(title=title,
                                               body=body,
                                               meetup=meetup,
                                               author=created_by,
                                               votes=0)
        return QUESTION_MODEL.save(new_question)
    except Exception as e:
        return jsonify({
            "status": 400,
            "error": str(e)+" "+str(user)
        }), 400


@v1_questions_blueprint.route('/questions/<int:question_id>', methods=['GET'])
def get_meetup_question(question_id):
    """Get a pecific question"""
    question = question_id
    try:
        if not int(question):
            return jsonify({
                "status": 400,
                "error": "Wrong parameters supplied for the request"
            }), 400

        response = QUESTION_MODEL.get_question(question)
        return jsonify({
            "status": 200,
            "data": response
            }), 200

    except Exception:
        return jsonify({
            "status": 404,
            "error": "The question of the given id is not found"
                }), 404


@v1_questions_blueprint.route('/questions/<int:question_id>/upvote',
                              methods=['PATCH'])
@requires_token
def upvote(user, question_id):
    """Upvote a specific question."""
    try:
        query = QUESTION_MODEL.get_question(question_id)
        updated_votes = QUESTION_MODEL.upvote(user, query)
        if updated_votes is False:
            return jsonify({
                "status": 400,
                "error": "You can only vote once!"
            }), 400
        return jsonify({
            "status": 200,
            "message": "Question upvoted successfully!",
            "question": updated_votes
        }), 200

    except Exception as e:
        return jsonify({
            "status": 404,
            "error": "The question of the given id is not found"+str(e)
                }), 404


@v1_questions_blueprint.route('/questions/<int:question_id>/downvote',
                              methods=['PATCH'])
@requires_token
def downvote(user, question_id):
    """Downvote a specific question."""
    try:
        query = QUESTION_MODEL.get_question(question_id)
        downvoted_votes = QUESTION_MODEL.downvote(user, query)
        if downvoted_votes is False:
            return jsonify({
                "status": 400,
                "error": "You can only vote once!"
            }), 400
        return jsonify({
            "status": 200,
            "message": "Question upvoted successfully!",
            "question": downvoted_votes
        }), 200

    except Exception:
        return jsonify({
            "status": 404,
            "error": "The question of the given id is not found"
                }), 404
