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
    
app.config['TRAP_HTTP_EXCEPTIONS']=True

# Global error handler for the application
@app.errorhandler(Exception)  # This catches any exception that inherits from Python's built-in Exception class
def handle_error(err):
    print("inside handle error")
    # Handle custom application-specific errors (FyleError)
    if isinstance(err, FyleError):
        print("inside FyleError")
        return jsonify(
            error=err.__class__.__name__,  
            message=err.message 
        ), err.status_code 

    # Handle validation errors from Marshmallow
    elif isinstance(err, ValidationError):
        print("inside ValidationError")
        return jsonify(
            error=err.__class__.__name__,  
            message=err.messages  
        ), 400

    elif isinstance(err, IntegrityError):
        print("inside IntegrityError")
        return jsonify(
            error=err.__class__.__name__, 
            message=str(err.orig)  
        ), 400

  
    elif isinstance(err, HTTPException):
        print("inside HTTPExceptions")
        return jsonify(
            error=err.__class__.__name__,  
            message=str(err) 
        ), err.code

    # if err.code != 409:  # Skip 409 Conflict
    #     if isinstance(err, HTTPException):
    #         print("inside HTTPException")
    #         return jsonify(
    #             error=err.__class__.__name__,
    #             message=str(err)
    #         ), err.code

    # If the error doesn't match any known cases, raise err is executed, and passed back to Flask’s default error handling mechanism
    raise err

