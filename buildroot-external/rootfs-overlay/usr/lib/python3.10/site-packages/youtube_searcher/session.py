from requests_cache import CachedSession
from datetime import timedelta

session = CachedSession(backend='memory', expire_after=timedelta(hours=1))


def new_session(new_session):
    global session
    session = new_session
    return session


def reset_session():
    new_session(CachedSession(backend='memory',
                              expire_after=timedelta(hours=1)))

