from __future__ import with_statement
#  used to set up logging so that Alembic can log important migration details.
import logging
from logging.config import fileConfig
# Accesses the running Flask app.
from flask import current_app
# used to run migrations (either in online or offline mode).
from alembic import context

# this is the Alembic Config object
config = context.config

# Sets up logging alembic.ini file so that Alembic logs events (like migration success/failure).
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Instead of hardcoding the database URL in alembic.ini, it dynamically pulls it from your Flask app's configuration, ensuring you're always migrating the correct database.
config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.get_engine().url).replace(
        '%', '%%'))
target_metadata = current_app.extensions['migrate'].db.metadata


# This function handles offline migrations, where there’s no direct database connection.
def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Fetches the database URL from the configuration.
    url = config.get_main_option("sqlalchemy.url")
    # Sets up the migration context in "offline" mode. It uses literal SQL statements instead of interacting with the database directly.
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

# This function where a direct connection to the database is available.
def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # it logs the message: "No changes in schema detected." and prevents empty migration scripts from being created.
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    # This line connects to the database.
    connectable = current_app.extensions['migrate'].db.get_engine()

    #  Establishes a database connection for migration.
    with connectable.connect() as connection:
        # Configures Alembic with the database connection and model metadata.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        # Begins a database transaction and Runs the migration
        with context.begin_transaction():
            context.run_migrations()

# Depending on the mode, it runs the appropriate migration function.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
