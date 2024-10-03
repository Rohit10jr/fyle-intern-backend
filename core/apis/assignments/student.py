from flask import Blueprint, jsonify, make_response
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum

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

    # Check if content is empty
    if not assignment.content:
        return APIResponse.respond(
            message="Content cannot be empty.",
            error="EMPTY_CONTENT",
            status_code=400  
        )

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

    # Fetch the assignment by ID
    assignment = Assignment.query.get(submit_assignment_payload.id)

    # Check if the assignment is in DRAFT state
    # if assignment.state != AssignmentStateEnum.DRAFT:
    # if assignment.state == AssignmentStateEnum.SUBMITTED or assignment.state == AssignmentStateEnum.GRADED:
    if assignment.state in {AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED}:

        return APIResponse.respond(
            message='only a draft assignment can be submitted',
            error="FyleError",  
            status_code=400  # Set the status code to 400
        )

    # assignment.state = AssignmentStateEnum.SUBMITTED
    # assignment.teacher_id = submit_assignment_payload.teacher_id

    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id,
        auth_principal=p,
        
    )

    # Commit the changes to the database
    db.session.commit()

    # Serialize to JSON format and return.
    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(data=submitted_assignment_dump)

    # return make_response(jsonify({
    #             'assignment id': submitted_assignment.id,
    #             'pteacherid': p.teacher_id,
    #             'teacher_id': submitted_assignment.teacher_id,
    #             'A': "aaa"
    #         }), 200)



