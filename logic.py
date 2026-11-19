def validate_subject(subject: object) -> str | None:
    """Return a user-facing error when the subject is missing."""
    if not isinstance(subject, str) or not subject.strip():
        return "กรุณากรอกชื่อวิชา โดยชื่อวิชาต้องไม่เป็นค่าว่าง"
    return None


def validate_duration(duration: object) -> str | None:
    """Return a user-facing error unless duration is an integer from 1 to 240."""
    if isinstance(duration, bool) or not isinstance(duration, int):
        return "เวลาเรียนต้องเป็นจำนวนเต็มตั้งแต่ 1–240 นาที"
    if not 1 <= duration <= 240:
        return "เวลาเรียนต้องอยู่ระหว่าง 1–240 นาที"
    return None


def classify_duration(duration: int) -> str:
    """Classify a validated duration as Short, Medium, or Long."""
    error = validate_duration(duration)
    if error is not None:
        raise ValueError(error)
    if duration < 30:
        return "Short"
    if duration < 60:
        return "Medium"
    return "Long"
