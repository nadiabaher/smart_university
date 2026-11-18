import config


def evaluate_access(distance_cm, rfid_valid=None, fingerprint_valid=None,
                    face_recognized=None):
    """
    The single place that decides whether the classroom door opens.

    - Nobody near the door   -> no decision yet (access_granted = None)
    - Someone near the door  -> granted if ANY credential is valid
    """
    person_near = distance_cm is not None and distance_cm <= config.PERSON_NEAR_CM

    if not person_near:
        access_granted = None
    else:
        access_granted = any(
            value is True for value in (rfid_valid, fingerprint_valid, face_recognized)
        )

    return {
        "person_near": person_near,
        "access_granted": access_granted,
        "door_state": "open" if access_granted else "closed",
    }
