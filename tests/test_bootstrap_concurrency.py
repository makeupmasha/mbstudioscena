"""A fresh shared database must survive concurrent container startup."""
import multiprocessing
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

from scena_web.bootstrap_lock import database_boot_lock


def boot_replica(database, start, results):
    os.environ.update(SCENA_DB_PATH=database, SCENA_CLOUD='0', VERCEL='0',
                      SCENA_ADMIN_PASSWORD='test-only-password',
                      SCENA_PUBLIC_BASE_URL='https://studio.example')
    import scena_core
    from scena_web import bootstrap
    original = scena_core._create_services_table

    def delayed_create(*args, **kwargs):
        # Expose the check-then-create race seen on the first Turso deployment.
        time.sleep(.2)
        return original(*args, **kwargs)

    scena_core._create_services_table = delayed_create
    start.wait(10)
    try:
        bootstrap.initialize()
        with sqlite3.connect(database) as db:
            identity = dict(db.execute("SELECT key,value FROM app_meta WHERE key IN ('owner_id','cloud_session_key')"))
        results.put(('ok', identity))
    except Exception as exc:
        results.put(('error', repr(exc)))


class BootstrapConcurrencyTests(unittest.TestCase):
    def test_four_replicas_share_one_complete_installation(self):
        with tempfile.TemporaryDirectory() as folder:
            database = str(Path(folder) / 'fresh.db')
            context = multiprocessing.get_context('spawn')
            start, results = context.Event(), context.Queue()
            processes = [context.Process(target=boot_replica, args=(database, start, results)) for _ in range(4)]
            try:
                for process in processes:
                    process.start()
                start.set()
                outcomes = [results.get(timeout=30) for _ in processes]
                for process in processes:
                    process.join(10)
                self.assertTrue(all(status == 'ok' for status, _ in outcomes), outcomes)
                self.assertTrue(all(identity == outcomes[0][1] for _, identity in outcomes), outcomes)
                self.assertTrue(outcomes[0][1]['owner_id'])
                with sqlite3.connect(database) as db:
                    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM scena_boot_lock').fetchone()[0], 0)
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM requests').fetchone()[0], 0)
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM posts').fetchone()[0], 2)
            finally:
                for process in processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()

    def test_failure_releases_lease_and_crashed_lease_expires(self):
        with tempfile.TemporaryDirectory() as folder:
            database = str(Path(folder) / 'lock.db')
            with self.assertRaisesRegex(ValueError, 'migration failed'):
                with database_boot_lock(database):
                    raise ValueError('migration failed')
            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM scena_boot_lock').fetchone()[0], 0)
                db.execute("INSERT INTO scena_boot_lock VALUES ('native','crashed',0)")
            with database_boot_lock(database, timeout=.1, poll=.01):
                pass

    def test_active_owner_is_not_displaced(self):
        with tempfile.TemporaryDirectory() as folder:
            database = str(Path(folder) / 'lock.db')
            with database_boot_lock(database):
                with self.assertRaises(TimeoutError):
                    with database_boot_lock(database, timeout=.05, poll=.01):
                        self.fail('Concurrent initialization must not enter.')


if __name__ == '__main__':
    unittest.main()
