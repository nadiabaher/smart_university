"""Turn raw state data into clean dictionaries for the dashboard."""


def adapt_parking_data(data):
    data = data or {}
    try:
        available = int(data.get("available_spaces", 0))
        occupied = int(data.get("occupied_spaces", 0))
    except (ValueError, TypeError):
        available = occupied = 0

    spaces = [
        {
            "space_id": space.get("space_id", "Unknown"),
            "status": str(space.get("status", "unknown")).lower(),
        }
        for space in data.get("spaces", [])
        if isinstance(space, dict)
    ]

    return {
        "available_spaces": available,
        "occupied_spaces": occupied,
        "total_spaces": available + occupied,
        "parked_cars_count": data.get("parked_cars_count", occupied),
        "pressure_occupied_count": data.get("pressure_occupied_count", occupied),
        "spaces": spaces,
    }


def adapt_attendance_data(data):
    data = data or {}
    recognized = bool(data.get("recognized", False))
    # Unknown students are never recorded as present
    recorded = bool(data.get("attendance_recorded", False)) and recognized

    if recorded:
        status = "Present"
    elif recognized:
        status = "Recognized but not recorded"
    else:
        status = "Unknown student"

    return {
        "student_id": data.get("student_id") if recognized else None,
        "student_name": data.get("student_name") if recognized else None,
        "recognized": recognized,
        "attendance_recorded": recorded,
        "timestamp": data.get("timestamp"),
        "session_id": data.get("session_id"),
        "status": status,
    }


def adapt_classroom_data(data):
    data = data or {}
    access_granted = data.get("access_granted")

    if access_granted is True:
        access_status = "Access Granted"
    elif access_granted is False:
        access_status = "Access Denied"
    else:
        access_status = "Waiting for verification"

    return {
        "distance_cm": data.get("distance_cm"),
        "person_near": data.get("person_near", False),
        "rfid_valid": data.get("rfid_valid"),
        "fingerprint_valid": data.get("fingerprint_valid"),
        "face_recognized": data.get("face_recognized"),
        "access_granted": access_granted,
        "access_status": access_status,
        "door_state": data.get("door_state", "unknown"),
    }
