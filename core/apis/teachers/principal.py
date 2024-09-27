from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.teachers import Teacher
# from core.models.users import User
from .schema import TeacherSchema


principal_teachers_resources = Blueprint('principal_teachers_resources', __name__)

# Principal can retrieve all teahchers.
@principal_teachers_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers_for_principal(p):
    teachers = Teacher.get_teachers()
    teachers_dump = TeacherSchema().dump(teachers, many=True)
    return APIResponse.respond(data=teachers_dump)


