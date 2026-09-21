"""Installation boundaries: identity, tenant links and portable owner uploads."""
import hashlib
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

os.environ['SCENA_CLOUD'] = '0'
os.environ['SCENA_PUBLIC_BASE_URL'] = 'https://studio.example'

from scena_core import init_db, get_settings, save_settings
from scena_business_card import get_card, save_card, render_card, vcard
from scena_transfer import build_backup, restore_backup
from scena_service_email import sender_from_public_base

ROOT = Path(__file__).resolve().parents[1]


class IndependentInstallationTests(unittest.TestCase):
    def test_new_owners_have_distinct_identity_and_no_customer_records(self):
        with tempfile.TemporaryDirectory() as folder:
            identities = []
            for name in ('first', 'second'):
                db_path = Path(folder) / (name + '.db')
                init_db(db_path)
                with sqlite3.connect(db_path) as db:
                    identities.append(dict(db.execute("SELECT key,value FROM app_meta WHERE key IN ('owner_id','installation_id')")))
                    for table in ('requests', 'shop_orders'):
                        self.assertEqual(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0], 0)
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM posts').fetchone()[0], 2)
                self.assertEqual(get_settings(db_path)['master_name'], 'София Леру')
                save_settings(db_path, {'master_name': 'Имя нового владельца'})
                init_db(db_path)
                self.assertEqual(get_settings(db_path)['master_name'], 'Имя нового владельца')
                with sqlite3.connect(db_path) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM posts').fetchone()[0], 2)
            for key in ('owner_id', 'installation_id'):
                self.assertNotEqual(identities[0][key], identities[1][key])

    def test_card_uses_new_origin_and_has_no_previous_owner_links(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / 'new.db'
            init_db(db)
            card = get_card(db)
            rendered = render_card(card) + vcard(card).decode()
            self.assertIn('https://studio.example/card/', rendered)
            self.assertIn('/card/qr.svg', rendered)
            for forbidden in ('mbstudio.scena.life', 'masha_cravcenco', 'Бараночникова'):
                self.assertNotIn(forbidden, rendered)
            self.assertEqual(card['instagram_url'], '')
            self.assertEqual(card['phone'], '')
            self.assertEqual(card['email'], '')

    def test_uploaded_photo_and_owner_edits_survive_restart_and_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            app = Path(folder) / 'app'
            shutil.copytree(ROOT / 'media', app / 'media')
            db = app / 'new.db'
            init_db(db)
            image = (ROOT / 'media/demo/studio.png').read_bytes()
            saved = save_card(db, app, {'first_name': 'Новый владелец'},
                              expected=get_card(db), upload=image)
            self.assertTrue(saved['photo'].startswith('media/business-card/'))
            init_db(db)
            self.assertEqual(get_card(db), saved)
            restored = restore_backup(build_backup(db, app / 'media'), Path(folder) / 'restored')
            self.assertEqual(get_card(restored['db_path']), saved)
            restored_file = Path(restored['db_path']).parent / saved['photo']
            self.assertEqual(hashlib.sha256(restored_file.read_bytes()).hexdigest(), hashlib.sha256(image).hexdigest())

    def test_email_requires_this_installations_sender_configuration(self):
        with patch.dict(os.environ, {'SCENA_EMAIL_FROM': ''}):
            self.assertEqual(sender_from_public_base('https://studio.example'), '')
        with patch.dict(os.environ, {'SCENA_EMAIL_FROM': 'studio@example.com'}):
            self.assertEqual(sender_from_public_base('https://studio.example'), 'studio@example.com')
        with patch.dict(os.environ, {'SCENA_EMAIL_FROM': 'bad\r\nBcc: other@example.com'}):
            self.assertEqual(sender_from_public_base('https://studio.example'), '')


if __name__ == '__main__':
    unittest.main()
