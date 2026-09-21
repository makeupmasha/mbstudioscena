"""Compatibility shim: source-owner migration is not applicable here."""

def migrate_public_origin(database, environment, *, connector=None):
    return "skipped_independent_installation"
