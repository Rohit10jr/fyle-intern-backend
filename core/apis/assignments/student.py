from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentSubmitSchema

# Blueprint is a Flask feature that allows modularization of routes. here, it groups routes related to student assignments under student_assignments_resources
student_assignments_resources = Blueprint('student_assignments_resources', __name__)

# allows students to list all their assignments.
@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    # fetch authenticated students assignments using id
    students_assignments = Assignment.get_assignments_by_student(p.student_id)

    # Serializes the list of Assignment
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    
    # Returns the serialized data as an API response.
    return APIResponse.respond(data=students_assignments_dump)


# allows a student to create a new assignment or edit an existing one.
@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    # Deserializes the incoming payload.
    assignment = AssignmentSchema().load(incoming_payload)

    # Ensures assignment belongs to the authenticated student, inserts or updates assignment
    assignment.student_id = p.student_id
    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()

    # Serializes back into JSON format and returns.
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)


# This endpoint allows a student to submit an assignment to a teacher.
@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    # Deserializes the payload
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)

    # Assignment submitted, which involves changing its state to "submitted" and assigning it to a teacher, finally committed to the database
    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id,
        auth_principal=p
    )
    db.session.commit()

    # Serializes to JSON format and returns.
    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(data=submitted_assignment_dump)
