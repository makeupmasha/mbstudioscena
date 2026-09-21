"""Local, isolated demo; never loads cloud credentials or the source database."""
from pathlib import Path
import os
import runpy
import secrets

ROOT = Path(__file__).resolve().parents[1]
for key in list(os.environ):
    if key.startswith(('VERCEL', 'SCENA_', 'RESEND_')):
        os.environ.pop(key, None)
port = os.environ.get('PORT', '8877')
data = ROOT / 'data'
data.mkdir(exist_ok=True)
password_file = data / 'demo-password.txt'
if not password_file.exists():
    password_file.write_text(secrets.token_urlsafe(24))
    password_file.chmod(0o600)
os.environ.update(
    SCENA_WEB_TESTING='1', SCENA_NATIVE_WEB='1', SCENA_CLOUD='0',
    SCENA_APP_DIR=str(ROOT), SCENA_DB_PATH=str(data / 'demo.db'),
    SCENA_ADMIN_PASSWORD=password_file.read_text().strip(),
    SCENA_LOCAL_BASE_URL='http://localhost:' + port,
    SCENA_PUBLIC_BASE_URL='http://localhost:' + port,
    SCENA_DEMO_SITE='1', PORT=port,
)
runpy.run_path(str(ROOT / 'deploy/start_web.py'), run_name='__main__')
