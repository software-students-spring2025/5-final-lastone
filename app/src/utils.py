from flask import session, redirect, url_for
from bson.objectid import ObjectId
from functools import wraps

def get_current_user_id():
    """Retrieves the current user's ObjectId from the session."""
    user_id_str = session.get('user_id')
    if user_id_str:
        try:
            return ObjectId(user_id_str)
        except:
            session.pop('user_id', None)
            return None
    return None

def login_required(view):
    """Decorator that redirects to the login page if the user is not logged in."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if get_current_user_id() is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

