from functools import wraps
from flask import request, jsonify
from functools import partial
from project.api.models import User


def is_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.admin


def authenticate(f, do_jsonify=True):
    if do_jsonify:
        def conversion_func(x):
            return jsonify(x)
    else:
        def conversion_func(x):
            return x

    @wraps(f)
    def decorated_function(*args, **kwargs):
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return conversion_func(response_object), 403
        auth_token = auth_header.split(" ")[1]
        user_id = User.decode_auth_token(auth_token)
        if isinstance(user_id, str):
            response_object['message'] = user_id
            return conversion_func(response_object), 401
        user = User.query.filter_by(id=user_id).first()
        if not user or not user.active:
            return conversion_func(response_object), 401
        return f(user_id, *args, **kwargs)

    return decorated_function


# in users.py we use flask-restful,
# it seems like make_response will happen in dispatch_request,
# so we just need to return dict as response data
authenticate_restful = partial(authenticate, do_jsonify=False)
