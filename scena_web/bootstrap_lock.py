"""Serialize first boot across replicas, including migrations that commit DDL.

A database lease is needed because a threading lock only protects one process.
The lease expires after a crashed container and is renewed during a slow boot.
"""
from contextlib import contextmanager
import logging
import secrets
import threading
import time

from scena_database import connect


@contextmanager
def database_boot_lock(database, *, timeout=240, lease_seconds=600, poll=1):
    owner = secrets.token_hex(24)
    deadline = time.monotonic() + timeout

    def statement(sql, parameters=(), *, read=False):
        db = connect(database)
        try:
            with db:
                cursor = db.execute(sql, parameters)
                return cursor.fetchone() if read else cursor.rowcount
        finally:
            db.close()

    statement('''CREATE TABLE IF NOT EXISTS scena_boot_lock (
        name TEXT PRIMARY KEY, owner TEXT NOT NULL, expires INTEGER NOT NULL)''')
    while True:
        statement('''INSERT INTO scena_boot_lock(name,owner,expires)
            VALUES ('native',?,CAST(strftime('%s','now') AS INTEGER)+?)
            ON CONFLICT(name) DO UPDATE SET owner=excluded.owner,expires=excluded.expires
            WHERE scena_boot_lock.expires <= CAST(strftime('%s','now') AS INTEGER)''',
            (owner, lease_seconds))
        row = statement("SELECT owner FROM scena_boot_lock WHERE name='native'", read=True)
        if row and row[0] == owner:
            break
        if time.monotonic() >= deadline:
            raise TimeoutError('Another replica is still initializing the database.')
        time.sleep(min(poll, max(0, deadline - time.monotonic())))

    stop = threading.Event()
    lost = threading.Event()

    def renew():
        while not stop.wait(min(30, lease_seconds / 3)):
            try:
                changed = statement('''UPDATE scena_boot_lock
                    SET expires=CAST(strftime('%s','now') AS INTEGER)+?
                    WHERE name='native' AND owner=?''', (lease_seconds, owner))
                if changed != 1:
                    lost.set()
                    return
            except Exception:
                lost.set()
                logging.exception('SCENA startup lease renewal failed')
                return

    heartbeat = threading.Thread(target=renew, name='scena-boot-lease', daemon=True)
    heartbeat.start()
    try:
        yield
        if lost.is_set():
            raise RuntimeError('Database startup lease was lost; restart initialization.')
    finally:
        stop.set()
        heartbeat.join(timeout=10)
        try:
            statement("DELETE FROM scena_boot_lock WHERE name='native' AND owner=?", (owner,))
        except Exception:
            # A failed cleanup cannot replace a migration error. The lease expires.
            logging.exception('SCENA startup lease cleanup failed')
