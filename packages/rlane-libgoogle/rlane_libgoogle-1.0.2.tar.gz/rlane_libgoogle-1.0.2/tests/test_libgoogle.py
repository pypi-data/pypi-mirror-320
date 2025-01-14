import sys

from loguru import logger
from rich.pretty import pprint

from libgoogle import connect, set_debug, use_cache

logger.remove()
logger.add(sys.stderr, level="TRACE")


def test_gcal_uncached() -> None:
    print()
    s1 = connect("calendar.readonly", "v3")
    s2 = connect("https://www.googleapis.com/auth/calendar.readonly", "v3")
    s3 = connect("calendar.readonly", "v3")
    assert s1 != s2
    assert s2 != s3


def test_gcal_cached() -> None:
    print()
    use_cache(True)
    s1 = connect("https://www.googleapis.com/auth/calendar.readonly", "v3")
    s2 = connect("calendar.readonly", "v3")
    s3 = connect("https://www.googleapis.com/auth/calendar.readonly", "v3")
    use_cache(False)
    assert s1 == s2
    assert s2 == s3

    calendars = s3.calendarList().list().execute()
    for item in calendars["items"]:
        pprint(item)
        break


def test_gdrive_uncached() -> None:
    print()
    s1 = connect("drive", "v3")
    s2 = connect("https://www.googleapis.com/auth/drive", "v3")
    s3 = connect("drive", "v3")
    assert s1 != s2
    assert s2 != s3


def test_gdrive_cached() -> None:
    print()
    use_cache(True)
    s1 = connect("https://www.googleapis.com/auth/drive", "v3")
    s2 = connect("drive", "v3")
    s3 = connect("https://www.googleapis.com/auth/drive", "v3")
    use_cache(False)
    assert s1 == s2
    assert s2 == s3

    about = s3.about().get(fields="user").execute()
    pprint(about)


def test_gmail_uncached() -> None:
    print()
    s1 = connect("gmail.readonly", "v1")
    s2 = connect("https://www.googleapis.com/auth/gmail.readonly", "v1")
    s3 = connect("gmail.readonly", "v1")
    assert s1 != s2
    assert s2 != s3


def test_gmail_cached() -> None:
    print()
    use_cache(True)
    s1 = connect("https://www.googleapis.com/auth/gmail.readonly", "v1")
    s2 = connect("gmail.readonly", "v1")
    s3 = connect("https://www.googleapis.com/auth/gmail.readonly", "v1")
    use_cache(False)
    assert s1 == s2
    assert s2 == s3

    labels = s3.users().labels().list(userId="me").execute()
    for item in labels["labels"]:
        pprint(item)
        break


def test_debug() -> None:
    print()
    set_debug(True)

    gcal = connect("calendar.readonly", "v3")
    calendars = gcal.calendarList().list().execute()
    for item in calendars["items"]:
        pprint(item)
        break

    gdrive = connect("drive", "v3")
    about = gdrive.about().get(fields="user").execute()
    pprint(about)

    gmail = connect("gmail.readonly", "v1")
    labels = gmail.users().labels().list(userId="me").execute()
    for item in labels["labels"]:
        pprint(item)
        break

    set_debug(False)
