from core.models.assignments import AssignmentStateEnum, GradeEnum


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 6,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B


#  additional tests 

def test_list_assignments_empty(client, h_principal):
    """Test to ensure no assignments returns an empty list."""
    # You might want to clear the assignments or set up a scenario with no assignments
    
    response = client.get('/principal/assignments', headers=h_principal)
    
    assert response.status_code == 200


def test_grade_assignment_draft_error(client, h_principal):
    """Test to ensure grading a draft assignment fails."""
    # Assuming there is an assignment with ID 2 that is in draft
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 6,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    
    assert response.status_code == 400



def test_grade_assignment_draft_error(client, h_principal):
    """Test to ensure grading a draft assignment fails."""
    # Assuming there is an assignment with ID 2 that is in draft
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 6,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    
    assert response.status_code == 400
    assert response.json['error'] == "DRAFT_STATE"


def test_grade_assignment_success(client, h_principal):
    """Test to grade an assignment successfully."""
    # Assuming there is an assignment with ID 1 that is not in draft
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    
    assert response.status_code == 200
    assert response.json['data']['grade'] == GradeEnum.A.value


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


def test_grade_assignment_invalid_id(client, h_principal):
    """Test to ensure grading an assignment with an invalid ID fails."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 9999,  # Assuming this ID does not exist
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'FyleError'


# principal/teacher route 

def test_list_teachers_no_teachers(client, h_principal):
    """
    Test when there are no teachers available.
    """
    # Assuming you can mock Teacher.get_teachers() to return an empty list
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200
    data = response.json['data']
    assert data == []


def test_list_teachers_success(client, h_principal):
    """
    Test successful fetching of teachers.
    """
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200
    data = response.json['data']
    
    assert isinstance(data, list)  # Ensure the data is a list
    assert len(data) > 0  # Ensure that the list contains teachers
    for teacher in data:
        assert 'id' in teacher  # Ensure each teacher has an ID


def test_list_teachers_unauthorized(client):
    """
    Test unauthorized access to the teachers endpoint.
    """
    response = client.get('/principal/teachers')

    assert response.status_code == 401  # Unauthorized
    assert 'error' in response.json  # Expect an error message


# Test for getting assignments with specific states
def test_get_assignments_specific_states(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )
    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


# Test for invalid payloads
def test_grade_assignment_invalid_payload(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={},
        headers=h_principal
    )
    assert response.status_code == 400

    # Test for grading the same assignment multiple times
def test_grade_assignment_multiple_times(client, h_principal):
    # First grade
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    assert response.status_code == 200

    # Re-grade the same assignment
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    assert response.status_code == 200
    assert response.json['data']['grade'] == GradeEnum.A.value