# User Views v2.
import datetime
import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from app.api.v2.models.users_model import UsersModel
from instance.config import key as enc_key
from app.api.v2.utils.utils import requires_token
from app.api.v2.utils.validator import (valid_email, check_if_exists,
                                        validate_password,
                                        contains_whitespace,
                                        is_string)

V2_USER_BLUEPRINT = Blueprint('v2_user_blueprint',
                              __name__, url_prefix='/api/v2')


@V2_USER_BLUEPRINT.route('/auth/signup', methods=['POST'])
def signup():
    """Signup route"""
    required = [
        "firstname",
        "lastname",
        "password",
        "email",
        "phoneNumber",
        "username"
    ]
    try:
        data = request.get_json()
        for field in required:
            if field not in data.keys():
                return jsonify({
                    "status": 400,
                    "error": "Please provide the following fields. "
                    "`{}`".format(field)
                })
        for key, value in data.items():
            if key in [field for field in required]:
                if contains_whitespace(value):
                    return jsonify({
                        "status": 400,
                        "error": "You cannot have whitepaces in"
                                 " {} field".format(key)
                    })
                if not value.replace(" ", ""):
                    return jsonify({
                        "status": 400,
                        "error": "{} is missing.".format(key)
                    })

        first_name = data.get('firstname')
        last_name = data.get("lastname")
        password = data.get("password")
        other_name = data.get("othername")
        email = data.get("email")
        phone = data.get("phoneNumber")
        username = data.get("username")

        if not valid_email(email):
            return jsonify({
                "status": 400,
                "error": "The email provided is not in the right format"
            }), 400
        if not validate_password(password):
            return jsonify({
                "status": 400,
                "error": "The password doesn't match our standards!"
                         "[(a-z)(A-Z)(0-9)(@#$)]"
            }), 400
        if check_if_exists('users', 'username', username):
            return jsonify({
                'status': 409,
                'error': 'That username already exists!'
            }), 409
        if check_if_exists('users', 'email', email):
            return jsonify({
                "status": 409,
                "error": "That email already exists."
                "Perhaps you want to login?"
            }), 409
        if not is_string(username):
            return jsonify({
                "status": 400,
                "error": "The username must be a string"
            })
        if not is_string(first_name):
            return jsonify({
                "status": 400,
                "error": "The firstname must be a string"
            })
        if not is_string(last_name):
            return jsonify({
                "status": 400,
                "error": "The lastname must be a string"
            })
        new_user = UsersModel(
            fname=first_name,
            lname=last_name,
            password=password,
            other_name=other_name,
            email=email,
            phone_number=phone,
            username=username)
        data = new_user.save()
        return jsonify({
            "status": 201,
            "message": "User `{}` created "
            "successfully!".format(data['username']),
            "data": data
        }), 201

    except Exception as e:
        return jsonify({
            "status": 400,
            "error": str(e)
        }), 400


@V2_USER_BLUEPRINT.route('/auth/login', methods=['POST'])
def login():
    """Log in route."""
    required = ['email', 'password']
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        for field in required:
            if field not in data.keys():
                return jsonify({
                    "status": 400,
                    "error": "Please provide the following fields. "
                    "`{}`".format(field)
                }), 400
        for key, value in data.items():
            if key in [field for field in required]:
                if not value.replace(" ", ""):
                    return jsonify({
                        "status": 400,
                        "error": "{} is missing.".format(key)
                        }), 400

        if valid_email(email):
            if check_if_exists('users', 'email', email):
                cur_user = UsersModel.get_user(email)
                if cur_user and \
                        check_password_hash(
                                cur_user.get('password'), password):
                    data = {
                        "email": email,
                        "sub": email,
                        "iat": datetime.datetime.now(),
                        "exp": datetime.datetime.now()
                               + datetime.timedelta(minutes=5)
                    }
                    token = jwt.encode(data, enc_key, algorithm='HS256')

                    if token:
                        return jsonify({
                            "status": 200,
                            "message": "Logged in successfully!",
                            "token": token.decode('utf-8')
                            }), 200
                    else:
                        return jsonify({
                            "status": 401,
                            "error": "Could not verify token. \
                            Please sign in again!",
                            "token": token.decode('utf-8')
                            }), 401
                return jsonify({
                    "status": 400,
                    "error": "Password is invalid. Please check your"
                    " credentials"
                    }), 400

            else:
                return jsonify({
                    "status": 400,
                    "error": "No user found with the given credentials"
                    }), 400
        else:
            return jsonify({
                "status": 400,
                "error": "Email invalid"
            }), 400

    except Exception as e:
        return jsonify({
            "status": 400,
            "error": str(e)
        }), 400


@V2_USER_BLUEPRINT.route('/auth/logout', methods=['POST'])
def logout():
    """Log out route."""
    token = request.headers.get('x-access-token')
    data = UsersModel.decode_token(token=token)
    if data is False:
        return jsonify({
            "status": 401,
            "error": "You're  not allowed to acces the resource"
        }), 401
    UsersModel.logout(token=token)
    return jsonify({
        "status": 200,
        "message": "Logged out successfully!"
    }), 200


@V2_USER_BLUEPRINT.route('/auth/password/change', methods=['POST'])
@requires_token
def change_password(logged_user):
    """Change password route."""
    try:
        data = request.json
        for key in data.keys():
            if 'new_password' not in key:
                return jsonify({
                    "status": 400,
                    "error": "`{}` field is required".format('new_password')
                })
        new_password = data.get('new_password')
        if not validate_password(new_password):
            return jsonify({
                "status": 400,
                "error": "The password doesn't match our standards! "
                         "[(a-z)(A-Z)(0-9)(@#$)]"
            }), 400
        user = logged_user.get('user_id')
        UsersModel.change_password(user, new_password)
        return jsonify({
            "status": 200,
            "message": "Password updated succesfully"
        }), 200
    except Exception as e:
        return jsonify({
            "status": 400,
            "error": str(e)
        })
