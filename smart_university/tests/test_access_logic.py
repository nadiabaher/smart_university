from src.access_logic import evaluate_access


def test_valid_rfid_near_door_grants_access():
    result = evaluate_access(20, rfid_valid=True)
    assert result == {"person_near": True, "access_granted": True, "door_state": "open"}


def test_each_credential_works_alone():
    assert evaluate_access(20, fingerprint_valid=True)["access_granted"] is True
    assert evaluate_access(20, face_recognized=True)["access_granted"] is True


def test_invalid_credentials_denied():
    result = evaluate_access(20, False, False, False)
    assert result["access_granted"] is False
    assert result["door_state"] == "closed"


def test_far_away_means_no_decision_even_with_valid_card():
    result = evaluate_access(120, rfid_valid=True)
    assert result["person_near"] is False
    assert result["access_granted"] is None
    assert result["door_state"] == "closed"


def test_distance_boundary_is_50_cm():
    assert evaluate_access(50, rfid_valid=True)["access_granted"] is True
    assert evaluate_access(51, rfid_valid=True)["access_granted"] is None


def test_no_reading():
    assert evaluate_access(None)["person_near"] is False
