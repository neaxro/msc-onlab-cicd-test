from datetime import datetime

date_format = "%Y.%m.%d. %H:%M:%S"

def utcnow() -> str:
    date = datetime.utcnow()
    return datetime.strftime(date, date_format)
