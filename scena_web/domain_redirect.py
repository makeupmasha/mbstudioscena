"""Independent installation: no aliases or redirects to another owner."""
from .server import serve

def with_legacy_redirects(application):
    return application
