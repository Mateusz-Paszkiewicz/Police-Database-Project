from flask import redirect, render_template, session
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def authorisation_2_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("authorisation") < 2:
            return render_template("index.html", wrong=1)
        return f(*args, **kwargs)
    return decorated_function

def authorisation_3_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("authorisation") < 3:
            return render_template("index.html", wrong=1)
        return f(*args, **kwargs)
    return decorated_function