import sqlite3, os
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:
        db_name = os.getenv('DB_NAME','data.db')
        g.db = sqlite3.connect(
            db_name, detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row can't be serialized 
        # g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        content = f.read().decode('utf8')
        db.executescript(content)

@click.command("init-db")
@click.argument('fake_arg',default=[])
# @click.argument
@with_appcontext
def init_db_command(fake_arg):
    """Clear the existing data and create new tables."""
    init_db()
    # click.echo("Initialized the database.")

def init_app(app):
    app.teardown_appcontext(close_db)
    # app.cli.add_command(init_db_command)