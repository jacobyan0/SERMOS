import cx_Oracle
from flask import g, current_app


def connect_db():
    username = 'xyan'
    password = 'yanxiang053991'
    address = 'oracle.cise.ufl.edu/orcl'
    con = cx_Oracle.connect(username, password, address, encoding="utf-8")
    return con


def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


def close_db():
    if hasattr(g, 'db'):
        g.db.close()
