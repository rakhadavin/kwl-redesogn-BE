import datetime


def isRewardValid(date_string):
    date_format = "%Y-%m-%d"

    date = datetime.strptime(date_string, date_format)

    now = datetime.now()

    if date < now:
        return False
    else:
        return True