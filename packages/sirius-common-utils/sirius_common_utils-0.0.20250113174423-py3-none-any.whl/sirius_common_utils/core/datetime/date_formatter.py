from datetime import datetime

PATTERN_DATETIME = "%d-%m-%Y %H:%M:%S"
PATTERN_DATETIME_TREND = "%Y-%m-%d %H:%M:%S"

PATTERN_DATE = "%d-%m-%Y"
PATTERN_TIME = "%H:%M:%S"

def convert_date_to_text(datetime:datetime, pattern=PATTERN_DATETIME, throws_ex_flag=False):
    return datetime.strftime(pattern)

def convert_text_to_date(text, pattern=PATTERN_DATETIME, throws_ex_flag=False):
    try:
        date_obj = datetime.strptime(text, pattern)
        return date_obj.date()
    except Exception as ex:
        if throws_ex_flag:
            raise ex
        else:
            return None


def convert_text_to_datetime(text, pattern=PATTERN_DATETIME, throws_ex_flag=False):
    try:
        date_obj = datetime.strptime(text, pattern)
        return date_obj
    except Exception as ex:
        if throws_ex_flag:
            raise ex
        else:
            return None
