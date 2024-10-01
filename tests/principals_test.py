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
            'id': 5,
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



# #  additional tests 

def test_get_assignments_unauthorized_access(client):
    """Test for unauthorized access when no principal token is provided."""
    response = client.get('/principal/assignments')

    # assert 'Unauthorized' in response.json['message']
    assert response.status_code == 401


def test_grade_assignment_invalid_grade_value(client, h_principal):
    """Test for grading an assignment with an invalid grade value."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': 'InvalidGrade'  
        },
        headers=h_principal
    )
    assert response.status_code == 400


def test_grade_assignment_invalid_id_value(client, h_principal):
    """Test for grading an assignment with an invalid grade value."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': "hello",
            'grade': GradeEnum.B.value  
        },
        headers=h_principal
    )
    assert response.status_code == 400


def test_grade_assignment_invalid_id(client, h_principal):
    """Test to ensure grading an assignment with an invalid ID fails."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 6,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    
    assert response.status_code == 404


def test_grade_assignment_invalid_id_2(client, h_principal):
    """Test to ensure grading an assignment with an invalid ID fails."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 9999, 
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'FyleError'



def test_get_assignments_specific_states(client, h_principal):
    """Test to ensure it fetches assignment with GRADED or SUBMITTED."""
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )
    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_invalid_payload(client, h_principal):
    """Test for invalid payloads"""
    response = client.post(
        '/principal/assignments/grade',
        json={},
        headers=h_principal
    )
    assert response.status_code == 400


def test_grade_assignment_multiple_times(client, h_principal):
    """Test for grading the same assignment multiple times"""
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


def test_grade_assignment_missing_fields(client, h_principal):
    """Test for missing fields in the grading payload."""
    # Missing 'grade' field
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4
        },
        headers=h_principal
    )
    assert response.status_code == 400

    # Missing 'id' field
    response = client.post(
        '/principal/assignments/grade',
        json={
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    assert response.status_code == 400


# # principal/teacher route 
def test_list_teachers_no_teachers(client, h_principal):
    """
    Test when there are no teachers available.
    """
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200
    data = response.json['data']


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
    
    assert len(data) > 0  
    for teacher in data:
        assert 'id' in teacher  


def test_list_teachers_unauthorized(client):
    """
    Test unauthorized access to the teachers endpoint.
    """
    response = client.get('/principal/teachers')

    assert response.status_code == 401  
    assert 'error' in response.json  

