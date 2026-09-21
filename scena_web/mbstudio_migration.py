"""Compatibility shim: source-owner migration is not applicable here."""

def migrate(database, environment, *, connector=None):
    return "skipped_independent_installation"
