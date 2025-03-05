from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context
import sys
import os

# Adicione o caminho do seu projeto ao sys.path
sys.path.append(os.getcwd())

# Importe seus modelos
from models import Base

# Configuração do Alembic
config = context.config
fileConfig(config.config_file_name)

# Configuração do target_metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Executa migrações no modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

    
def run_migrations_online():
    # Defina a URL de conexão diretamente ou de outra fonte
    url = "sqlite:///./enduro.db"  # Exemplo para SQLite
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    

