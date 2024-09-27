from flask import Blueprint
from core import db 
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from .schema import AssignmentSchema, AssignmentGradeSchema


# principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


# Principal can retrieve all assignments.
@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments_for_principal(p):
    # assignments = Assignment.query.all()
    assignments = Assignment.get_assignments_by_teacher()
    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    return APIResponse.respond(data=assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment_for_principal(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    
    # Mark the assignment as graded
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p  # Principal is grading
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)