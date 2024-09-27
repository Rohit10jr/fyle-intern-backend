from flask import jsonify
from marshmallow.exceptions import ValidationError
from core import app
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources
from core.apis.assignments.principal import principal_assignments_resources
from core.apis.teachers.principal import principal_teachers_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException

from sqlalchemy.exc import IntegrityError

# Registering blueprints to handle student and teacher-related APIs
app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')

app.register_blueprint(principal_assignments_resources, url_prefix='/principal')
app.register_blueprint(principal_teachers_resources, url_prefix='/principal')

# the root URL.
@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

    return response


# Global error handler for the application
@app.errorhandler(Exception)  # This catches any exception that inherits from Python's built-in Exception class
def handle_error(err):
    # Handle custom application-specific errors (FyleError)
    if isinstance(err, FyleError):
        # Return a JSON response with the error class name, custom message, and HTTP status code
        return jsonify(
            error=err.__class__.__name__,  # (e.g., "FyleError")
            message=err.message  # Custom error message and status code stored in FyleError
        ), err.status_code 

    # Handle validation errors from Marshmallow
    elif isinstance(err, ValidationError):
        # Return a JSON response with validation error details and a 400 Bad Request status code
        return jsonify(
            error=err.__class__.__name__,  # ("ValidationError")
            message=err.messages  
        ), 400

    # Handle database integrity errors from SQLAlchemy
    elif isinstance(err, IntegrityError):
        return jsonify(
            error=err.__class__.__name__,  # ("IntegrityError")
            message=str(err.orig)  # Original database error message
        ), 400

    # Handle other HTTP-related exceptions (e.g., 404, 403)
    elif isinstance(err, HTTPException):
        return jsonify(
            error=err.__class__.__name__,  # (e.g., "NotFound", "Forbidden")
            message=str(err)  # Description of the HTTP error
        ), err.code

    # If the error doesn't match any known cases, raise err is executed, and passed back to Flask’s default error handling mechanism
    raise err


# err.__class__.__name__ is not a constructor; it simply gets the name of the exception class for better readability in the response.

# The isinstance() function checks whether the object err is an instance of the class FyleError. If it is, this block of code will execute.