import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


DATA_FILE = Path(__file__).with_name("study_records.json")
_REQUIRED_FIELDS = {"subject", "duration", "category", "timestamp"}
_CATEGORIES = {"Short", "Medium", "Long"}


class DataStoreError(Exception):
    """Raised when study records cannot be read or safely written."""


def _validate_records(records: object) -> list[dict[str, object]]:
    if not isinstance(records, list):
        raise DataStoreError("รูปแบบไฟล์ต้องเป็น JSON List")

    for index, record in enumerate(records):
        if not isinstance(record, dict) or not _REQUIRED_FIELDS.issubset(record):
            raise DataStoreError(f"ข้อมูลรายการที่ {index + 1} ไม่ครบหรือไม่ถูกต้อง")
        if (
            not isinstance(record["subject"], str)
            or isinstance(record["duration"], bool)
            or not isinstance(record["duration"], int)
            or not isinstance(record["category"], str)
            or record["category"] not in _CATEGORIES
            or not isinstance(record["timestamp"], str)
        ):
            raise DataStoreError(f"ข้อมูลรายการที่ {index + 1} ไม่ถูกต้อง")

    return records


def read_records() -> list[dict[str, object]]:
    """Read all records, creating an empty JSON list when the file is absent."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except FileNotFoundError:
        try:
            with DATA_FILE.open("x", encoding="utf-8") as file:
                json.dump([], file)
        except FileExistsError:
            return read_records()
        except OSError as error:
            raise DataStoreError(f"สร้างไฟล์ประวัติไม่ได้ ({error})") from error
        return []
    except json.JSONDecodeError as error:
        raise DataStoreError(
            f"ไฟล์ JSON เสียหาย กรุณาตรวจสอบ {DATA_FILE.name}"
        ) from error
    except OSError as error:
        raise DataStoreError(f"อ่านไฟล์ประวัติไม่ได้ ({error})") from error

    return _validate_records(records)


def add_record(
    subject: str,
    duration: int,
    category: str,
) -> list[dict[str, object]]:
    """Append a record while preserving existing records, then return all records."""
    records = read_records()
    records.append(
        {
            "subject": subject,
            "duration": duration,
            "category": category,
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    )

    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = file.name
            json.dump(records, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(temporary_path, DATA_FILE)
    except OSError as error:
        if temporary_path is not None and os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise DataStoreError(f"บันทึกไฟล์ประวัติไม่ได้ ({error})") from error

    return records
