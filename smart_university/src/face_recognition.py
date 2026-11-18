"""
PLACEHOLDER for the attendance teammate (laptop camera + OpenCV).

Paste the face recognition code here. When a face is recognized, report it with:

    from src.message_handler import MessageHandler
    MessageHandler().handle_message({
        "module": "attendance",
        "message_type": "attendance_update",
        "data": {
            "student_id": "2024001",
            "student_name": "Ahmed",
            "recognized": True,
            "attendance_recorded": True,
            "timestamp": "2026-11-18 10:30:00",
            "session_id": "LAB_01",
        },
    })

For an unknown face send recognized=False, attendance_recorded=False.
See docs/PROTOCOL.md.
"""
