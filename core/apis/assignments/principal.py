from flask import Blueprint
from core import db 
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from .schema import AssignmentSchema, AssignmentGradeSchema
from core.libs import assertions

# principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


# Principal can retrieve all assignments.
@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments_for_principal(p):
    # assignments = Assignment.query.all()
    assignments = Assignment.get_assignments_by_principal()

    assertions.assert_found(assignments, 'No assignments found for this principal')

    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    print("assignment dump",assignments_dump)
    return APIResponse.respond(data=assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment_for_principal(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    # Fetch the assignment by ID
    assignment = Assignment.query.get(grade_assignment_payload.id)

    # if not assignment:
    #     return APIResponse.respond(
    #         message='Assignment not found.',
    #         error="FyleError",
    #         status_code=404  
    #     )

    # Check if the assignment is in "DRAFT" state
    # if assignment.state == AssignmentStateEnum.DRAFT:
    #     return APIResponse.respond(
    #         message="Assignments in draft state cannot be graded.",
    #         error="DRAFT_STATE",
    #         status_code=400 
    #     )

    assertions.assert_found(assignment, 'No assignments found for this principal')

    assertions.assert_valid(assignment.state != AssignmentStateEnum.DRAFT,
                            'Assignments in draft state cannot be graded')

    # Proceed to grade the assignment if it's not in DRAFT state
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p  # Principal is grading
    )
    
    db.session.commit()
    
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)