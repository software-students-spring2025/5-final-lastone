from utils import get_current_user_id, login_required
from flask import Flask, session, request
import pytest
from bson.objectid import ObjectId

def test_get_current_user_id_no_session(app):
    """Test with no session data"""
    with app.test_request_context():
        assert get_current_user_id() is None

def test_get_current_user_id_valid_session(app):
    """Test with valid session"""
    test_id = '507f1f77bcf86cd799439011'
    with app.test_request_context():
        session['user_id'] = test_id
        assert str(get_current_user_id()) == test_id

def test_get_current_user_id_invalid_session(app):
    """Test with invalid session ID"""
    with app.test_request_context():
        session['user_id'] = 'invalid_id'
        assert get_current_user_id() is None
        assert 'user_id' not in session  # Should be cleared

def test_login_required_decorator(app):
    """Test the login_required decorator"""
    @app.route('/protected')
    @login_required
    def protected():
        return "Protected Content"

    # Test unauthorized access
    with app.test_client() as client:
        response = client.get('/protected', follow_redirects=True)
        assert b'login' in response.data.lower()

    # Test authorized access
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = '507f1f77bcf86cd799439011'
        response = client.get('/protected')
        assert b'Protected Content' in response.data