#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
#!/usr/bin/env python
import os
import sys

# --- ADICIONE ESTE BLOCO DE "VACINA" AQUI ---
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# 1. Ignora o aviso de versão antiga
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# 2. Desativa o comando 'RETURNING' que está quebrando o seu banco
@property
def can_return_columns_from_insert(self):
    return False

DatabaseFeatures.can_return_columns_from_insert = can_return_columns_from_insert
# --------------------------------------------

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_clinica.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_clinica.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
