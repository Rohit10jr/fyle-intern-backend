from flask import Blueprint, jsonify, make_response
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.models.assignments import AssignmentStateEnum
from .schema import AssignmentSchema, AssignmentGradeSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


# Teachers can retrieve all assignment
@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    # Fetches all assignments accessed by teacher.
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)

    # Serializes the list of Assignment and returns.
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


# Teachers can grade a specific assignment by submitting the assignment ID and grade.
@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    # Deserializes the incoming JSON
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    assignment = Assignment.query.get(grade_assignment_payload.id)

    if not assignment:
        return APIResponse.respond(
            message='Assignment not found.',
            error="FyleError",
            status_code=404  
        )

    # if assignment.state != AssignmentStateEnum.SUBMITTED:
    if assignment.state == AssignmentStateEnum.DRAFT:
        return APIResponse.respond(
            message='Only a Submitted assignment can be given Grade.',
            error="FyleError", 
            status_code=400   
        )
    
    if assignment.teacher_id != p.teacher_id:
        return APIResponse.respond(
            message='You are not authorized to grade this assignment.',
            error="FyleError",
            status_code=400
        )

        # return make_response(jsonify({
        #     'assignment id': assignment.id,
        #     'pteacherid': p.teacher_id,
        #     'teacher_id': assignment.teacher_id,
        #     'message': 'You are not authorized to grade this assignment.',
        #     'error': 'FyleError'
        # }), 400)

    # Grades the assignment from provided grade and commits
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()

    #  Serializes the graded_assignment back to json
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
