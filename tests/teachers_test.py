from core.models.assignments import AssignmentStateEnum, GradeEnum, Assignment
from core.models.teachers import Teacher
from core.apis.teachers.schema import TeacherSchema
import pytest
from core.models.assignments import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from core.__init__ import app

from werkzeug.exceptions import BadRequest, NotFound
from core.libs.exceptions import FyleError

def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )
    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(


        '/teacher/assignments',
        headers=h_teacher_2
    )
    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )
    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )
    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )
    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_invalid_id(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )
    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": "A"
        }
    )
    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


# additional tests

def test_grade_assignment_missing_grade(client, h_teacher_2):
    """Test for missing fields in the grading payload."""
    # Missing 'grade' field
    response = client.post(
        '/teacher/assignments/grade',
        json={
            'id': 4
        },
        headers=h_teacher_2
    )
    assert response.status_code == 400


def test_grade_assignment_missing_id(client, h_teacher_2):
    # Missing 'id' field
    response = client.post(
        '/teacher/assignments/grade',
        json={
            'grade': 'A'
        },
        headers=h_teacher_2
    )
    assert response.status_code == 400


def test_grade_assignment_invalid_grade_value(client, h_teacher_1):
    """Test for grading an assignment with an invalid grade value."""
    response = client.post(
        '/teacher/assignments/grade',
        json={
            'id': 4,
            'grade': 'InvalidGrade'  
        },
        headers=h_teacher_1
    )
    assert response.status_code == 400


def test_grade_assignment_invalid_id_value(client, h_teacher_2):
    """Test for grading an assignment with an invalid id value."""
    response = client.post(
        '/teacher/assignments/grade',
        json={
            'id': "hello",
            'grade': GradeEnum.B.value  
        },
        headers=h_teacher_2
    )
    assert response.status_code == 400


def test_grade_unauthorized_method(client, h_teacher_2):
    """
    Test unauthorized method(post) to the assignments endpoint.
    """
    response = client.post(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 405  


def test_list_assignments_unauthorized(client):
    """
    Test unauthorized access to the teachers endpoint.
    """
    response = client.get('/teacher/assignments')

    assert response.status_code == 401     


def test_get_assignments(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.DRAFT, AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_invalid_payload(client, h_teacher_1):
    """Test for invalid payloads"""
    response = client.post(
        '/teacher/assignments/grade',
        json={},
        headers=h_teacher_1
    )
    assert response.status_code == 400


def test_grade_assignment_not_submit(client, h_teacher_2):
    """
    failure case: assignment 5 was submitted to none
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 5,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_cross2(client, h_teacher_1):
    """
    failure case: assignment 3 was submitted to teacher 2 and not teacher 1
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 3,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_success(client, h_teacher_2):
    """
    success case: Successfully grade a submitted assignment.
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 4, 
            "grade": "B"
        }
    )

    assert response.status_code == 200
    data = response.json['data']
    
    # Check that the grade is updated in the response
    assert data['id'] == 4
    assert data['grade'] == "B"


# schema test
def test_teacher_schema_load():
    """
    Test deserialization of Teacher data using TeacherSchema.
    This will trigger the @post_load method and test line 20.
    """
    schema = TeacherSchema()
    
    # Create a dictionary simulating the incoming JSON data for a Teacher
    teacher_data = {
        "id": 1,
        "user_id": 3,
        "created_at": "2023-09-25T00:00:00",
        "updated_at": "2023-09-25T00:00:00"
    }
    
    # Load the data into the schema (this triggers @post_load)
    teacher = schema.load(teacher_data)
    
    # Check if the result is a Teacher instance and the data is correctly deserialized
    assert isinstance(teacher, Teacher)
    assert teacher.id == 1 


#################### server tests ####################

def test_base_route(client):
    response = client.get('/')

    assert response.status_code == 200

    response_json = response.json
    assert 'status' in response_json
    assert 'time' in response_json


#################### model reprs ####################

def test_teacher_repr():
    teacher = Teacher(id=1)
    repr_student = repr(teacher)
    assert repr_student == '<Teacher 1>'


def test_assignment_repr():
    assignment = Assignment(id=1)
    repr_student = repr(assignment)
    assert repr_student == '<Assignment 1>'


@pytest.fixture(scope='function')
def db_session():
    """
    Fixture to create a new database session for a test and rollback afterward.
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Use the connection for the test's session
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    # Overwrite the global session object with our new session
    db.session = session

    yield session

    # Rollback the session after the test runs to maintain a clean state
    transaction.rollback()
    # connection.close()
    session.remove()


def test_assignment_class_method(db_session):
    assignment_new = Assignment(
        id=5, 
        student_id=1,
        teacher_id=1, 
        content="Test assignment content", 
        state=AssignmentStateEnum.DRAFT
    )

    Assignment.upsert(assignment_new)
    inserted_assignment = Assignment.query.filter_by(content="Test assignment content").first()

    assert inserted_assignment is not None 
    assert inserted_assignment.state == AssignmentStateEnum.DRAFT 
    assert inserted_assignment.student_id == 1  


def test_http_exception_bad_request(client, h_teacher_1):
    # with app.test_client() as client:
       
        response = client.get('/teacher/abort',
            headers=h_teacher_1)

        assert response.status_code == 403


# def test_http_exception_bad_request(client, h_teacher_1):
#     # with app.test_client() as client:
       
#         response = client.get('/teacher/raise-error',
#             headers=h_teacher_1)

#         assert response.status_code == 500
        





